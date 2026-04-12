#!/usr/bin/env python3
"""
配置管理模块
用于管理应用的运行时配置（端口、主机等）
"""

import os
import sys
import json
from pathlib import Path


def get_config_file_path():
    """获取配置文件路径
    
    兼容开发环境和 PyInstaller 打包环境
    统一使用 config.json 作为唯一配置文件
    """
    # 如果是 PyInstaller 打包的应用
    if getattr(sys, 'frozen', False):
        # 使用可执行文件所在目录
        base_dir = Path(sys.executable).parent
    else:
        # 开发环境：项目根目录
        base_dir = Path(__file__).parent.parent
    
    return base_dir / "config.json"


def load_app_config():
    """加载应用配置
    
    从 config.json 中读取所有配置（包括应用启动配置和大模型配置）
    
    Returns:
        dict: 包含 port, host, debug, auto_open_browser 等配置项
    """
    config_file = get_config_file_path()
    
    # 默认配置
    default_config = {
        "port": 9898,
        "host": "0.0.0.0",
        "debug": False,
        "auto_open_browser": True
    }
    
    if not config_file.exists():
        # 如果配置文件不存在，创建默认配置
        save_app_config(default_config)
        print(f"[信息] 已创建默认配置文件: {config_file}")
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 合并默认配置，确保所有字段都存在
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"[警告] 读取配置文件失败: {e}，使用默认配置")
        return default_config


def save_app_config(config):
    """保存应用配置
    
    Args:
        config (dict): 要保存的配置字典
    
    Returns:
        bool: 保存成功返回 True
    """
    config_file = get_config_file_path()
    
    try:
        # 确保目录存在
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"[信息] 配置已保存到: {config_file}")
        return True
    except IOError as e:
        print(f"[错误] 保存配置文件失败: {e}")
        return False


def update_port(port):
    """更新端口配置
    
    Args:
        port (int): 新的端口号
    
    Returns:
        bool: 更新成功返回 True
    """
    if not isinstance(port, int) or port < 1 or port > 65535:
        print(f"[错误] 无效的端口号: {port}")
        return False
    
    config = load_app_config()
    config['port'] = port
    
    return save_app_config(config)


def update_host(host):
    """更新主机地址配置
    
    Args:
        host (str): 新的主机地址
    
    Returns:
        bool: 更新成功返回 True
    """
    config = load_app_config()
    config['host'] = host
    
    return save_app_config(config)


def update_auto_open_browser(auto_open):
    """更新自动打开浏览器配置
    
    Args:
        auto_open (bool): 是否自动打开浏览器
    
    Returns:
        bool: 更新成功返回 True
    """
    config = load_app_config()
    config['auto_open_browser'] = auto_open
    
    return save_app_config(config)
