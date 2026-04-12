#!/usr/bin/env python3
"""
DrawThings WebUI - 统一启动器
支持开发环境和打包后的环境
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包）"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def main():
    """主函数"""
    # 设置工作目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(application_path)
    
    # 确保数据目录存在
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "generated_images").mkdir(exist_ok=True)
    (data_dir / "thumbnails").mkdir(exist_ok=True)
    (data_dir / "logs").mkdir(exist_ok=True)
    
    # 加载应用配置
    try:
        from src.config_manager import load_app_config
        config = load_app_config()
        port = config.get('port', 9898)
        host = config.get('host', '0.0.0.0')
        debug = config.get('debug', False)
        auto_open_browser = config.get('auto_open_browser', True)
    except ImportError:
        # 如果配置模块不存在，使用默认值
        port = 9898
        host = '0.0.0.0'
        debug = False
        auto_open_browser = True
    except Exception as e:
        print(f"[警告] 加载配置失败: {e}，使用默认配置")
        port = 9898
        host = '0.0.0.0'
        debug = False
        auto_open_browser = True
    
    # 导入并启动 Flask 应用
    from src.app import app
    
    print("=" * 60)
    print("  DrawThings WebUI Server")
    print("=" * 60)
    print()
    print(f"[INFO] 服务器地址: http://{host}:{port}")
    print(f"[INFO] 调试模式: {'开启' if debug else '关闭'}")
    print("[INFO] 按 Ctrl+C 停止服务器")
    print()
    
    # 在 macOS 上自动打开浏览器
    if auto_open_browser and sys.platform == 'darwin':
        import subprocess
        import time
        
        def open_browser():
            time.sleep(2)
            subprocess.call(['open', f'http://localhost:{port}'])
        
        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        print(f"[INFO] 将在 2 秒后自动打开浏览器...")
    
    # 启动 Flask 服务器
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False
    )


if __name__ == '__main__':
    main()
