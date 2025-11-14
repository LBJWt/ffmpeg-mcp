#!/usr/bin/env python3
"""
FFmpeg MCP工具安装脚本
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        print(f"当前版本：{sys.version}")
        return False
    print(f"✓ Python版本检查通过：{sys.version}")
    return True

def install_requirements():
    """安装Python依赖"""
    print("正在安装Python依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Python依赖安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ Python依赖安装失败")
        return False

def check_ffmpeg():
    """检查FFmpeg是否安装"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ FFmpeg已安装并可用")
            return True
        else:
            print("✗ FFmpeg不可用")
            return False
    except Exception:
        print("✗ FFmpeg未安装或不在PATH中")
        return False

def show_ffmpeg_install_instructions():
    """显示FFmpeg安装说明"""
    system = platform.system()
    print("\n=== FFmpeg安装说明 ===")
    
    if system == "Windows":
        print("Windows用户请按以下步骤安装FFmpeg：")
        print("1. 访问 https://ffmpeg.org/download.html#build-windows")
        print("2. 下载FFmpeg压缩包")
        print("3. 解压到某个目录（如 C:\\ffmpeg）")
        print("4. 将 C:\\ffmpeg\\bin 添加到系统PATH环境变量")
        print("5. 重启命令提示符并运行 'ffmpeg -version' 验证")
    
    elif system == "Darwin":  # macOS
        print("macOS用户可以使用Homebrew安装：")
        print("brew install ffmpeg")
    
    elif system == "Linux":
        print("Linux用户可以使用包管理器安装：")
        print("Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("CentOS/RHEL: sudo yum install ffmpeg 或 sudo dnf install ffmpeg")
    
    print("\n安装完成后，请重新运行此安装脚本进行验证。")

def create_test_directories():
    """创建测试目录"""
    test_dirs = ["test_input", "test_output"]
    for dir_name in test_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建测试目录：{dir_name}")

def main():
    """主安装函数"""
    print("=== FFmpeg MCP工具安装程序 ===")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装Python依赖
    if not install_requirements():
        print("请解决依赖安装问题后重试")
        sys.exit(1)
    
    # 检查FFmpeg
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        show_ffmpeg_install_instructions()
        print("\n⚠️  警告：FFmpeg未正确安装，某些功能可能无法使用")
    
    # 创建测试目录
    create_test_directories()
    
    print("\n=== 安装完成 ===")
    if ffmpeg_ok:
        print("✓ 所有组件安装成功！")
        print("你现在可以运行：")
        print("  python start_server.py  # 启动MCP服务器")
        print("  或者在Windows上双击 start_server.bat")
    else:
        print("⚠️  安装部分完成，请安装FFmpeg后再使用")
    
    print("\n详细使用说明请查看 README.md 文件")

if __name__ == "__main__":
    main()
