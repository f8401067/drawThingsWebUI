#!/usr/bin/env python3
"""
配置管理模块测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config_manager import (
    load_app_config,
    save_app_config,
    update_port,
    update_host,
    update_auto_open_browser
)


def test_config_management():
    """测试配置管理功能"""
    
    print("=" * 60)
    print("  配置管理模块测试")
    print("=" * 60)
    print()
    
    # 测试 1: 加载配置
    print("[测试 1] 加载配置...")
    config = load_app_config()
    print(f"✓ 配置加载成功: {config}")
    print()
    
    # 测试 2: 更新端口
    print("[测试 2] 更新端口为 8080...")
    result = update_port(8080)
    if result:
        print("✓ 端口更新成功")
        config = load_app_config()
        print(f"  当前端口: {config['port']}")
    else:
        print("✗ 端口更新失败")
    print()
    
    # 测试 3: 更新主机地址
    print("[测试 3] 更新主机地址为 127.0.0.1...")
    result = update_host("127.0.0.1")
    if result:
        print("✓ 主机地址更新成功")
        config = load_app_config()
        print(f"  当前主机: {config['host']}")
    else:
        print("✗ 主机地址更新失败")
    print()
    
    # 测试 4: 更新自动打开浏览器设置
    print("[测试 4] 关闭自动打开浏览器...")
    result = update_auto_open_browser(False)
    if result:
        print("✓ 设置更新成功")
        config = load_app_config()
        print(f"  自动打开浏览器: {config['auto_open_browser']}")
    else:
        print("✗ 设置更新失败")
    print()
    
    # 测试 5: 验证无效端口
    print("[测试 5] 测试无效端口（99999）...")
    result = update_port(99999)
    if not result:
        print("✓ 正确拒绝了无效端口")
    else:
        print("✗ 应该拒绝无效端口")
    print()
    
    # 恢复默认配置
    print("[清理] 恢复默认配置...")
    default_config = {
        "port": 9898,
        "host": "0.0.0.0",
        "debug": False,
        "auto_open_browser": True
    }
    save_app_config(default_config)
    print("✓ 已恢复默认配置")
    print()
    
    print("=" * 60)
    print("  测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_config_management()
