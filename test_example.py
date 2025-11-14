#!/usr/bin/env python3
"""
FFmpeg MCP工具的测试示例
展示如何使用各种功能
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from ffmpeg_mcp import server

async def test_ffmpeg_mcp():
    """测试FFmpeg MCP工具的功能"""
    
    # 这里是一些使用示例，实际使用时需要根据你的文件路径调整
    test_cases = [
        {
            "name": "check_ffmpeg_status",
            "description": "检查FFmpeg状态",
            "arguments": {}
        },
        {
            "name": "get_media_info", 
            "description": "获取媒体文件信息",
            "arguments": {
                "file_path": "D:/test/sample.jpg"  # 请替换为实际的文件路径
            }
        },
        {
            "name": "compress_image",
            "description": "压缩单个图片",
            "arguments": {
                "input_path": "D:/test/input.jpg",  # 请替换为实际的输入路径
                "output_path": "D:/output/compressed.jpg",  # 请替换为实际的输出路径
                "quality": 80
            }
        },
        {
            "name": "batch_compress_images",
            "description": "批量压缩图片", 
            "arguments": {
                "input_dir": "D:/1",  # 你提到的输入目录
                "output_dir": "D:/output",  # 你提到的输出目录
                "quality": 85
            }
        },
        {
            "name": "compress_video",
            "description": "压缩单个视频",
            "arguments": {
                "input_path": "D:/test/input.mp4",  # 请替换为实际的输入路径
                "output_path": "D:/output/compressed.mp4",  # 请替换为实际的输出路径
                "crf": 23,
                "preset": "medium"
            }
        }
    ]
    
    print("=== FFmpeg MCP工具测试示例 ===")
    print("注意：请根据你的实际文件路径修改测试用例\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['description']}")
        print(f"   工具名称: {test_case['name']}")
        print(f"   参数: {json.dumps(test_case['arguments'], indent=2, ensure_ascii=False)}")
        print()

if __name__ == "__main__":
    asyncio.run(test_ffmpeg_mcp())
