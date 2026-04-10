"""
DrawThings WebUI - Python Flask 后端服务
提供与 DrawThings 服务交互的 API 接口
"""

import os
import json
import time
import base64
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

# 导入数据库模块
from database import (
    add_history_record,
    update_history_record,
    delete_history_record,
    cleanup_incomplete_records,
    migrate_from_json,
    get_history_count,
    get_or_create_user,
    get_user_history
)

# 导入历史记录路由模块
from history_routes import register_history_routes

# 导入 AI 润色模块
from ai_refine import refine_prompt_with_llm, load_config as load_ai_config, save_config as save_ai_config

# 创建 Flask 应用实例
app = Flask(__name__, static_folder='static', static_url_path='')
# 启用跨域支持
CORS(app)

# 全局并发计数器（线程安全）
import threading
generating_count = 0
count_lock = threading.Lock()

# 启动定期清理任务
def start_cleanup_scheduler(interval_hours=24):
    """启动定期清理不完整记录的后台任务
    
    Args:
        interval_hours (int): 清理间隔（小时），默认24小时
    """
    import time
    
    def cleanup_task():
        while True:
            time.sleep(interval_hours * 3600)  # 转换为秒
            try:
                print(f"\n[定时清理] 开始检查不完整记录...")
                result = cleanup_incomplete_records(IMAGES_DIR)
                if result['cleaned_count'] > 0:
                    print(f"[定时清理] ✅ 已清理 {result['cleaned_count']} 条不完整记录")
                else:
                    print(f"[定时清理] ✅ 没有发现不完整的记录")
            except Exception as e:
                print(f"[定时清理] ⚠️  清理出错: {e}")
    
    # 启动守护线程
    thread = threading.Thread(target=cleanup_task, daemon=True)
    thread.start()
    print(f"已启动定期清理任务（每{interval_hours}小时执行一次）")

# 存储生成图片的目录
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_images')
# 创建日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 配置图片生成日志
image_logger = logging.getLogger('image_generation')
image_logger.setLevel(logging.INFO)
image_handler = logging.FileHandler(os.path.join(LOG_DIR, 'image_generation.log'), encoding='utf-8')
image_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
image_logger.addHandler(image_handler)

# 配置LLM调用日志
llm_logger = logging.getLogger('llm_calls')
llm_logger.setLevel(logging.INFO)
llm_handler = logging.FileHandler(os.path.join(LOG_DIR, 'llm_calls.log'), encoding='utf-8')
llm_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
llm_logger.addHandler(llm_handler)

os.makedirs(IMAGES_DIR, exist_ok=True)

# 存储耗时统计数据的文件
TIMING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timing_stats.json')

# 存储 DrawThings 配置的文件
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# DrawThings 服务默认地址
DEFAULT_DRAWTHINGS_URL = "http://127.0.0.1:7888"


def get_user_id():
    """从请求头中获取或创建用户 ID
    
    Returns:
        int: 用户 ID
    """
    user_id_header = request.headers.get("X-User-ID")
    
    if user_id_header:
        try:
            return int(user_id_header)
        except (ValueError, TypeError):
            pass
    
    # 如果没有提供用户 ID，自动创建或获取一个
    return get_or_create_user()


def load_timing_stats():
    """加载耗时统计数据
    
    从 timing_stats.json 文件中读取历史生成耗时记录。
    
    Returns:
        dict: 包含 times 列表和 average_time 的字典，如果文件不存在或读取失败则返回默认值
    """
    if os.path.exists(TIMING_FILE):
        try:
            with open(TIMING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"times": [], "average_time": 0}
    return {"times": [], "average_time": 0}


def save_timing_stats(stats):
    """保存耗时统计数据
    
    将耗时统计信息写入 timing_stats.json 文件。
    
    Args:
        stats (dict): 包含 times 列表和 average_time 的统计字典
    """
    try:
        with open(TIMING_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"保存耗时统计出错: {e}")


def calculate_average_time(times):
    """计算平均耗时
    
    根据耗时列表计算平均值。
    
    Args:
        times (list): 耗时列表（秒）
    
    Returns:
        float: 平均耗时，如果列表为空则返回 0
    """
    if not times:
        return 0
    return sum(times) / len(times)


def estimate_generation_time(width, height, steps, user_id=None):
    """预估图片生成时间
    
    根据历史记录中的平均耗时、图片尺寸和步数来预估生成时间。
    基准：512x512 @ 8 steps 作为参考点。
    
    Args:
        width (int): 图片宽度
        height (int): 图片高度
        steps (int): 生成步数
        user_id (int, optional): 用户 ID，用于获取该用户的历史记录
    
    Returns:
        dict: 包含 estimated_time（预估总时间秒）和 base_time（基准时间）
    """
    # 获取该用户的历史记录
    history = []
    if user_id:
        try:
            history = get_user_history(user_id, limit=10)
        except Exception as e:
            print(f"Error getting user history for estimation: {e}")
    
    # 基准参数
    base_width = 512
    base_height = 512
    base_steps = 8
    
    # 计算基准时间（从历史记录中获取平均耗时）
    if history:
        # 使用最近 10 条记录的平均值
        recent_times = [h.get('elapsed_time', 0) for h in history[:10] if h.get('elapsed_time', 0) > 0]
        if recent_times:
            base_time = sum(recent_times) / len(recent_times)
        else:
            base_time = 30  # 默认 30 秒
    else:
        base_time = 30  # 没有历史记录时使用默认值
    
    # 计算像素比例
    current_pixels = width * height
    base_pixels = base_width * base_height
    pixel_ratio = current_pixels / base_pixels
    
    # 计算步数比例
    step_ratio = steps / base_steps
    
    # 预估时间 = 基准时间 * 像素比例 * 步数比例
    # 添加一些缓冲时间（10%）
    estimated_time = base_time * pixel_ratio * step_ratio * 1.1
    
    return {
        "estimated_time": round(estimated_time, 2),
        "base_time": round(base_time, 2),
        "pixel_ratio": round(pixel_ratio, 2),
        "step_ratio": round(step_ratio, 2)
    }


def load_config():
    """加载 DrawThings 服务配置
    
    从 config.json 文件中读取 DrawThings 服务地址配置。
    
    Returns:
        str: DrawThings 服务 URL，如果配置不存在则返回默认地址
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("drawthings_url", DEFAULT_DRAWTHINGS_URL)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_DRAWTHINGS_URL
    return DEFAULT_DRAWTHINGS_URL


def save_config(drawthings_url):
    """保存 DrawThings 服务配置
    
    将 DrawThings 服务地址写入 config.json 文件。
    
    Args:
        drawthings_url (str): DrawThings 服务地址
    
    Returns:
        bool: 保存成功返回 True，失败返回 False
    """
    try:
        # 确保 URL 包含协议前缀
        if not drawthings_url.startswith(('http://', 'https://')):
            drawthings_url = 'http://' + drawthings_url
        
        config = {"drawthings_url": drawthings_url}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"保存配置出错: {e}")
        return False


# 存储生成历史的文件（已弃用，改用 SQLite）
# HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generation_history.json')


# ===== 数据迁移脚本（已弃用）=====
# 不再支持从 JSON 迁移数据
def auto_migrate_if_needed():
    """自动迁移 JSON 数据到数据库（已弃用）"""
    pass

# 启动时执行迁移（跳过）
# auto_migrate_if_needed()



@app.route('/')
def index():
    """提供主页 HTML 文件
    
    Returns:
        Response: 静态 HTML 页面
    """
    return send_from_directory('static', 'index.html')


@app.route('/api/status', methods=['GET'])
def check_status():
    """检查 DrawThings 服务器状态
    
    连接到配置的 DrawThings 服务地址，获取当前提示词和模型信息。
    
    Returns:
        Response: JSON 响应，包含 success、prompt、model 字段
    """
    drawthings_url = load_config()
    try:
        response = requests.get(drawthings_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "success": True,
                "prompt": data.get("prompt", ""),
                "model": data.get("model", ""),
                "raw_data": data
            })
        else:
            return jsonify({
                "success": False,
                "error": f"服务器返回状态码: {response.status_code}"
            }), 500
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": f"无法连接到 DrawThings 服务器: {drawthings_url}"
        }), 500
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "连接 DrawThings 服务器超时"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/estimate_time', methods=['POST'])
def estimate_time():
    """预估图片生成时间
    
    根据图片尺寸、步数和用户历史记录预估生成时间。
    
    Returns:
        Response: JSON 响应，包含 estimated_time（秒）
    """
    try:
        params = request.json
        width = params.get("width", 512)
        height = params.get("height", 512)
        steps = params.get("steps", 8)
        
        # 获取用户 ID
        user_id = get_user_id()
        
        # 计算预估时间
        estimation = estimate_generation_time(width, height, steps, user_id)
        
        return jsonify({
            "success": True,
            "estimated_time": estimation["estimated_time"],
            "base_time": estimation["base_time"],
            "pixel_ratio": estimation["pixel_ratio"],
            "step_ratio": estimation["step_ratio"]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/generate', methods=['POST'])
def generate_image():
    """生成图片
    
    接收前端参数，转发到 DrawThings 服务的 txt2img 接口进行图片生成。
    生成完成后保存图片、更新耗时统计、记录历史。
    
    Returns:
        Response: JSON 响应，包含图片 URL、耗时、seed 等信息
    """
    drawthings_url = load_config()
    start_time = time.time()
    
    # 检查当前正在生成的任务数量
    global generating_count
    with count_lock:
        current_count = generating_count
        if current_count >= 5:
            return jsonify({
                "success": False,
                "error": f"当前已有 {current_count} 个任务正在生成中，请稍后再试（最多允许5个并发任务）"
            }), 429
        # 增加并发计数
        generating_count += 1
    
    # 初始化 user_id 和 seed 变量，避免在异常处理中未定义
    user_id = None
    seed = -1

    try:
        # 获取请求参数
        params = request.json
        
        # 获取用户 ID（可选，如果没有则不保存历史记录）
        user_id = get_user_id()
        
        # 计算预估时间
        width = params.get("width", 512)
        height = params.get("height", 512)
        steps = params.get("steps", 8)
        estimation = estimate_generation_time(width, height, steps, user_id)

        # 记录图片生成开始
        image_logger.info(f"开始生成图片 - 用户ID: {user_id}, 尺寸: {width}x{height}, 步数: {steps}, Seed: {params.get('seed', -1)}")
        
        # 生成唯一ID用于NSFW检测和历史记录（在转发请求前）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 先创建初始历史记录（is_nsfw默认为0，后续NSFW检测会更新它）
        if user_id:
            initial_record = {
                "user_id": user_id,
                "id": timestamp,
                "image_url": f"/generated_images/generated_{timestamp}.png",
                "image_filename": f"generated_{timestamp}.png",
                "prompt": params.get("prompt", ""),
                "negative_prompt": params.get("negative_prompt", ""),
                "width": width,
                "height": height,
                "steps": steps,
                "seed": params.get("seed", -1),
                "elapsed_time": 0,
                "rating": 0,
                "created_at": datetime.now().isoformat()
            }
            add_history_record(initial_record)
            image_logger.info(f"已创建初始历史记录 - image_id: {timestamp}")
        
        # 异步进行NSFW检测（如果配置了LLM）- 在转发请求前执行
        try:
            from llm_client import async_detect_nsfw
            prompt = params.get("prompt", "")
            negative_prompt = params.get("negative_prompt", "")
            async_detect_nsfw(prompt, negative_prompt, timestamp)
        except Exception as e:
            print(f"启动NSFW检测失败: {e}")
        
        # 转发请求到 DrawThings 服务
        drawthings_response = requests.post(
            f"{drawthings_url}/sdapi/v1/txt2img",
            json=params,
            timeout=600  # 10 分钟超时，因为生成可能需要较长时间
        )

        if drawthings_response.status_code != 200:
            raise Exception(f"DrawThings API 返回状态码: {drawthings_response.status_code}")

        # 解析响应
        result = drawthings_response.json()

        # 提取 base64 图片数据
        if "images" in result and len(result["images"]) > 0:
            image_base64 = result["images"][0]
        elif "data" in result:
            image_base64 = result["data"]
        else:
            raise Exception("响应中没有图片数据")

        # 使用之前生成的timestamp创建文件名并保存图片
        image_filename = f"generated_{timestamp}.png"
        image_path = os.path.join(IMAGES_DIR, image_filename)

        # 解码并保存图片
        image_data = base64.b64decode(image_base64)
        with open(image_path, 'wb') as f:
            f.write(image_data)

        # 获取 seed 值 - 通过请求 DrawThings 状态接口获取
        seed = -1
        try:
            # 请求 DrawThings 服务状态接口获取实际的 seed
            status_response = requests.get(drawthings_url, timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                if "seed" in status_data:
                    seed = status_data["seed"]
        except Exception as e:
            print(f"从状态接口获取 seed 时出错: {e}")
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 记录图片生成成功
        image_logger.info(f"图片生成成功 - 文件名: {image_filename}, 耗时: {elapsed_time:.2f}秒, Seed: {seed}")

        # 更新耗时统计
        stats = load_timing_stats()
        stats["times"].append(elapsed_time)
        # 只保留最近 100 条记录，防止文件过大
        if len(stats["times"]) > 100:
            stats["times"] = stats["times"][-100:]
        stats["average_time"] = calculate_average_time(stats["times"])
        save_timing_stats(stats)

        # 更新历史记录中的实际数据（耗时、seed等）
        if user_id:
            updates = {
                'elapsed_time': round(elapsed_time, 2),
                'seed': seed
            }
            success = update_history_record(timestamp, updates)
            if success:
                image_logger.info(f"已更新历史记录 - image_id: {timestamp}, 耗时: {elapsed_time:.2f}秒, Seed: {seed}")
            else:
                image_logger.warning(f"更新历史记录失败 - image_id: {timestamp}")

        # 返回图片路径和元数据
        return jsonify({
            "success": True,
            "image_url": f"/generated_images/{image_filename}",
            "image_filename": image_filename,
            "elapsed_time": round(elapsed_time, 2),
            "average_time": round(stats["average_time"], 2),
            "seed": seed,
            "estimated_time": estimation["estimated_time"]
        })

    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        image_logger.error(f"图片生成超时 - 耗时: {elapsed_time:.2f}秒, 用户ID: {user_id}")
        # 清理失败的记录
        if user_id and timestamp:
            delete_history_record(timestamp)
            image_logger.info(f"已清理失败记录 - image_id: {timestamp}")
        return jsonify({
            "success": False,
            "error": "图片生成超时（超过 10 分钟）",
            "elapsed_time": round(elapsed_time, 2)
        }), 500
    except requests.exceptions.ConnectionError:
        elapsed_time = time.time() - start_time
        image_logger.error(f"无法连接到DrawThings服务器 - 耗时: {elapsed_time:.2f}秒, 用户ID: {user_id}")
        # 清理失败的记录
        if user_id and timestamp:
            delete_history_record(timestamp)
            image_logger.info(f"已清理失败记录 - image_id: {timestamp}")
        return jsonify({
            "success": False,
            "error": "无法连接到 DrawThings 服务器",
            "elapsed_time": round(elapsed_time, 2)
        }), 500
    except Exception as e:
        elapsed_time = time.time() - start_time
        image_logger.error(f"图片生成失败 - 错误: {str(e)}, 耗时: {elapsed_time:.2f}秒, 用户ID: {user_id}")
        # 清理失败的记录
        if user_id and timestamp:
            delete_history_record(timestamp)
            image_logger.info(f"已清理失败记录 - image_id: {timestamp}")
        return jsonify({
            "success": False,
            "error": str(e),
            "elapsed_time": round(elapsed_time, 2)
        }), 500
    finally:
        # 减少并发计数
        with count_lock:
            generating_count -= 1


@app.route('/generated_images/<filename>')
def serve_generated_image(filename):
    """提供生成的图片文件
    
    Args:
        filename (str): 图片文件名
    
    Returns:
        Response: 图片文件
    """
    return send_from_directory(IMAGES_DIR, filename)


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前 DrawThings 服务配置
    
    Returns:
        Response: JSON 响应，包含当前的 drawthings_url
    """
    drawthings_url = load_config()
    return jsonify({
        "success": True,
        "drawthings_url": drawthings_url
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新 DrawThings 服务配置
    
    接收前端提交的新服务地址并保存到配置文件。
    
    Returns:
        Response: JSON 响应，包含操作结果
    """
    try:
        data = request.json
        drawthings_url = data.get("drawthings_url", DEFAULT_DRAWTHINGS_URL)
        
        # 保存配置
        if save_config(drawthings_url):
            return jsonify({
                "success": True,
                "message": "配置保存成功",
                "drawthings_url": drawthings_url
            })
        else:
            return jsonify({
                "success": False,
                "error": "保存配置失败"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



@app.route('/api/status/generating', methods=['GET'])
def get_generating_status():
    """获取当前正在生成的请求数量
    
    Returns:
        Response: JSON 响应，包含正在生成的数量
    """
    with count_lock:
        count = generating_count
    return jsonify({
        "success": True,
        "generating_count": count
    })


@app.route('/api/refine_prompt', methods=['POST'])
def refine_prompt():
    """AI 润色提示词
    
    接收用户输入的提示词，调用大模型 API 进行优化。
    
    Returns:
        Response: JSON 响应，包含润色后的提示词
    """
    try:
        data = request.json
        original_prompt = data.get("prompt", "")
        language = data.get("language", "zh")
        
        if not original_prompt:
            return jsonify({
                "success": False,
                "error": "提示词不能为空"
            }), 400
            
        refined_prompt = refine_prompt_with_llm(original_prompt, language)
        
        return jsonify({
            "success": True,
            "refined_prompt": refined_prompt
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"润色失败: {str(e)}"
        }), 500


@app.route('/api/refine_config', methods=['GET'])
def get_refine_config():
    """获取 AI 润色配置
    
    Returns:
        Response: JSON 响应，包含当前的 API 配置（不返回 key）
    """
    config = load_ai_config()
    # 为了安全，不返回完整的 api_key
    safe_config = {
        "llm_api_url": config.get("llm_api_url"),
        "llm_model": config.get("llm_model"),
        "has_key": bool(config.get("llm_api_key") or os.getenv("LLM_API_KEY"))
    }
    return jsonify({
        "success": True,
        "config": safe_config
    })


@app.route('/api/refine_config', methods=['POST'])
def update_refine_config():
    """更新 AI 润色配置
    
    Returns:
        Response: JSON 响应，包含操作结果
    """
    try:
        data = request.json
        current_config = load_ai_config()
        
        # 更新 LLM 相关配置，保留其他配置（如 drawthings_url）
        new_config = current_config.copy()
        if "llm_api_url" in data:
            new_config["llm_api_url"] = data["llm_api_url"]
        if "llm_model" in data:
            new_config["llm_model"] = data["llm_model"]
        if "llm_api_key" in data:
            new_config["llm_api_key"] = data["llm_api_key"]
        
        if save_ai_config(new_config):
            return jsonify({
                "success": True,
                "message": "配置保存成功"
            })
        else:
            return jsonify({
                "success": False,
                "error": "保存配置失败"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# 注册历史记录相关路由
register_history_routes(app)

# 启动时清理不完整的历史记录
print("检查并清理不完整的历史记录...")
try:
    result = cleanup_incomplete_records(IMAGES_DIR)
    if result['cleaned_count'] > 0:
        print(f"✅ 已清理 {result['cleaned_count']} 条不完整记录")
    else:
        print("✅ 没有发现不完整的记录")
except Exception as e:
    print(f"⚠️  清理不完整记录时出错: {e}")


if __name__ == '__main__':
    print("启动 DrawThings WebUI 服务器...")
    print(f"静态文件目录: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')}")
    print(f"生成图片保存目录: {IMAGES_DIR}")
    
    # 启动定期清理任务
    start_cleanup_scheduler(interval_hours=24)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
