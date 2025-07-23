# 隐藏弃用警告
import os
os.environ['YTDLP_NO_DEPRECATION_WARNING'] = '1'

import sys
import threading
import io
import yt_dlp
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageOps, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font

# 工具版本信息
TOOL_NAME = "知识解放者"
VERSION = "1.5.0"
DEVELOPER = "开源社区"

# 创建下载目录
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# 多语言资源
LANGUAGE = {
    'cn': {
        'title': "YouTube高清视频下载工具",
        'subtitle': "基于开源技术，致力于知识共享",
        'url_label': "视频URL:",
        'parse_button': "解析",
        'info_label': "视频信息:",
        'thumbnail_label': "缩略图:",
        'res_label': "分辨率:",
        'progress_label': "进度:",
        'status_label': "状态:",
        'download_button': "下载",
        'open_folder_button': "打开下载文件夹",
        'exit_button': "退出",
        'language_button': "English",
        'version': f"{TOOL_NAME} v{VERSION} | 开发者: {DEVELOPER}",
        'status_ready': "就绪",
        'resolutions': ['最高质量', '2160p (4K)', '1440p (2K)', '1080p (HD)', '720p', '480p', '360p'],
        'status_input_url': "请输入YouTube URL",
        'status_invalid_url': "无效的YouTube URL",
        'status_fetching': "正在获取视频信息...",
        'status_ready_download': "就绪 - 请选择分辨率并下载",
        'status_downloading': "开始下载...",
        'download_complete': "下载完成!",
        'download_error': "错误",
        'thumbnail_error': "缩略图加载失败",
        'folder_error': "无法打开文件夹: {error}",
        'info_title': "标题: {title}",
        'info_uploader': "上传者: {uploader}",
        'info_duration': "时长: {duration}",
        'unknown_title': "未知标题",
        'unknown_uploader': "未知上传者",
        'unknown_duration': "未知",
        'subtitle_label': "字幕:",
        'subtitle_none': "无字幕",
        'subtitle_download': "下载字幕",
        'subtitle_lang': "字幕语言:",
        'subtitle_all': "所有可用字幕",
        'subtitle_downloading': "正在下载字幕...",
        'subtitle_downloaded': "字幕已下载",
        'subtitle_no_subs': "该视频无可用字幕",
    },
    'en': {
        'title': "YouTube HD Video Downloader",
        'subtitle': "Based on open source technology, dedicated to knowledge sharing",
        'url_label': "Video URL:",
        'parse_button': "Parse",
        'info_label': "Video Info:",
        'thumbnail_label': "Thumbnail:",
        'res_label': "Resolution:",
        'progress_label': "Progress:",
        'status_label': "Status:",
        'download_button': "Download",
        'open_folder_button': "Open Download Folder",
        'exit_button': "Exit",
        'language_button': "中文",
        'version': f"{TOOL_NAME} v{VERSION} | Developer: {DEVELOPER}",
        'status_ready': "Ready",
        'resolutions': ['Best Quality', '2160p (4K)', '1440p (2K)', '1080p (HD)', '720p', '480p', '360p'],
        'status_input_url': "Please input YouTube URL",
        'status_invalid_url': "Invalid YouTube URL",
        'status_fetching': "Fetching video info...",
        'status_ready_download': "Ready - Please select resolution and download",
        'status_downloading': "Start downloading...",
        'download_complete': "Download Complete!",
        'download_error': "Error",
        'thumbnail_error': "Thumbnail load failed",
        'folder_error': "Cannot open folder: {error}",
        'info_title': "Title: {title}",
        'info_uploader': "Uploader: {uploader}",
        'info_duration': "Duration: {duration}",
        'unknown_title': "Unknown Title",
        'unknown_uploader': "Unknown Uploader",
        'unknown_duration': "Unknown",
        'subtitle_label': "Subtitles:",
        'subtitle_none': "No subtitles",
        'subtitle_download': "Download subtitles",
        'subtitle_lang': "Subtitle language:",
        'subtitle_all': "All available subtitles",
        'subtitle_downloading': "Downloading subtitles...",
        'subtitle_downloaded': "Subtitles downloaded",
        'subtitle_no_subs': "No subtitles available for this video",
    }
}

current_language = 'cn'  # 默认语言为中文

def is_valid_youtube_url(url):
    """验证是否为有效的YouTube URL"""
    parsed = urlparse(url)
    if parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be']:
        if parsed.path == '/watch' and 'v' in parse_qs(parsed.query):
            return True
        elif parsed.path.startswith('/embed/'):
            return True
        elif parsed.path.startswith('/shorts/'):
            return True
        elif parsed.netloc == 'youtu.be' and len(parsed.path) > 1:
            return True
    return False

def get_video_info(url):
    """获取视频信息，包括字幕"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'suppress_warnings': True,  # 抑制所有警告
        'listsubtitles': True,      # 获取字幕信息
        'skip_download': True       # 不下载视频
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 获取所有可用字幕
            subtitles = {}
            if info.get('subtitles'):
                subtitles.update(info['subtitles'])
            if info.get('automatic_captions'):
                subtitles.update(info['automatic_captions'])
            
            # 创建字幕语言列表
            subtitle_langs = []
            for lang_code, sub_info in subtitles.items():
                # 获取语言名称
                lang_name = lang_code
                if len(sub_info) > 0:
                    lang_name = sub_info[0].get('name', lang_code)
                subtitle_langs.append({
                    'code': lang_code,
                    'name': lang_name
                })
            
            # 按语言名称排序
            subtitle_langs.sort(key=lambda x: x['name'])
            
            return {
                'title': info.get('title', LANGUAGE[current_language]['unknown_title']),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', LANGUAGE[current_language]['unknown_uploader']),
                'formats': info.get('formats', []),
                'thumbnail': info.get('thumbnail', ''),
                'id': info.get('id', ''),
                'subtitles': subtitle_langs
            }
    except Exception as e:
        print(f"获取视频信息错误: {e}")
        return None

def download_video(url, resolution, download_subs=False, sub_lang=None, progress_callback=None):
    """下载并处理视频和字幕"""
    def progress_hook(d):
        if progress_callback and d['status'] == 'downloading':
            progress = d.get('_percent_str', '0%').strip('%')
            try:
                progress_callback(float(progress))
            except:
                pass
    
    # 选择最佳格式
    format_selection = f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]'
    
    # 下载选项
    ydl_opts = {
        'format': format_selection,
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'quiet': True,
        'no_warnings': True,
        'suppress_warnings': True  # 抑制所有警告
    }
    
    # 添加字幕下载选项
    if download_subs:
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = [sub_lang] if sub_lang != 'all' else ['all']
        ydl_opts['subtitlesformat'] = 'srt'
        ydl_opts['writeautomaticsub'] = True  # 包括自动生成的字幕
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, ""
    except Exception as e:
        return False, str(e)

def format_duration(seconds):
    """格式化视频时长"""
    if not seconds:
        return LANGUAGE[current_language]['unknown_duration']
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"

def create_gui():
    """创建图形用户界面"""
    # 全局变量
    global current_language
    current_video = None
    download_thread = None
    # 创建主窗口
    root = tk.Tk()
    root.title(f"{TOOL_NAME} - {LANGUAGE['cn']['title']}")
    root.geometry("700x650")  # 增加高度以容纳字幕选项
    root.resizable(True, True)
    
    def update_ui_language():
        """更新UI语言"""
        lang = LANGUAGE[current_language]
        root.title(f"{TOOL_NAME} - {lang['title']}")
        title_label.config(text=lang['title'])
        subtitle_label.config(text=lang['subtitle'])
        url_label.config(text=lang['url_label'])
        parse_button.config(text=lang['parse_button'])
        info_label.config(text=lang['info_label'])
        thumbnail_label.config(text=lang['thumbnail_label'])
        res_label.config(text=lang['res_label'])
        progress_label.config(text=lang['progress_label'])
        status_label.config(text=lang['status_label'])
        download_button.config(text=lang['download_button'])
        open_folder_button.config(text=lang['open_folder_button'])
        exit_button.config(text=lang['exit_button'])
        language_button.config(text=lang['language_button'])
        version_label.config(text=lang['version'])
        subtitle_label.config(text=lang['subtitle_label'])
        subtitle_download_var.set(lang['subtitle_download'])
        subtitle_lang_label.config(text=lang['subtitle_lang'])
        
        # 更新分辨率下拉框
        res_combo['values'] = lang['resolutions']
        res_combo.set(lang['resolutions'][3])  # 默认选择1080p/HD
        
        # 更新状态
        status_var.set(lang['status_ready'])
        status_display.configure(style="Status.TLabel")
        
        # 如果有视频信息，更新信息显示
        if current_video:
            update_video_info_display()
    
    def update_video_info_display():
        """更新视频信息显示"""
        if not current_video:
            return
            
        duration = format_duration(current_video['duration'])
        lang = LANGUAGE[current_language]
        info_content = "\n".join([
            lang['info_title'].format(title=current_video['title']),
            lang['info_uploader'].format(uploader=current_video['uploader']),
            lang['info_duration'].format(duration=duration)
        ])
        
        info_text.config(state=tk.NORMAL)
        info_text.delete(1.0, tk.END)
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # 更新字幕语言下拉框
        subtitle_lang_combo['values'] = [lang['name'] for lang in current_video['subtitles']]
        if current_video['subtitles']:
            subtitle_lang_combo.set(LANGUAGE[current_language]['subtitle_all'])
            subtitle_download_check.config(state=tk.NORMAL)
            subtitle_lang_combo.config(state='readonly')
        else:
            subtitle_lang_combo.set(LANGUAGE[current_language]['subtitle_none'])
            subtitle_download_check.config(state=tk.DISABLED)
            subtitle_lang_combo.config(state=tk.DISABLED)
    
    def toggle_language():
        """切换语言"""
        global current_language
        current_language = 'en' if current_language == 'cn' else 'cn'
        update_ui_language()
    
    def parse_video(url):
        """解析视频URL"""
        nonlocal current_video
        
        url = url.strip()
        if not url:
            status_var.set(LANGUAGE[current_language]['status_input_url'])
            status_display.configure(style="Error.TLabel")
            return
            
        if not is_valid_youtube_url(url):
            status_var.set(LANGUAGE[current_language]['status_invalid_url'])
            status_display.configure(style="Error.TLabel")
            return
            
        status_var.set(LANGUAGE[current_language]['status_fetching'])
        status_display.configure(style="Error.TLabel")
        root.update()
        
        video_info = get_video_info(url)
        if not video_info:
            status_var.set(LANGUAGE[current_language]['status_invalid_url'])
            status_display.configure(style="Error.TLabel")
            return
            
        current_video = video_info
        update_video_info_display()
        
        status_var.set(LANGUAGE[current_language]['status_ready_download'])
        status_display.configure(style="Status.TLabel")
        download_button.config(state=tk.NORMAL)
        
        # 加载并显示缩略图
        load_thumbnail(video_info['thumbnail'], video_info['id'])
    
    def load_thumbnail(thumbnail_url, video_id):
        """加载并显示缩略图"""
        try:
            response = requests.get(thumbnail_url, timeout=10)
            if response.status_code == 200:
                # 使用PIL处理图像
                img = Image.open(io.BytesIO(response.content))
                
                # 转换为RGB模式（解决RGBA问题）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 设置最大尺寸并保持宽高比
                max_size = (320, 180)
                img.thumbnail(max_size, Image.LANCZOS)
                
                # 创建带有边框的图像（如果尺寸不匹配）
                if img.size[0] < max_size[0] or img.size[1] < max_size[1]:
                    # 计算边框大小
                    delta_w = max_size[0] - img.size[0]
                    delta_h = max_size[1] - img.size[1]
                    padding = (delta_w//2, delta_h//2, delta_w - (delta_w//2), delta_h - (delta_h//2))
                    
                    # 添加黑色边框
                    img = ImageOps.expand(img, padding, fill='black')
                
                # 转换为Tkinter图像
                nonlocal thumbnail_image
                thumbnail_image = ImageTk.PhotoImage(img)
                
                # 更新画布
                thumbnail_canvas.delete("all")
                thumbnail_canvas.create_image(0, 0, anchor=tk.NW, image=thumbnail_image)
            else:
                print(f"无法下载缩略图: HTTP {response.status_code}")
                thumbnail_canvas.delete("all")
                thumbnail_canvas.create_text(160, 90, text=LANGUAGE[current_language]['thumbnail_error'], 
                                           fill="white", font=("Helvetica", 10))
        except Exception as e:
            print(f"缩略图处理错误: {e}")
            # 错误时清除缩略图
            thumbnail_canvas.delete("all")
            thumbnail_canvas.create_text(160, 90, text=LANGUAGE[current_language]['thumbnail_error'], 
                                       fill="white", font=("Helvetica", 10))
    
    def start_download():
        """开始下载视频和字幕"""
        nonlocal download_thread
        
        if not current_video:
            return
            
        resolution = res_var.get()
        res_map = {
            LANGUAGE[current_language]['resolutions'][0]: 10000,   # 最高质量/Best Quality
            LANGUAGE[current_language]['resolutions'][1]: 2160,   # 2160p (4K)
            LANGUAGE[current_language]['resolutions'][2]: 1440,   # 1440p (2K)
            LANGUAGE[current_language]['resolutions'][3]: 1080,   # 1080p (HD)
            LANGUAGE[current_language]['resolutions'][4]: 720,     # 720p
            LANGUAGE[current_language]['resolutions'][5]: 480,     # 480p
            LANGUAGE[current_language]['resolutions'][6]: 360      # 360p
        }
        res_value = res_map.get(resolution, 1080)
        
        # 检查是否下载字幕
        download_subs = subtitle_download_var.get() == 1
        sub_lang = None
        
        if download_subs:
            selected_lang_name = subtitle_lang_var.get()
            if selected_lang_name == LANGUAGE[current_language]['subtitle_all']:
                sub_lang = 'all'  # 下载所有字幕
            else:
                # 根据选择的语言名称查找对应的语言代码
                for lang in current_video['subtitles']:
                    if lang['name'] == selected_lang_name:
                        sub_lang = lang['code']
                        break
                
                if not sub_lang:
                    status_var.set(f"{LANGUAGE[current_language]['subtitle_no_subs']}")
                    status_display.configure(style="Error.TLabel")
                    return
            
            status_var.set(f"{LANGUAGE[current_language]['status_downloading']} - {LANGUAGE[current_language]['subtitle_downloading']}")
        else:
            status_var.set(LANGUAGE[current_language]['status_downloading'])
        
        status_display.configure(style="Error.TLabel")
        download_button.config(state=tk.DISABLED)
        parse_button.config(state=tk.DISABLED)
        progress_var.set(0)
        root.update()
        
        # 在单独的线程中下载
        def download_task():
            try:
                success, error = download_video(
                    url_var.get(), 
                    res_value,
                    download_subs,
                    sub_lang,
                    update_progress
                )
                
                if success:
                    root.after(0, lambda: download_complete(LANGUAGE[current_language]['download_complete']))
                else:
                    root.after(0, lambda: download_error(f"{LANGUAGE[current_language]['download_error']}: {error}"))
            except Exception as e:
                root.after(0, lambda: download_error(f"{LANGUAGE[current_language]['download_error']}: {str(e)}"))
        
        download_thread = threading.Thread(target=download_task, daemon=True)
        download_thread.start()
    
    def update_progress(progress):
        """更新进度条"""
        progress_var.set(progress)
        base_status = LANGUAGE[current_language]['status_downloading']
        if subtitle_download_var.get() == 1:
            base_status += f" - {LANGUAGE[current_language]['subtitle_downloading']}"
        status_var.set(f"{base_status}: {progress:.1f}%")
        status_display.configure(style="Error.TLabel")
    
    def download_complete(message):
        """下载完成处理"""
        progress_var.set(100)
        status_var.set(message)
        if subtitle_download_var.get() == 1:
            status_var.set(f"{message} {LANGUAGE[current_language]['subtitle_downloaded']}")
        status_display.configure(style="Status.TLabel")
        download_button.config(state=tk.NORMAL)
        parse_button.config(state=tk.NORMAL)
        
        # 显示完成消息
        msg = LANGUAGE[current_language]['download_complete']
        if subtitle_download_var.get() == 1:
            msg += f"\n{LANGUAGE[current_language]['subtitle_downloaded']}"
        messagebox.showinfo(message, msg)
    
    def download_error(message):
        """下载错误处理"""
        progress_var.set(0)
        status_var.set(message)
        status_display.configure(style="Error.TLabel")
        download_button.config(state=tk.NORMAL)
        parse_button.config(state=tk.NORMAL)
        
        # 显示错误消息
        messagebox.showerror(LANGUAGE[current_language]['download_error'], message)
    
    def open_download_folder():
        """打开下载文件夹"""
        download_path = os.path.abspath('downloads')
        try:
            if sys.platform == 'win32':
                os.startfile(download_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{download_path}"')
            else:
                os.system(f'xdg-open "{download_path}"')
        except Exception as e:
            status_var.set(LANGUAGE[current_language]['folder_error'].format(error=str(e)))
            status_display.configure(style="Error.TLabel")
    
    def toggle_subtitle_options():
        """切换字幕选项状态"""
        if subtitle_download_var.get() == 1 and current_video and current_video['subtitles']:
            subtitle_lang_combo.config(state='readonly')
        else:
            subtitle_lang_combo.config(state=tk.DISABLED)
    
    # 绑定回车键到解析按钮
    root.bind('<Return>', lambda event: parse_video(url_var.get()))
    
    # 设置主题 - 修改为您的实际路径
    theme_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Azure-ttk-theme")
    theme_path = os.path.join(theme_dir, "azure.tcl")
    
    try:
        if os.path.exists(theme_path):
            root.tk.call("source", theme_path)
            root.tk.call("set_theme", "dark")
            print("成功加载Azure主题")
        else:
            print(f"未找到主题文件: {theme_path}")
    except Exception as e:
        print(f"加载主题错误: {e}")
    
    # 创建样式
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 10))
    style.configure("TLabel", font=("Helvetica", 9))
    style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
    style.configure("Subtitle.TLabel", font=("Helvetica", 10), foreground="yellow")
    style.configure("Status.TLabel", font=("Helvetica", 9), foreground="green")
    style.configure("Error.TLabel", font=("Helvetica", 9), foreground="red")
    style.configure("TCheckbutton", font=("Helvetica", 9))
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题栏框架 - 包含标题和语言切换按钮
    title_bar_frame = ttk.Frame(main_frame)
    title_bar_frame.pack(fill=tk.X, pady=(0, 5))
    
    # 标题在左侧
    title_label = ttk.Label(title_bar_frame, text=LANGUAGE[current_language]['title'], style="Title.TLabel")
    title_label.pack(side=tk.LEFT)
    
    # 语言切换按钮在右上角
    language_button = ttk.Button(title_bar_frame, text=LANGUAGE[current_language]['language_button'], 
                               command=toggle_language, width=8)
    language_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    # 副标题
    subtitle_label = ttk.Label(main_frame, text=LANGUAGE[current_language]['subtitle'], style="Subtitle.TLabel")
    subtitle_label.pack(pady=(0, 10))
    
    # 分隔线
    separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
    separator.pack(fill=tk.X, pady=10)
    
    # URL输入区域
    url_frame = ttk.Frame(main_frame)
    url_frame.pack(fill=tk.X, pady=5)
    
    url_label = ttk.Label(url_frame, text=LANGUAGE[current_language]['url_label'], width=10)
    url_label.pack(side=tk.LEFT, padx=(0, 5))
    
    url_var = tk.StringVar()
    url_entry = ttk.Entry(url_frame, textvariable=url_var, width=60)
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    parse_button = ttk.Button(url_frame, text=LANGUAGE[current_language]['parse_button'], 
                            command=lambda: parse_video(url_var.get()))
    parse_button.pack(side=tk.LEFT)
    
    # 视频信息区域
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill=tk.X, pady=5)
    
    info_label = ttk.Label(info_frame, text=LANGUAGE[current_language]['info_label'], width=10)
    info_label.pack(side=tk.LEFT, padx=(0, 5), anchor=tk.N)
    
    info_text = scrolledtext.ScrolledText(info_frame, width=70, height=4, font=("Helvetica", 9))
    info_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
    info_text.config(state=tk.DISABLED)
    
    # 缩略图区域
    thumbnail_frame = ttk.Frame(main_frame)
    thumbnail_frame.pack(fill=tk.X, pady=5)
    
    thumbnail_label = ttk.Label(thumbnail_frame, text=LANGUAGE[current_language]['thumbnail_label'], width=10)
    thumbnail_label.pack(side=tk.LEFT, padx=(0, 5), anchor=tk.N)
    
    thumbnail_image = None
    thumbnail_canvas = tk.Canvas(thumbnail_frame, width=320, height=180, bg="black")
    thumbnail_canvas.pack(side=tk.LEFT)
    
    # 分辨率选择区域
    res_frame = ttk.Frame(main_frame)
    res_frame.pack(fill=tk.X, pady=5)
    
    res_label = ttk.Label(res_frame, text=LANGUAGE[current_language]['res_label'], width=10)
    res_label.pack(side=tk.LEFT, padx=(0, 5))
    
    resolutions = LANGUAGE[current_language]['resolutions']
    res_var = tk.StringVar(value=resolutions[3])  # 默认选择1080p/HD
    res_combo = ttk.Combobox(res_frame, textvariable=res_var, values=resolutions, width=15)
    res_combo.pack(side=tk.LEFT)
    
    # 字幕选项区域
    subtitle_frame = ttk.Frame(main_frame)
    subtitle_frame.pack(fill=tk.X, pady=5)
    
    subtitle_label = ttk.Label(subtitle_frame, text=LANGUAGE[current_language]['subtitle_label'], width=10)
    subtitle_label.pack(side=tk.LEFT, padx=(0, 5))
    
    # 字幕下载复选框
    subtitle_download_var = tk.IntVar(value=0)
    subtitle_download_check = ttk.Checkbutton(
        subtitle_frame, 
        text=LANGUAGE[current_language]['subtitle_download'], 
        variable=subtitle_download_var,
        command=toggle_subtitle_options
    )
    subtitle_download_check.pack(side=tk.LEFT, padx=(0, 10))
    
    # 字幕语言标签
    subtitle_lang_label = ttk.Label(subtitle_frame, text=LANGUAGE[current_language]['subtitle_lang'])
    subtitle_lang_label.pack(side=tk.LEFT, padx=(0, 5))
    
    # 字幕语言下拉框
    subtitle_lang_var = tk.StringVar()
    subtitle_lang_combo = ttk.Combobox(
        subtitle_frame, 
        textvariable=subtitle_lang_var, 
        width=60,
        state=tk.DISABLED
    )
    subtitle_lang_combo.pack(side=tk.LEFT)
    subtitle_lang_var.set(LANGUAGE[current_language]['subtitle_none'])
    
    # 进度条区域
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=10)
    
    progress_label = ttk.Label(progress_frame, text=LANGUAGE[current_language]['progress_label'])
    progress_label.pack(side=tk.LEFT, padx=(0, 5))
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=400)
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # 状态区域
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    status_label = ttk.Label(status_frame, text=LANGUAGE[current_language]['status_label'], width=10)
    status_label.pack(side=tk.LEFT, padx=(0, 5))
    
    status_var = tk.StringVar(value=LANGUAGE[current_language]['status_ready'])
    status_display = ttk.Label(status_frame, textvariable=status_var, style="Status.TLabel")
    status_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # 按钮区域 - 底部按钮
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    # 左侧按钮组
    left_button_frame = ttk.Frame(button_frame)
    left_button_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    download_button = ttk.Button(left_button_frame, text=LANGUAGE[current_language]['download_button'], 
                               state=tk.DISABLED, command=start_download)
    download_button.pack(side=tk.LEFT, padx=5)
    
    open_folder_button = ttk.Button(left_button_frame, text=LANGUAGE[current_language]['open_folder_button'], 
                                  command=open_download_folder)
    open_folder_button.pack(side=tk.LEFT, padx=5)
    
    # 右侧按钮组
    right_button_frame = ttk.Frame(button_frame)
    right_button_frame.pack(side=tk.RIGHT)
    
    exit_button = ttk.Button(right_button_frame, text=LANGUAGE[current_language]['exit_button'], command=root.destroy)
    exit_button.pack(side=tk.RIGHT, padx=5)
    
    # 版本信息
    version_frame = ttk.Frame(main_frame)
    version_frame.pack(fill=tk.X, pady=5)
    
    version_label = ttk.Label(version_frame, text=LANGUAGE[current_language]['version'], 
                            font=("Helvetica", 8), foreground="gray")
    version_label.pack(side=tk.LEFT)
    
    # Python版本警告
    py_warning_var = tk.StringVar()
    py_warning_label = ttk.Label(version_frame, textvariable=py_warning_var, 
                               font=("Helvetica", 8), foreground="red")
    py_warning_label.pack(side=tk.RIGHT)
    
    # 检查Python版本并显示警告
    if sys.version_info < (3, 8):
        py_warning_var.set(f"警告: 使用Python {sys.version.split()[0]} (建议升级到3.8+)")
    
    # 启动主循环
    root.mainloop()

if __name__ == '__main__':
    create_gui()
