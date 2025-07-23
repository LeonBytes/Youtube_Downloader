# YouTube高清视频下载工具

一个基于Python的YouTube视频和字幕下载工具，具有现代化的图形用户界面，支持多种分辨率选择和字幕下载功能。

## ✨ 主要特性

- 🎥 **多分辨率下载**：支持360p到4K的各种分辨率选择
- 📝 **字幕下载**：支持手动和自动生成的字幕，可选择多种语言
- 🖼️ **缩略图预览**：自动加载并显示视频缩略图
- 🌍 **双语界面**：支持中文和英文界面切换
- 🎨 **现代UI**：采用Azure深色主题，界面美观
- 📁 **便捷管理**：一键打开下载文件夹
- ⚡ **实时进度**：显示下载进度和状态信息
- 🔄 **多种下载模式**：支持仅视频、仅字幕、视频+字幕三种模式

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows/macOS/Linux

### 安装步骤

1. **克隆项目**
```bash
git clone <your-repo-url>
cd YouTubeDownloader
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行程序**
```bash
cd src
python youtube_multisub.py
```

## 📦 项目结构

```
YouTubeDownloader/
├── src/
│   ├── youtube_multisub.py      # 完整版本（推荐使用）
│   ├── youtube_Zh_Eng.py        # 双语版本
│   ├── youtube_downloader.py    # 基础版本
│   └── requirements.txt         # 依赖列表
├── downloads/                   # 下载文件存放目录
├── Azure-ttk-theme/            # UI主题文件
│   ├── azure.tcl               # 主题配置
│   └── theme/                  # 主题资源文件
└── README.md                   # 项目说明文档
```

## 🎯 使用说明

### 基本操作

1. **输入URL**：在输入框中粘贴YouTube视频链接
2. **解析视频**：点击"解析"按钮获取视频信息
3. **选择分辨率**：从下拉菜单中选择所需分辨率
4. **选择字幕**（可选）：
   - 从字幕列表中选择需要的语言
   - 支持多选（Ctrl+点击）
   - 可使用"全选"和"清空"按钮
5. **开始下载**：选择下载模式并点击相应按钮

### 下载模式

- **下载视频**：仅下载视频文件
- **仅下载字幕**：仅下载选中的字幕文件
- **下载视频和字幕**：同时下载视频和字幕

### 支持的URL格式

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

## 🛠️ 技术栈

- **yt-dlp**：YouTube视频下载核心库
- **tkinter**：GUI图形界面框架
- **Pillow (PIL)**：图像处理和缩略图显示
- **requests**：HTTP请求处理
- **Azure-ttk-theme**：现代化UI主题

## 📋 依赖说明

### 核心依赖
- `yt-dlp`：最新的YouTube下载工具，youtube-dl的活跃分支
- `Pillow`：Python图像处理库
- `requests`：HTTP请求库

### 可选依赖
- `ffmpeg`：视频格式转换（建议安装以获得最佳体验）

## ⚙️ 高级配置

### FFmpeg安装（推荐）

为了获得最佳的视频处理体验，建议安装FFmpeg：

**Windows:**
```bash
# 使用Chocolatey
choco install ffmpeg

# 或下载预编译版本并添加到PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

### 自定义下载路径

默认下载路径为项目根目录下的`downloads`文件夹。如需修改，可编辑源代码中的路径设置。

## 🎨 界面预览

- 深色主题界面，现代美观
- 实时缩略图预览
- 多语言字幕选择
- 进度条显示下载状态
- 中英文界面切换

## 📄 版本历史

- **v1.6.0** (youtube_multisub.py)：完整版本，支持多字幕下载
- **v1.5.0** (youtube_Zh_Eng.py)：添加中英文界面切换
- **v1.0.0** (youtube_downloader.py)：基础功能版本

## ⚠️ 注意事项

1. **合法使用**：请遵守YouTube服务条款，仅下载您有权下载的内容
2. **教育目的**：本工具主要用于教育和学习目的
3. **网络要求**：需要稳定的网络连接以获取视频信息和下载内容
4. **Python版本**：建议使用Python 3.8及以上版本

## 🐛 故障排除

### 常见问题

1. **下载失败**：
   - 检查网络连接
   - 确认视频URL有效
   - 尝试更换分辨率

2. **字幕不可用**：
   - 部分视频可能没有字幕
   - 检查视频是否支持所选语言

3. **主题加载失败**：
   - 确认Azure-ttk-theme文件夹存在
   - 检查主题文件路径是否正确

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📜 许可证

本项目基于开源协议，仅供学习和教育使用。

## 👨‍💻 开发者

知识解放者 - 开源社区

---

**免责声明**：请合理使用本工具，遵守相关法律法规和平台服务条款。开发者不承担因使用本工具而产生的任何法律责任。