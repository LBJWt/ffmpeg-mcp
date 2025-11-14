#!/usr/bin/env python3
"""
FFmpeg MCP Server
一个基于FFmpeg的媒体处理MCP工具，支持图片和视频的转码、压缩等功能
"""

import asyncio
import json
import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Any, Sequence, Optional, Dict, List
from PIL import Image
import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ffmpeg_mcp")

# 创建MCP服务器实例
server = Server("ffmpeg-mcp")

class FFmpegProcessor:
    """FFmpeg处理器类"""
    
    @staticmethod
    def check_ffmpeg_available() -> bool:
        """检查FFmpeg是否可用"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_media_info(file_path: str) -> Dict[str, Any]:
        """获取媒体文件信息"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json", 
                "-show_format", "-show_streams", file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise Exception(f"FFprobe error: {result.stderr}")
        except Exception as e:
            raise Exception(f"Failed to get media info: {str(e)}")
    
    @staticmethod
    def compress_image(input_path: str, output_path: str, quality: int = 85) -> bool:
        """压缩图片"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-q:v", str(quality),
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def convert_image_format(input_path: str, output_path: str, format: str = "jpg") -> bool:
        """转换图片格式"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def resize_image(input_path: str, output_path: str, width: int, height: int) -> bool:
        """调整图片尺寸"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"scale={width}:{height}",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def compress_video(input_path: str, output_path: str, crf: int = 23, preset: str = "medium") -> bool:
        """压缩视频"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
                "-c:a", "aac", "-b:a", "128k",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def convert_video_format(input_path: str, output_path: str, format: str = "mp4") -> bool:
        """转换视频格式"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def resize_video(input_path: str, output_path: str, width: int, height: int) -> bool:
        """调整视频尺寸"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"scale={width}:{height}",
                "-c:a", "copy",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

class FileManager:
    """文件管理器类"""
    
    @staticmethod
    def get_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
        """根据扩展名获取文件列表"""
        files = []
        path = Path(directory)
        if path.exists() and path.is_dir():
            for ext in extensions:
                files.extend(path.glob(f"*.{ext}"))
                files.extend(path.glob(f"*.{ext.upper()}"))
        return [str(f) for f in files]
    
    @staticmethod
    def batch_process_files(input_dir: str, output_dir: str, process_func, **kwargs) -> Dict[str, Any]:
        """批量处理文件"""
        results = {
            "success": [],
            "failed": [],
            "total": 0
        }
        
        # 图片扩展名
        image_extensions = ["jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"]
        # 视频扩展名
        video_extensions = ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v"]
        
        all_extensions = image_extensions + video_extensions
        files = FileManager.get_files_by_extension(input_dir, all_extensions)
        
        results["total"] = len(files)
        
        for file_path in files:
            try:
                file_name = Path(file_path).name
                output_path = os.path.join(output_dir, file_name)
                
                if process_func(file_path, output_path, **kwargs):
                    results["success"].append(file_name)
                else:
                    results["failed"].append(file_name)
            except Exception as e:
                results["failed"].append(f"{Path(file_path).name}: {str(e)}")
        
        return results


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出可用的工具函数
    """
    return [
        types.Tool(
            name="compress_image",
            description="压缩单个图片文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "输入图片文件路径"
                    },
                    "output_path": {
                        "type": "string", 
                        "description": "输出图片文件路径"
                    },
                    "quality": {
                        "type": "integer",
                        "description": "压缩质量 (1-100, 默认85)",
                        "default": 85
                    }
                },
                "required": ["input_path", "output_path"]
            },
        ),
        types.Tool(
            name="batch_compress_images",
            description="批量压缩指定文件夹中的所有图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "description": "输入文件夹路径"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出文件夹路径"
                    },
                    "quality": {
                        "type": "integer",
                        "description": "压缩质量 (1-100, 默认85)",
                        "default": 85
                    }
                },
                "required": ["input_dir", "output_dir"]
            },
        ),
        types.Tool(
            name="convert_image_format",
            description="转换图片格式",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "输入图片文件路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片文件路径"
                    }
                },
                "required": ["input_path", "output_path"]
            },
        ),
        types.Tool(
            name="resize_image",
            description="调整图片尺寸",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "输入图片文件路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片文件路径"
                    },
                    "width": {
                        "type": "integer",
                        "description": "目标宽度"
                    },
                    "height": {
                        "type": "integer", 
                        "description": "目标高度"
                    }
                },
                "required": ["input_path", "output_path", "width", "height"]
            },
        ),
        types.Tool(
            name="compress_video",
            description="压缩单个视频文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "输入视频文件路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出视频文件路径"
                    },
                    "crf": {
                        "type": "integer",
                        "description": "压缩质量 (18-28, 数值越小质量越高, 默认23)",
                        "default": 23
                    },
                    "preset": {
                        "type": "string",
                        "description": "压缩速度预设 (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, 默认medium)",
                        "default": "medium"
                    }
                },
                "required": ["input_path", "output_path"]
            },
        ),
        types.Tool(
            name="batch_compress_videos",
            description="批量压缩指定文件夹中的所有视频",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "description": "输入文件夹路径"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出文件夹路径"
                    },
                    "crf": {
                        "type": "integer",
                        "description": "压缩质量 (18-28, 数值越小质量越高, 默认23)",
                        "default": 23
                    },
                    "preset": {
                        "type": "string",
                        "description": "压缩速度预设 (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, 默认medium)",
                        "default": "medium"
                    }
                },
                "required": ["input_dir", "output_dir"]
            },
        ),
        types.Tool(
            name="convert_video_format",
            description="转换视频格式",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "输入视频文件路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出视频文件路径"
                    }
                },
                "required": ["input_path", "output_path"]
            },
        ),
        types.Tool(
            name="resize_video",
            description="调整视频尺寸",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "输入视频文件路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出视频文件路径"
                    },
                    "width": {
                        "type": "integer",
                        "description": "目标宽度"
                    },
                    "height": {
                        "type": "integer",
                        "description": "目标高度"
                    }
                },
                "required": ["input_path", "output_path", "width", "height"]
            },
        ),
        types.Tool(
            name="get_media_info",
            description="获取媒体文件信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "媒体文件路径"
                    }
                },
                "required": ["file_path"]
            },
        ),
        types.Tool(
            name="check_ffmpeg_status",
            description="检查FFmpeg是否已安装并可用",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """
    处理工具调用
    """
    if arguments is None:
        arguments = {}

    try:
        if name == "compress_image":
            input_path = arguments.get("input_path")
            output_path = arguments.get("output_path")
            quality = arguments.get("quality", 85)
            
            if not os.path.exists(input_path):
                return [types.TextContent(type="text", text=f"错误：输入文件不存在: {input_path}")]
            
            success = FFmpegProcessor.compress_image(input_path, output_path, quality)
            if success:
                return [types.TextContent(type="text", text=f"图片压缩成功：{input_path} -> {output_path}")]
            else:
                return [types.TextContent(type="text", text=f"图片压缩失败：{input_path}")]

        elif name == "batch_compress_images":
            input_dir = arguments.get("input_dir")
            output_dir = arguments.get("output_dir")
            quality = arguments.get("quality", 85)
            
            if not os.path.exists(input_dir):
                return [types.TextContent(type="text", text=f"错误：输入目录不存在: {input_dir}")]
            
            results = FileManager.batch_process_files(
                input_dir, output_dir, FFmpegProcessor.compress_image, quality=quality
            )
            
            message = f"批量图片压缩完成！\n总计: {results['total']} 个文件\n成功: {len(results['success'])} 个\n失败: {len(results['failed'])} 个"
            if results['failed']:
                message += f"\n失败的文件: {', '.join(results['failed'])}"
            
            return [types.TextContent(type="text", text=message)]

        elif name == "convert_image_format":
            input_path = arguments.get("input_path")
            output_path = arguments.get("output_path")
            
            if not os.path.exists(input_path):
                return [types.TextContent(type="text", text=f"错误：输入文件不存在: {input_path}")]
            
            success = FFmpegProcessor.convert_image_format(input_path, output_path)
            if success:
                return [types.TextContent(type="text", text=f"图片格式转换成功：{input_path} -> {output_path}")]
            else:
                return [types.TextContent(type="text", text=f"图片格式转换失败：{input_path}")]

        elif name == "resize_image":
            input_path = arguments.get("input_path")
            output_path = arguments.get("output_path")
            width = arguments.get("width")
            height = arguments.get("height")
            
            if not os.path.exists(input_path):
                return [types.TextContent(type="text", text=f"错误：输入文件不存在: {input_path}")]
            
            success = FFmpegProcessor.resize_image(input_path, output_path, width, height)
            if success:
                return [types.TextContent(type="text", text=f"图片尺寸调整成功：{input_path} -> {output_path} ({width}x{height})")]
            else:
                return [types.TextContent(type="text", text=f"图片尺寸调整失败：{input_path}")]

        elif name == "compress_video":
            input_path = arguments.get("input_path")
            output_path = arguments.get("output_path")
            crf = arguments.get("crf", 23)
            preset = arguments.get("preset", "medium")
            
            if not os.path.exists(input_path):
                return [types.TextContent(type="text", text=f"错误：输入文件不存在: {input_path}")]
            
            success = FFmpegProcessor.compress_video(input_path, output_path, crf, preset)
            if success:
                return [types.TextContent(type="text", text=f"视频压缩成功：{input_path} -> {output_path}")]
            else:
                return [types.TextContent(type="text", text=f"视频压缩失败：{input_path}")]

        elif name == "batch_compress_videos":
            input_dir = arguments.get("input_dir")
            output_dir = arguments.get("output_dir")
            crf = arguments.get("crf", 23)
            preset = arguments.get("preset", "medium")
            
            if not os.path.exists(input_dir):
                return [types.TextContent(type="text", text=f"错误：输入目录不存在: {input_dir}")]
            
            results = FileManager.batch_process_files(
                input_dir, output_dir, FFmpegProcessor.compress_video, crf=crf, preset=preset
            )
            
            message = f"批量视频压缩完成！\n总计: {results['total']} 个文件\n成功: {len(results['success'])} 个\n失败: {len(results['failed'])} 个"
            if results['failed']:
                message += f"\n失败的文件: {', '.join(results['failed'])}"
            
            return [types.TextContent(type="text", text=message)]

        elif name == "convert_video_format":
            input_path = arguments.get("input_path")
            output_path = arguments.get("output_path")
            
            if not os.path.exists(input_path):
                return [types.TextContent(type="text", text=f"错误：输入文件不存在: {input_path}")]
            
            success = FFmpegProcessor.convert_video_format(input_path, output_path)
            if success:
                return [types.TextContent(type="text", text=f"视频格式转换成功：{input_path} -> {output_path}")]
            else:
                return [types.TextContent(type="text", text=f"视频格式转换失败：{input_path}")]

        elif name == "resize_video":
            input_path = arguments.get("input_path")
            output_path = arguments.get("output_path")
            width = arguments.get("width")
            height = arguments.get("height")
            
            if not os.path.exists(input_path):
                return [types.TextContent(type="text", text=f"错误：输入文件不存在: {input_path}")]
            
            success = FFmpegProcessor.resize_video(input_path, output_path, width, height)
            if success:
                return [types.TextContent(type="text", text=f"视频尺寸调整成功：{input_path} -> {output_path} ({width}x{height})")]
            else:
                return [types.TextContent(type="text", text=f"视频尺寸调整失败：{input_path}")]

        elif name == "get_media_info":
            file_path = arguments.get("file_path")
            
            if not os.path.exists(file_path):
                return [types.TextContent(type="text", text=f"错误：文件不存在: {file_path}")]
            
            try:
                info = FFmpegProcessor.get_media_info(file_path)
                return [types.TextContent(type="text", text=json.dumps(info, indent=2, ensure_ascii=False))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"获取媒体信息失败：{str(e)}")]

        elif name == "check_ffmpeg_status":
            available = FFmpegProcessor.check_ffmpeg_available()
            if available:
                return [types.TextContent(type="text", text="FFmpeg 已安装并可用")]
            else:
                return [types.TextContent(type="text", text="FFmpeg 未安装或不可用，请先安装FFmpeg")]

        else:
            return [types.TextContent(type="text", text=f"未知的工具名称: {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"工具执行出错: {str(e)}")]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ffmpeg-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
