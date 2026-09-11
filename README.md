# YouTube 高清视频下载工具 / YouTube HD Video Downloader

[中文](#中文说明) · [English](#english)

一款基于 Python 和 yt-dlp 的桌面 YouTube 视频与字幕下载工具，提供图形界面、分辨率选择、字幕下载和中英文界面。

A desktop YouTube video and subtitle downloader built with Python and yt-dlp. It provides a graphical interface, resolution selection, subtitle downloads, and Chinese/English UI support.

## 中文说明

### 功能特性

- 支持从 360p 到 4K 的多种分辨率
- 支持人工字幕和自动生成字幕，并可选择语言
- 支持单独下载 MP3、M4A、WAV 或原始最佳音频
- 自动加载视频信息和缩略图
- 支持中文与英文界面切换
- 显示实时下载进度
- 支持仅下载视频、仅下载字幕或同时下载
- 支持 Windows、macOS 和 Linux

### 环境要求

- Python 3.8 或更高版本
- FFmpeg（推荐，用于合并视频和音频）

### 安装

```bash
git clone https://github.com/LeonBytes/Youtube_Downloader.git
cd Youtube_Downloader
python -m pip install -r requirements.txt
```

安装 FFmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows（Chocolatey）
choco install ffmpeg
```

### 运行

推荐运行支持多字幕的完整版本：

```bash
python youtube_multisub.py
```

仅下载音频：

```bash
python youtube_audio.py
```

其他版本：

```bash
python youtube_Zh_Eng.py     # 中英文界面版本
python youtube_sub.py        # 字幕版本
python youtube_downloader.py # 基础版本
```

### 使用方法

1. 粘贴 YouTube 视频链接。
2. 点击“解析”获取视频信息。
3. 选择需要的分辨率。
4. 根据需要选择字幕语言和下载模式。
5. 开始下载；文件默认保存在 `downloads` 文件夹中。

支持常见的 `youtube.com/watch`、`youtu.be`、`youtube.com/embed` 和 `youtube.com/shorts` 链接。

### 技术栈

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)：媒体信息解析与下载
- tkinter：桌面图形界面
- Pillow：缩略图处理
- Requests：网络请求
- FFmpeg：视频和音频合并

### 合法使用说明

本项目仅用于下载以下内容：用户本人拥有的内容、已获得版权所有者明确授权的内容、公共领域内容，或适用法律明确允许下载的内容。使用者有责任确认自己拥有下载、保存和使用相关内容的合法权利。

本项目与 YouTube 或 Google 没有关联，也未获得其认可。YouTube 是 Google LLC 的商标。使用本软件仍可能受到 YouTube 服务条款及当地法律的限制。请勿使用本项目绕过数字版权管理、付费限制、访问控制、地区限制或其他技术保护措施。

## English

### Features

- Multiple resolutions from 360p to 4K
- Manual and automatically generated subtitles with language selection
- Audio-only downloads as MP3, M4A, WAV, or the best original format
- Automatic video metadata and thumbnail loading
- Chinese and English user interfaces
- Real-time download progress
- Video-only, subtitle-only, and combined download modes
- Windows, macOS, and Linux support

### Requirements

- Python 3.8 or later
- FFmpeg (recommended for merging video and audio)

### Installation

```bash
git clone https://github.com/LeonBytes/Youtube_Downloader.git
cd Youtube_Downloader
python -m pip install -r requirements.txt
```

Install FFmpeg:

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### Running the application

Run the full version with multi-subtitle support:

```bash
python youtube_multisub.py
```

Download audio only:

```bash
python youtube_audio.py
```

Other versions:

```bash
python youtube_Zh_Eng.py     # Chinese/English UI version
python youtube_sub.py        # Subtitle-enabled version
python youtube_downloader.py # Basic version
```

### Usage

1. Paste a YouTube video URL.
2. Select **Parse** to retrieve the video information.
3. Choose a resolution.
4. Select subtitle languages and a download mode if needed.
5. Start the download. Files are saved to the `downloads` directory by default.

Common `youtube.com/watch`, `youtu.be`, `youtube.com/embed`, and `youtube.com/shorts` links are supported.

### Technology

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for media extraction and downloading
- tkinter for the desktop interface
- Pillow for thumbnail processing
- Requests for HTTP requests
- FFmpeg for merging video and audio

### Responsible use

This project is intended only for content that you own, content for which you have explicit permission from the copyright holder, public-domain content, or content whose downloading is otherwise permitted by applicable law. You are responsible for confirming that you have the legal right to download, retain, and use the relevant content.

This project is not affiliated with or endorsed by YouTube or Google. YouTube is a trademark of Google LLC. Use of this software may still be restricted by YouTube's Terms of Service and applicable local law. Do not use this project to circumvent digital rights management, paywalls, access controls, geographic restrictions, or other technical protection measures.

## Contributing / 参与贡献

欢迎提交 Issue 和 Pull Request。Bug reports and pull requests are welcome.

## License / 许可证

本项目采用 [MIT License](LICENSE) 开源。

This project is licensed under the [MIT License](LICENSE).
