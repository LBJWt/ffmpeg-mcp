#!/usr/bin/env python3
"""
启动FFmpeg MCP服务器的便捷脚本
"""

import asyncio
import sys
import os

# 将当前目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ffmpeg_mcp import main

if __name__ == "__main__":
    print("启动 FFmpeg MCP 服务器...")
    print("确保你已经安装了 FFmpeg 并且可以在命令行中使用")
    print("按 Ctrl+C 停止服务器")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)
