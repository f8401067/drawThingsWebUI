#!/usr/bin/env python3
"""
DrawThings WebUI - 独立应用打包脚本
使用 PyInstaller 创建无需 Python 环境的独立应用
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def build_standalone_app():
    """构建独立应用（兼容 macOS 和 Windows）"""
    
    project_root = Path(__file__).parent
    dist_path = project_root / "dist"
    build_path = project_root / "build_temp"
    
    print("=" * 60)
    print("  DrawThings WebUI - 独立应用打包工具")
    print("=" * 60)
    print()
    
    # 检查 PyInstaller 是否安装
    try:
        import PyInstaller
    except ImportError:
        print("[错误] PyInstaller 未安装")
        print("请先运行: pip install pyinstaller")
        return False
    
    # 清理旧的构建文件
    print("[信息] 清理旧的构建文件...")
    for path in [dist_path, build_path]:
        if path.exists():
            shutil.rmtree(path)
            print(f"  ✓ 已删除 {path.name}")
    
    # 创建 PyInstaller spec 文件
    print("[信息] 创建打包配置...")
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('data', 'data'),
        ('scripts', 'scripts'),
        ('src/config_manager.py', 'src'),
        ('src/history_routes.py', 'src'),
        ('src/ai_refine.py', 'src'),
        ('src/llm_client.py', 'src'),
        ('src/database.py', 'src'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'requests',
        'PIL',
        'sqlite3',
        'src.config_manager',
        'src.history_routes',
        'src.ai_refine',
        'src.llm_client',
        'src.database',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DrawThingsWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_file = project_root / "drawthings_standalone.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"  ✓ 已创建 {spec_file.name}")
    
    # 运行 PyInstaller
    print("[信息] 运行 PyInstaller...")
    print("[提示] 这可能需要几分钟时间，请耐心等待...")
    print()
    
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        str(spec_file),
        "--clean",
        "--noconfirm"
    ], cwd=project_root)
    
    if result.returncode != 0:
        print("[错误] PyInstaller 打包失败")
        return False
    
    print()
    print("  ✓ PyInstaller 打包完成")
    
    # 根据平台进行后续处理
    if sys.platform == 'darwin':
        return create_macos_app_bundle(project_root, dist_path)
    elif sys.platform == 'win32':
        print()
        print("=" * 60)
        print("  Windows 打包完成！")
        print("=" * 60)
        print()
        print(f"可执行文件位置: {dist_path / 'DrawThingsWebUI.exe'}")
        print()
        print("使用方法:")
        print("  1. 双击 DrawThingsWebUI.exe 启动")
        print("  2. 首次启动会自动创建 app_config.json 配置文件")
        print("  3. 可以编辑配置文件修改端口等设置")
        print()
        return True
    else:
        print()
        print("=" * 60)
        print("  打包完成！")
        print("=" * 60)
        print()
        print(f"可执行文件位置: {dist_path / 'DrawThingsWebUI'}")
        print()
        return True


def create_macos_app_bundle(project_root, dist_path):
    """创建 macOS .app 应用包"""
    
    print("[信息] 创建 macOS 应用包...")
    
    app_name = "DrawThings WebUI.app"
    app_path = dist_path / app_name
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # 创建目录结构
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # 移动可执行文件
    exe_src = dist_path / "DrawThingsWebUI"
    exe_dst = macos_path / "DrawThingsWebUI"
    
    if exe_src.exists():
        shutil.move(str(exe_src), str(exe_dst))
        exe_dst.chmod(0o755)
        print("  ✓ 可执行文件")
    
    # 复制 Info.plist
    plist_src = project_root / "build" / "Info.plist"
    plist_dst = contents_path / "Info.plist"
    
    if plist_src.exists():
        shutil.copy2(plist_src, plist_dst)
        print("  ✓ Info.plist")
    else:
        # 创建基本的 Info.plist（使用正确的可执行文件名）
        plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>DrawThings WebUI</string>
    <key>CFBundleDisplayName</key>
    <string>DrawThings WebUI</string>
    <key>CFBundleIdentifier</key>
    <string>com.drawthings.webui</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>DrawThingsWebUI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
'''
        with open(plist_dst, 'w', encoding='utf-8') as f:
            f.write(plist_content)
        print("  ✓ Info.plist (默认)")
    
    # 复制图标（如果存在）
    icon_src = project_root / "build" / "app_icon.icns"
    icon_dst = resources_path / "app_icon.icns"
    
    if icon_src.exists():
        shutil.copy2(icon_src, icon_dst)
        print("  ✓ 应用图标")
    
    # 复制示例配置文件到 Resources
    example_config = project_root / "config.example.json"
    if example_config.exists():
        shutil.copy2(example_config, resources_path / "config.example.json")
        print("  ✓ 示例配置文件")
    
    # 复制配置说明文档
    config_guide = project_root / "CONFIG_GUIDE.md"
    if config_guide.exists():
        shutil.copy2(config_guide, resources_path / "CONFIG_GUIDE.md")
        print("  ✓ 配置说明文档")
    
    print()
    print("=" * 60)
    print("  macOS 应用包打包完成！")
    print("=" * 60)
    print()
    print(f"应用位置: {app_path}")
    print()
    print("使用方法:")
    print("  1. 双击 DrawThings WebUI.app 启动")
    print("  2. 首次启动会自动创建 config.json 配置文件")
    print("  3. 可以编辑配置文件修改端口等设置")
    print("  4. 确保 DrawThings 服务已启动")
    print()
    print("配置文件位置:")
    print(f"  {app_path}/Contents/Resources/config.json")
    print()
    
    return True


if __name__ == "__main__":
    success = build_standalone_app()
    sys.exit(0 if success else 1)
