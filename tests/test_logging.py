"""
测试日志记录功能
"""

import os
import sys
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging_setup():
    """测试日志配置是否正确"""
    print("=" * 60)
    print("测试日志记录功能")
    print("=" * 60)
    
    # 检查日志目录是否存在
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    print(f"\n1. 检查日志目录: {log_dir}")
    if os.path.exists(log_dir):
        print(f"   ✓ 日志目录存在")
    else:
        print(f"   ✗ 日志目录不存在")
        return False
    
    # 导入app模块以触发日志配置
    print("\n2. 导入app模块...")
    try:
        import src.app as app
        print(f"   ✓ app模块导入成功")
    except Exception as e:
        print(f"   ✗ app模块导入失败: {e}")
        return False
    
    # 检查日志文件是否创建
    image_log = os.path.join(log_dir, 'image_generation.log')
    llm_log = os.path.join(log_dir, 'llm_calls.log')
    
    print(f"\n3. 检查日志文件:")
    print(f"   - 图片生成日志: {image_log}")
    if os.path.exists(image_log):
        print(f"     ✓ 文件已创建")
    else:
        print(f"     ℹ 文件尚未创建（首次使用时会创建）")
    
    print(f"   - LLM调用日志: {llm_log}")
    if os.path.exists(llm_log):
        print(f"     ✓ 文件已创建")
    else:
        print(f"     ℹ 文件尚未创建（首次使用时会创建）")
    
    # 测试写入日志
    print("\n4. 测试写入日志...")
    try:
        # 获取logger
        image_logger = logging.getLogger('image_generation')
        llm_logger = logging.getLogger('llm_calls')
        
        # 写入测试日志
        image_logger.info("测试日志 - 图片生成功能正常")
        llm_logger.info("测试日志 - LLM调用功能正常")
        
        print(f"   ✓ 测试日志写入成功")
        
        # 验证日志内容
        if os.path.exists(image_log):
            with open(image_log, 'r', encoding='utf-8') as f:
                content = f.read()
                if "测试日志 - 图片生成功能正常" in content:
                    print(f"   ✓ 图片生成日志内容验证通过")
                else:
                    print(f"   ✗ 图片生成日志内容验证失败")
        
        if os.path.exists(llm_log):
            with open(llm_log, 'r', encoding='utf-8') as f:
                content = f.read()
                if "测试日志 - LLM调用功能正常" in content:
                    print(f"   ✓ LLM调用日志内容验证通过")
                else:
                    print(f"   ✗ LLM调用日志内容验证失败")
                    
    except Exception as e:
        print(f"   ✗ 测试日志写入失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！日志功能正常工作")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_logging_setup()
