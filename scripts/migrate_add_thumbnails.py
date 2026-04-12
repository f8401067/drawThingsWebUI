"""
数据库迁移脚本 - 为已有图片生成缩略图
"""

import os
import sys
import json
from PIL import Image

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.database import get_all_history, update_history_record
except ModuleNotFoundError:
    from database import get_all_history, update_history_record

# 目录配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'generated_images')
THUMBNAILS_DIR = os.path.join(BASE_DIR, 'data', 'thumbnails')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# 确保缩略图目录存在
os.makedirs(THUMBNAILS_DIR, exist_ok=True)


def load_thumbnail_config():
    """加载缩略图配置"""
    default_config = {
        "max_size": [300, 300],
        "quality": 85,
        "format": "JPEG"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("thumbnail", default_config)
        except (json.JSONDecodeError, IOError):
            return default_config
    return default_config


def generate_thumbnail(image_path, thumbnail_path, size=None):
    """生成图片缩略图
    
    Args:
        image_path (str): 原图路径
        thumbnail_path (str): 缩略图保存路径
        size (tuple, optional): 缩略图最大尺寸 (width, height)，如果为 None 则从配置读取
    
    Returns:
        bool: 生成成功返回 True，失败返回 False
    """
    try:
        # 检查原图是否存在
        if not os.path.exists(image_path):
            print(f"原图不存在: {image_path}")
            return False
        
        # 加载缩略图配置
        thumb_config = load_thumbnail_config()
        
        # 如果没有指定尺寸，使用配置中的尺寸
        if size is None:
            size = tuple(thumb_config.get("max_size", [300, 300]))
        
        # 获取其他配置参数
        quality = thumb_config.get("quality", 85)
        img_format = thumb_config.get("format", "JPEG")
        
        # 打开图片
        with Image.open(image_path) as img:
            # 转换为 RGB 模式（处理 PNG 透明通道等）
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # 生成缩略图（保持宽高比）
            img.thumbnail(size, Image.LANCZOS)
            
            # 根据配置的格式保存缩略图
            save_kwargs = {'optimize': True}
            if img_format.upper() == 'JPEG':
                save_kwargs['quality'] = quality
                img.save(thumbnail_path, 'JPEG', **save_kwargs)
            elif img_format.upper() == 'PNG':
                img.save(thumbnail_path, 'PNG', **save_kwargs)
            elif img_format.upper() == 'WEBP':
                save_kwargs['quality'] = quality
                img.save(thumbnail_path, 'WEBP', **save_kwargs)
            else:
                # 默认使用 JPEG
                save_kwargs['quality'] = quality
                img.save(thumbnail_path, 'JPEG', **save_kwargs)
            
        return True
    except Exception as e:
        print(f"生成缩略图失败 [{image_path}]: {e}")
        return False


def migrate_add_thumbnails(force_regenerate=False):
    """为所有已有图片生成缩略图并更新数据库
    
    Args:
        force_regenerate (bool): 是否强制重新生成（删除旧缩略图）
    """
    print("=" * 60)
    if force_regenerate:
        print("开始为已有图片重新生成缩略图（强制模式）...")
    else:
        print("开始为已有图片生成缩略图...")
    print("=" * 60)
    
    # 获取所有历史记录
    history = get_all_history(limit=10000)
    total = len(history)
    print(f"找到 {total} 条历史记录\n")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, record in enumerate(history, 1):
        image_id = record.get('image_id')
        image_filename = record.get('image_filename')
        thumbnail_filename = record.get('thumbnail_filename')
        
        # 如果已经有缩略图且不强制重新生成，跳过
        if not force_regenerate and thumbnail_filename and os.path.exists(os.path.join(THUMBNAILS_DIR, thumbnail_filename)):
            skip_count += 1
            print(f"[{i}/{total}] 跳过 (已有缩略图): {image_filename}")
            continue
        
        # 如果强制重新生成且存在旧缩略图，先删除
        if force_regenerate and thumbnail_filename:
            old_thumb_path = os.path.join(THUMBNAILS_DIR, thumbnail_filename)
            if os.path.exists(old_thumb_path):
                try:
                    os.remove(old_thumb_path)
                    print(f"[{i}/{total}] 删除旧缩略图: {thumbnail_filename}")
                except Exception as e:
                    print(f"[{i}/{total}] 删除旧缩略图失败: {e}")
        
        # 构建路径
        image_path = os.path.join(IMAGES_DIR, image_filename)
        timestamp = image_id  # image_id 就是时间戳
        
        # 生成缩略图文件名
        thumb_filename = f"thumb_{timestamp}.jpg"
        thumb_path = os.path.join(THUMBNAILS_DIR, thumb_filename)
        
        # 生成缩略图
        print(f"[{i}/{total}] 生成缩略图: {image_filename}", end=" -> ")
        if generate_thumbnail(image_path, thumb_path):
            # 更新数据库记录
            updates = {
                'thumbnail_url': f'/thumbnails/{thumb_filename}',
                'thumbnail_filename': thumb_filename
            }
            if update_history_record(image_id, updates):
                success_count += 1
                print("✅ 成功")
            else:
                fail_count += 1
                print("❌ 数据库更新失败")
        else:
            fail_count += 1
            print("❌ 生成失败")
    
    print("\n" + "=" * 60)
    print(f"迁移完成!")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ⏭️  跳过: {skip_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📊 总计: {total}")
    print("=" * 60)


if __name__ == '__main__':
    import sys
    # 检查是否有 --force 参数
    force = '--force' in sys.argv or '-f' in sys.argv
    migrate_add_thumbnails(force_regenerate=force)
