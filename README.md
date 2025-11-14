# FFmpeg MCP Tool

一个基于FFmpeg的MCP（Model Context Protocol）工具，用于处理图片和视频的转码、压缩等操作。

## 功能特性

### 图片处理
- 图片压缩（单个文件或批量处理）
- 图片格式转换（JPG、PNG、BMP、GIF、TIFF、WebP等）
- 图片尺寸调整
- 获取图片信息

### 视频处理
- 视频压缩（支持H.264编码）
- 视频格式转换（MP4、AVI、MKV、MOV等）
- 视频尺寸调整
- 获取视频信息

### 批量处理
- 支持批量压缩指定文件夹中的所有图片
- 支持批量压缩指定文件夹中的所有视频
- 自动识别常见的图片和视频格式

## 系统要求

1. Python 3.8+
2. FFmpeg（必须安装并可在命令行中使用）

## 安装步骤

### 1. 安装FFmpeg

#### Windows
- 下载FFmpeg：https://ffmpeg.org/download.html#build-windows
- 解压到某个目录（如 `C:\ffmpeg`）
- 将 `C:\ffmpeg\bin` 添加到系统PATH环境变量
- 打开命令提示符，运行 `ffmpeg -version` 验证安装

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 启动MCP服务器

```bash
python start_server.py
```

### 2. 配置MCP客户端

将 `config.json` 中的配置添加到你的MCP客户端配置中：

```json
{
  "mcpServers": {
    "ffmpeg": {
      "command": "python",
      "args": ["path/to/ffmpeg_mcp.py"],
      "env": null
    }
  }
}
```

### 3. 可用工具

#### 图片处理工具

##### `compress_image`
压缩单个图片文件
```json
{
  "input_path": "D:/input/image.jpg",
  "output_path": "D:/output/compressed.jpg", 
  "quality": 85
}
```

##### `batch_compress_images`
批量压缩指定文件夹中的所有图片
```json
{
  "input_dir": "D:/1",
  "output_dir": "D:/output",
  "quality": 85
}
```

##### `convert_image_format`
转换图片格式
```json
{
  "input_path": "D:/input/image.png",
  "output_path": "D:/output/image.jpg"
}
```

##### `resize_image`  
调整图片尺寸
```json
{
  "input_path": "D:/input/image.jpg",
  "output_path": "D:/output/resized.jpg",
  "width": 800,
  "height": 600
}
```

#### 视频处理工具

##### `compress_video`
压缩单个视频文件
```json
{
  "input_path": "D:/input/video.mp4",
  "output_path": "D:/output/compressed.mp4",
  "crf": 23,
  "preset": "medium"
}
```

##### `batch_compress_videos`
批量压缩指定文件夹中的所有视频
```json
{
  "input_dir": "D:/videos", 
  "output_dir": "D:/output",
  "crf": 23,
  "preset": "medium"
}
```

##### `convert_video_format`
转换视频格式
```json
{
  "input_path": "D:/input/video.avi",
  "output_path": "D:/output/video.mp4"
}
```

##### `resize_video`
调整视频尺寸
```json
{
  "input_path": "D:/input/video.mp4",
  "output_path": "D:/output/resized.mp4",
  "width": 1280,
  "height": 720
}
```

#### 信息工具

##### `get_media_info`
获取媒体文件详细信息
```json
{
  "file_path": "D:/media/file.mp4"
}
```

##### `check_ffmpeg_status`
检查FFmpeg是否安装并可用
```json
{}
```

## 参数说明

### 图片压缩质量 (quality)
- 范围：1-100
- 数值越高，质量越好，文件越大
- 推荐值：80-90

### 视频压缩质量 (crf)  
- 范围：18-28
- 数值越小，质量越高，文件越大
- 推荐值：
  - 高质量：18-20
  - 平衡：21-24  
  - 小文件：25-28

### 视频压缩速度预设 (preset)
- `ultrafast`：最快速度，文件最大
- `superfast, veryfast, faster, fast`：速度递减，质量递增
- `medium`：平衡选择（默认）
- `slow, slower, veryslow`：速度最慢，质量最好

## 支持的文件格式

### 图片格式
- 输入：JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
- 输出：根据输出文件扩展名自动判断

### 视频格式
- 输入：MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- 输出：根据输出文件扩展名自动判断

## 使用示例

### 批量压缩图片
假设你有一个文件夹 `D:/1` 包含很多JPG图片，想要压缩后保存到 `D:/output`：

```python
# 使用MCP客户端调用
tool_call = {
    "name": "batch_compress_images",
    "arguments": {
        "input_dir": "D:/1",
        "output_dir": "D:/output", 
        "quality": 80
    }
}
```

### 视频格式转换
将AVI格式转换为MP4：

```python
tool_call = {
    "name": "convert_video_format",
    "arguments": {
        "input_path": "D:/video.avi",
        "output_path": "D:/output/video.mp4"
    }
}
```

## 错误处理

工具会自动处理常见错误：
- 输入文件不存在
- 输出目录不存在（会自动创建）
- FFmpeg命令执行失败
- 不支持的文件格式

## 注意事项

1. 确保有足够的磁盘空间用于输出文件
2. 大文件处理可能需要较长时间
3. 批量处理时会跳过无法处理的文件并在结果中报告
4. 输出路径中的目录会被自动创建

## 故障排除

### FFmpeg未找到
```
错误：FFmpeg 未安装或不可用
```
解决方案：
1. 确认FFmpeg已正确安装
2. 确认FFmpeg已添加到系统PATH
3. 在命令行运行 `ffmpeg -version` 验证

### 文件权限错误
确保Python有读取输入文件和写入输出目录的权限。

### 内存不足
对于大文件或大量文件，可能需要：
1. 增加系统内存
2. 分批处理文件
3. 调整FFmpeg参数

## 开发和扩展

项目结构：
```
ffmpeg-mcp/
├── ffmpeg_mcp.py      # 主要的MCP服务器代码
├── requirements.txt   # Python依赖
├── config.json       # MCP配置文件
├── start_server.py   # 服务器启动脚本
├── test_example.py   # 使用示例
└── README.md        # 说明文档
```

如需添加新功能，可以：
1. 在 `FFmpegProcessor` 类中添加新的处理方法
2. 在 `handle_list_tools()` 中注册新工具
3. 在 `handle_call_tool()` 中处理新工具的调用

## 许可证

MIT License - 可自由使用和修改。
