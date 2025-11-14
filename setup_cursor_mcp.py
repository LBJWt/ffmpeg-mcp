#!/usr/bin/env python3
"""
自动配置Cursor MCP设置的脚本
"""

import json
import os
import platform
import sys
from pathlib import Path

def get_current_directory():
    """获取当前项目目录的绝对路径"""
    return os.path.abspath(os.path.dirname(__file__))

def get_cursor_config_path():
    """获取Cursor配置文件路径"""
    system = platform.system()
    
    if system == "Windows":
        config_path = os.path.expanduser("~\\AppData\\Roaming\\Cursor\\User\\settings.json")
    elif system == "Darwin":  # macOS
        config_path = os.path.expanduser("~/Library/Application Support/Cursor/User/settings.json")
    elif system == "Linux":
        config_path = os.path.expanduser("~/.config/Cursor/User/settings.json")
    else:
        return None
    
    return config_path

def get_python_executable():
    """获取Python可执行文件路径"""
    return sys.executable

def create_mcp_config():
    """创建MCP配置"""
    current_dir = get_current_directory()
    python_exe = get_python_executable()
    
    # 使用正斜杠，在所有系统上都能工作
    ffmpeg_script = os.path.join(current_dir, "ffmpeg_mcp.py").replace("\\", "/")
    
    config = {
        "ffmpeg": {
            "command": python_exe.replace("\\", "/"),
            "args": [ffmpeg_script],
            "env": {
                "PYTHONPATH": current_dir.replace("\\", "/")
            }
        }
    }
    
    return config

def save_standalone_config():
    """保存独立的配置文件供手动使用"""
    config = {
        "mcpServers": create_mcp_config()
    }
    
    config_file = os.path.join(get_current_directory(), "cursor_mcp_config.json")
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已创建配置文件：{config_file}")
    return config_file

def update_cursor_config():
    """更新Cursor的配置文件"""
    cursor_config_path = get_cursor_config_path()
    
    if not cursor_config_path:
        print("✗ 无法确定Cursor配置文件路径")
        return False
    
    # 确保配置目录存在
    os.makedirs(os.path.dirname(cursor_config_path), exist_ok=True)
    
    # 读取现有配置
    existing_config = {}
    if os.path.exists(cursor_config_path):
        try:
            with open(cursor_config_path, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except Exception as e:
            print(f"⚠️  读取现有配置文件时出错：{e}")
            existing_config = {}
    
    # 添加或更新MCP配置
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"].update(create_mcp_config())
    
    # 保存配置
    try:
        with open(cursor_config_path, "w", encoding="utf-8") as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 已更新Cursor配置文件：{cursor_config_path}")
        return True
    
    except Exception as e:
        print(f"✗ 更新配置文件失败：{e}")
        return False

def create_project_config():
    """在项目目录创建.cursor-server配置"""
    cursor_server_dir = os.path.join(get_current_directory(), ".cursor-server")
    os.makedirs(cursor_server_dir, exist_ok=True)
    
    config = {
        "mcpServers": {
            "ffmpeg": {
                "command": "python",
                "args": ["./ffmpeg_mcp.py"],
                "env": None
            }
        }
    }
    
    config_file = os.path.join(cursor_server_dir, "config.json")
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ 已创建项目配置：{config_file}")
    return config_file

def show_manual_instructions(config_file):
    """显示手动配置说明"""
    print("\n" + "="*60)
    print("手动配置说明")
    print("="*60)
    
    print(f"\n如果自动配置失败，请手动进行以下操作：")
    print(f"\n1. 打开Cursor设置 (Ctrl+, 或 Cmd+,)")
    print(f"2. 搜索 'MCP' 设置")
    print(f"3. 添加以下配置内容：")
    
    # 读取并显示配置内容
    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    print(f"\n{config_content}")
    
    print(f"\n4. 保存设置并重启Cursor")
    print(f"\n配置文件已保存到：{config_file}")

def main():
    """主函数"""
    print("=== Cursor MCP 配置工具 ===")
    print("正在配置FFmpeg MCP工具...")
    
    # 检查当前目录是否包含必要文件
    current_dir = get_current_directory()
    ffmpeg_script = os.path.join(current_dir, "ffmpeg_mcp.py")
    
    if not os.path.exists(ffmpeg_script):
        print(f"✗ 找不到ffmpeg_mcp.py文件：{ffmpeg_script}")
        print("请确保在正确的项目目录中运行此脚本")
        sys.exit(1)
    
    print(f"✓ 项目目录：{current_dir}")
    print(f"✓ Python路径：{get_python_executable()}")
    
    # 创建独立配置文件
    config_file = save_standalone_config()
    
    # 尝试多种配置方式
    success_methods = []
    
    # 方法1：更新全局Cursor配置
    print("\n正在尝试更新Cursor全局配置...")
    if update_cursor_config():
        success_methods.append("全局配置")
    
    # 方法2：创建项目配置
    print("\n正在创建项目特定配置...")
    try:
        create_project_config()
        success_methods.append("项目配置")
    except Exception as e:
        print(f"✗ 创建项目配置失败：{e}")
    
    # 显示结果
    print("\n" + "="*60)
    print("配置完成!")
    print("="*60)
    
    if success_methods:
        print(f"✓ 成功创建配置：{', '.join(success_methods)}")
        print("\n下一步：")
        print("1. 重启Cursor")
        print("2. 在Cursor中测试FFmpeg MCP工具")
        print("   例如输入：'压缩D:/1文件夹中的图片到D:/output'")
    else:
        print("⚠️  自动配置未完全成功，请查看手动配置说明：")
        show_manual_instructions(config_file)
    
    print(f"\n详细配置说明请查看：CURSOR_SETUP.md")

if __name__ == "__main__":
    main()

