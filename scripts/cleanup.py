"""
清理脚本 - 清理项目中的临时文件和缓存
"""

import os
import shutil
import glob


def clean_pycache():
    """清理 Python 缓存文件"""
    print("清理 Python 缓存...")
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            path = os.path.join(root, '__pycache__')
            shutil.rmtree(path)
            print(f"  删除: {path}")


def clean_test_db():
    """清理测试数据库"""
    print("\n清理测试数据...")
    test_files = [
        'test_history.db',
        'test_timing_stats.json',
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  删除: {file}")


def clean_temp_files():
    """清理临时文件"""
    print("\n清理临时文件...")
    temp_patterns = [
        '*.pyc',
        '*.pyo',
        '*~',
        '.DS_Store',
    ]
    
    for pattern in temp_patterns:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"  删除: {file}")


def clean_old_images(days=30):
    """清理超过指定天数的生成图片
    
    Args:
        days (int): 保留的天数，默认 30 天
    """
    print(f"\n清理 {days} 天前的生成图片...")
    
    import time
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    images_dir = 'generated_images'
    
    if not os.path.exists(images_dir):
        print("  生成图片目录不存在")
        return
    
    deleted_count = 0
    for filename in os.listdir(images_dir):
        if filename.endswith('.png'):
            filepath = os.path.join(images_dir, filename)
            # 从文件名提取日期
            try:
                # 文件名格式: generated_YYYYMMDD_HHMMSS.png
                date_str = filename.replace('generated_', '').replace('.png', '')
                date_part = date_str.split('_')[0]
                file_date = datetime.strptime(date_part, '%Y%m%d')
                
                if file_date < cutoff_date:
                    os.remove(filepath)
                    print(f"  删除: {filename}")
                    deleted_count += 1
            except (ValueError, IndexError):
                # 如果文件名格式不匹配，跳过
                pass
    
    print(f"  共删除 {deleted_count} 张图片")


def show_directory_size():
    """显示各目录大小"""
    print("\n" + "="*60)
    print("目录大小统计")
    print("="*60)
    
    directories = [
        'generated_images',
        'tests',
        'docs',
        'scripts',
        'static',
    ]
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            total_size = 0
            file_count = 0
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
                        file_count += 1
            
            # 转换为单位
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024 * 1024:
                size_str = f"{total_size / 1024:.2f} KB"
            else:
                size_str = f"{total_size / (1024 * 1024):.2f} MB"
            
            print(f"{dir_name:25} {file_count:4} 文件  {size_str:>10}")


def main():
    """主函数"""
    print("="*60)
    print("项目清理工具")
    print("="*60)
    
    # 执行清理
    clean_pycache()
    clean_test_db()
    clean_temp_files()
    
    # 可选：清理旧图片（取消注释以启用）
    # clean_old_images(days=30)
    
    # 显示目录大小
    show_directory_size()
    
    print("\n" + "="*60)
    print("清理完成！")
    print("="*60)


if __name__ == "__main__":
    main()

