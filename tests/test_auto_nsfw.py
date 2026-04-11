"""
测试NSFW自动标记功能
"""

import sys
import os
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.llm_client import detect_nsfw_content, async_detect_nsfw
from src.database import update_nsfw_status, get_user_history
import time


def test_nsfw_detection():
    """测试NSFW检测功能"""
    print("=" * 60)
    print("测试1: NSFW内容检测")
    print("=" * 60)
    
    # 测试明显的NSFW提示词
    nsfw_prompts = [
        "nude woman, explicit content",
        "violent scene with blood",
        "adult content, sexual"
    ]
    
    safe_prompts = [
        "beautiful landscape with mountains",
        "cute cat sitting on a windowsill",
        "professional business portrait"
    ]
    
    print("\n测试NSFW提示词:")
    for prompt in nsfw_prompts:
        result = detect_nsfw_content(prompt)
        status = "⚠️ 检测到NSFW" if result else "✅ 未检测到"
        print(f"  {status}: {prompt[:50]}...")
    
    print("\n测试安全提示词:")
    for prompt in safe_prompts:
        result = detect_nsfw_content(prompt)
        status = "⚠️ 检测到NSFW" if result else "✅ 未检测到"
        print(f"  {status}: {prompt[:50]}...")


def test_async_detection():
    """测试异步NSFW检测"""
    print("\n" + "=" * 60)
    print("测试2: 异步NSFW检测")
    print("=" * 60)
    
    prompt = "test prompt for async detection"
    print(f"\n启动异步检测: {prompt}")
    
    thread = async_detect_nsfw(prompt, "", "test_image_001")
    print("异步检测已启动，等待结果...")
    
    # 等待线程完成
    thread.join(timeout=10)
    print("异步检测完成")


def test_database_update():
    """测试数据库NSFW状态更新"""
    print("\n" + "=" * 60)
    print("测试3: 数据库NSFW状态更新")
    print("=" * 60)
    
    # 注意：这个测试需要一个实际存在的image_id
    # 这里只是演示函数调用
    test_image_id = "test_timestamp_" + str(int(time.time()))
    
    print(f"\n尝试更新图片 {test_image_id} 的NSFW状态")
    
    # 先设置为NSFW
    success = update_nsfw_status(test_image_id, True)
    print(f"设置为NSFW: {'成功' if success else '失败（图片不存在）'}")
    
    # 再取消NSFW
    success = update_nsfw_status(test_image_id, False)
    print(f"取消NSFW: {'成功' if success else '失败（图片不存在）'}")


def test_llm_config():
    """测试LLM配置加载"""
    print("\n" + "=" * 60)
    print("测试4: LLM配置加载")
    print("=" * 60)
    
    from src.llm_client import load_llm_config
    
    config = load_llm_config()
    if config:
        print(f"\n✓ LLM配置加载成功:")
        print(f"  API URL: {config.get('api_url', 'N/A')}")
        print(f"  Model: {config.get('model', 'N/A')}")
        print(f"  API Key: {'已配置' if config.get('api_key') else '未配置'}")
    else:
        print("\n✗ LLM配置加载失败")


if __name__ == '__main__':
    print("\n开始测试NSFW自动标记功能...\n")
    
    try:
        test_llm_config()
        test_nsfw_detection()
        test_async_detection()
        test_database_update()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
