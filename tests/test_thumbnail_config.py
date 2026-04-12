"""
测试缩略图配置功能
"""

import os
import sys
import json
from PIL import Image

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.app import load_thumbnail_config, generate_thumbnail
except ModuleNotFoundError:
    from app import load_thumbnail_config, generate_thumbnail

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'generated_images')
THUMBNAILS_DIR = os.path.join(BASE_DIR, 'data', 'thumbnails')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')


def test_default_config():
    """测试默认配置"""
    print("=" * 60)
    print("测试 1: 加载默认配置")
    print("=" * 60)
    
    config = load_thumbnail_config()
    print(f"✅ 配置加载成功:")
    print(f"   max_size: {config.get('max_size')}")
    print(f"   quality: {config.get('quality')}")
    print(f"   format: {config.get('format')}")
    print()
    
    return config


def test_custom_config():
    """测试自定义配置"""
    print("=" * 60)
    print("测试 2: 使用自定义配置生成缩略图")
    print("=" * 60)
    
    # 读取当前配置
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        original_config = json.load(f)
    
    try:
        # 保存原始 thumbnail 配置
        original_thumb = original_config.get('thumbnail', {})
        
        # 设置更高质量的配置
        test_config = {
            "max_size": [400, 400],
            "quality": 95,
            "format": "JPEG"
        }
        
        original_config['thumbnail'] = test_config
        
        # 写入临时配置
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(original_config, f, ensure_ascii=False, indent=2)
        
        print(f"已更新配置为:")
        print(f"   max_size: {test_config['max_size']}")
        print(f"   quality: {test_config['quality']}")
        print(f"   format: {test_config['format']}")
        print()
        
        # 重新加载配置
        config = load_thumbnail_config()
        print(f"✅ 配置加载验证:")
        print(f"   max_size: {config.get('max_size')}")
        print(f"   quality: {config.get('quality')}")
        print(f"   format: {config.get('format')}")
        print()
        
        # 找到一张测试图片
        if os.path.exists(IMAGES_DIR):
            test_images = [f for f in os.listdir(IMAGES_DIR) if f.endswith('.png')]
            if test_images:
                test_image = test_images[0]
                image_path = os.path.join(IMAGES_DIR, test_image)
                thumb_path = os.path.join(THUMBNAILS_DIR, f"test_custom_{test_image.replace('.png', '.jpg')}")
                
                print(f"生成测试缩略图...")
                print(f"   原图: {test_image}")
                
                if generate_thumbnail(image_path, thumb_path):
                    orig_size = os.path.getsize(image_path)
                    thumb_size = os.path.getsize(thumb_path)
                    
                    print(f"   ✅ 缩略图生成成功")
                    print(f"   原图大小: {orig_size / 1024:.2f} KB")
                    print(f"   缩略图大小: {thumb_size / 1024:.2f} KB")
                    print(f"   压缩率: {(1 - thumb_size / orig_size) * 100:.1f}%")
                    
                    # 检查缩略图尺寸
                    with Image.open(thumb_path) as img:
                        print(f"   缩略图尺寸: {img.size[0]}x{img.size[1]}")
                    print()
                else:
                    print(f"   ❌ 缩略图生成失败")
                    print()
        
    finally:
        # 恢复原始配置
        if 'thumbnail' in original_thumb:
            original_config['thumbnail'] = original_thumb
        else:
            original_config.pop('thumbnail', None)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(original_config, f, ensure_ascii=False, indent=2)
        
        print("✅ 已恢复原始配置")
        print()


def test_different_formats():
    """测试不同格式"""
    print("=" * 60)
    print("测试 3: 测试不同输出格式")
    print("=" * 60)
    
    # 找到一张测试图片
    if not os.path.exists(IMAGES_DIR):
        print("❌ 图片目录不存在")
        return
    
    test_images = [f for f in os.listdir(IMAGES_DIR) if f.endswith('.png')]
    if not test_images:
        print("❌ 没有找到测试图片")
        return
    
    test_image = test_images[0]
    image_path = os.path.join(IMAGES_DIR, test_image)
    
    formats = ['JPEG', 'PNG', 'WEBP']
    
    for fmt in formats:
        thumb_path = os.path.join(THUMBNAILS_DIR, f"test_format_{test_image.replace('.png', '.' + fmt.lower())}")
        
        # 临时修改配置
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        original_thumb = config.get('thumbnail', {})
        config['thumbnail'] = {
            "max_size": [300, 300],
            "quality": 85,
            "format": fmt
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试 {fmt} 格式...")
        if generate_thumbnail(image_path, thumb_path):
            thumb_size = os.path.getsize(thumb_path)
            print(f"   ✅ {fmt} 缩略图生成成功")
            print(f"   文件大小: {thumb_size / 1024:.2f} KB")
            
            # 清理测试文件
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        else:
            print(f"   ❌ {fmt} 缩略图生成失败")
        
        # 恢复配置
        config['thumbnail'] = original_thumb
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    print()


if __name__ == '__main__':
    print("\n🔍 开始测试缩略图配置功能\n")
    
    test_default_config()
    test_custom_config()
    test_different_formats()
    
    print("=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print("\n💡 提示: 你可以在 config.json 中调整以下参数:")
    print("   - max_size: 缩略图最大尺寸")
    print("   - quality: 压缩质量 (1-100)")
    print("   - format: 输出格式 (JPEG/PNG/WEBP)")
    print()
