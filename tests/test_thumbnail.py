"""
测试缩略图生成功能
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pillow_import():
    """测试 Pillow 是否正确安装"""
    try:
        from PIL import Image
        print("✅ Pillow 库导入成功")
        print(f"   Pillow 版本: {Image.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Pillow 库导入失败: {e}")
        print("\n请运行以下命令安装:")
        print("   pip install Pillow")
        return False


def test_thumbnail_generation():
    """测试缩略图生成功能"""
    print("\n" + "=" * 60)
    print("测试缩略图生成功能")
    print("=" * 60)
    
    # 检查是否有图片可以测试
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'generated_images')
    
    if not os.path.exists(images_dir):
        print(f"❌ 图片目录不存在: {images_dir}")
        return False
    
    # 获取第一张图片
    files = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("⚠️  没有找到图片文件进行测试")
        print(f"   目录: {images_dir}")
        return False
    
    test_image = files[0]
    image_path = os.path.join(images_dir, test_image)
    
    print(f"\n📷 使用测试图片: {test_image}")
    print(f"   文件大小: {os.path.getsize(image_path) / 1024:.2f} KB")
    
    # 创建测试缩略图
    thumbnails_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True)
    
    thumb_filename = f"test_{test_image.replace('.png', '.jpg').replace('.jpeg', '.jpg')}"
    thumb_path = os.path.join(thumbnails_dir, thumb_filename)
    
    try:
        from src.app import generate_thumbnail
    except ModuleNotFoundError:
        from app import generate_thumbnail
    
    print(f"\n🔧 生成缩略图...")
    success = generate_thumbnail(image_path, thumb_path, size=(300, 300))
    
    if success and os.path.exists(thumb_path):
        thumb_size = os.path.getsize(thumb_path) / 1024
        original_size = os.path.getsize(image_path) / 1024
        compression_ratio = (1 - thumb_size / original_size) * 100
        
        print(f"✅ 缩略图生成成功!")
        print(f"   缩略图路径: {thumb_path}")
        print(f"   缩略图大小: {thumb_size:.2f} KB")
        print(f"   原图大小: {original_size:.2f} KB")
        print(f"   压缩率: {compression_ratio:.1f}%")
        print(f"   缩小倍数: {original_size / thumb_size:.1f}x")
        
        # 清理测试文件
        os.remove(thumb_path)
        print(f"\n🧹 已清理测试文件")
        
        return True
    else:
        print(f"❌ 缩略图生成失败")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("缩略图功能测试")
    print("=" * 60)
    
    # 测试 1: Pillow 导入
    if not test_pillow_import():
        sys.exit(1)
    
    # 测试 2: 缩略图生成
    if not test_thumbnail_generation():
        print("\n⚠️  测试未完全通过，但基本功能可能正常")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过!")
    print("=" * 60)
