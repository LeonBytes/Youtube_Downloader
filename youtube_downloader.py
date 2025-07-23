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
    """获取视频信息"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'suppress_warnings': True  # 抑制所有警告
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', '未知标题'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', '未知上传者'),
                'formats': info.get('formats', []),
                'thumbnail': info.get('thumbnail', ''),
                'id': info.get('id', '')
            }
    except Exception as e:
        print(f"获取视频信息错误: {e}")
        return None

def download_video(url, resolution, progress_callback=None):
    """下载并处理视频"""
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
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, ""
    except Exception as e:
        return False, str(e)

def format_duration(seconds):
    """格式化视频时长"""
    if not seconds:
        return "未知"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"

def create_gui():
    """创建图形用户界面"""
    # 全局变量
    current_video = None
    download_thread = None
    # 创建主窗口
    root = tk.Tk()
    root.title(f"{TOOL_NAME} - YouTube高清下载工具")
    root.geometry("700x600")
    root.resizable(True, True)
    
    def parse_video(url):
        """解析视频URL"""
        nonlocal current_video
        
        url = url.strip()
        if not url:
            status_var.set("请输入YouTube URL")
            status_display.configure(style="Error.TLabel")
            return
            
        if not is_valid_youtube_url(url):
            status_var.set("无效的YouTube URL")
            status_display.configure(style="Error.TLabel")
            return
            
        status_var.set("正在获取视频信息...")
        status_display.configure(style="Error.TLabel")
        root.update()
        
        video_info = get_video_info(url)
        if not video_info:
            status_var.set("无法获取视频信息，请检查URL")
            status_display.configure(style="Error.TLabel")
            return
            
        current_video = video_info
        duration = format_duration(video_info['duration'])
        info_content = f"标题: {video_info['title']}\n上传者: {video_info['uploader']}\n时长: {duration}"
        
        # 更新信息文本框
        info_text.config(state=tk.NORMAL)
        info_text.delete(1.0, tk.END)
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        status_var.set("就绪 - 请选择分辨率并下载")
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
                thumbnail_canvas.create_text(160, 90, text="缩略图加载失败", fill="white", font=("Helvetica", 10))
        except Exception as e:
            print(f"缩略图处理错误: {e}")
            # 错误时清除缩略图
            thumbnail_canvas.delete("all")
            thumbnail_canvas.create_text(160, 90, text="缩略图加载失败", fill="white", font=("Helvetica", 10))
    
    def start_download():
        """开始下载视频"""
        nonlocal download_thread
        
        if not current_video:
            return
            
        resolution = res_var.get()
        res_map = {
            '最高质量': 10000,
            '2160p (4K)': 2160,
            '1440p (2K)': 1440,
            '1080p (HD)': 1080,
            '720p': 720,
            '480p': 480,
            '360p': 360
        }
        res_value = res_map.get(resolution, 1080)
        
        status_var.set("开始下载...")
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
                    update_progress
                )
                
                if success:
                    root.after(0, lambda: download_complete("下载完成!"))
                else:
                    root.after(0, lambda: download_error(f"错误: {error}"))
            except Exception as e:
                root.after(0, lambda: download_error(f"错误: {str(e)}"))
        
        download_thread = threading.Thread(target=download_task, daemon=True)
        download_thread.start()
    
    def update_progress(progress):
        """更新进度条"""
        progress_var.set(progress)
        status_var.set(f"下载中: {progress:.1f}%")
        status_display.configure(style="Error.TLabel")
    
    def download_complete(message):
        """下载完成处理"""
        progress_var.set(100)
        status_var.set(message)
        status_display.configure(style="Status.TLabel")
        download_button.config(state=tk.NORMAL)
        parse_button.config(state=tk.NORMAL)
        
        # 显示完成消息
        messagebox.showinfo("下载完成", "视频已成功下载到downloads文件夹")
    
    def download_error(message):
        """下载错误处理"""
        progress_var.set(0)
        status_var.set(message)
        status_display.configure(style="Error.TLabel")
        download_button.config(state=tk.NORMAL)
        parse_button.config(state=tk.NORMAL)
        
        # 显示错误消息
        messagebox.showerror("下载错误", message)
    
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
            status_var.set(f'无法打开文件夹: {str(e)}')
            status_display.configure(style="Error.TLabel")
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
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="YouTube高清视频下载工具", style="Title.TLabel")
    title_label.pack(pady=(0, 5))
    
    subtitle_label = ttk.Label(main_frame, text="基于开源技术，致力于知识共享", style="Subtitle.TLabel")
    subtitle_label.pack(pady=(0, 10))
    
    # 分隔线
    separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
    separator.pack(fill=tk.X, pady=10)
    
    # URL输入区域
    url_frame = ttk.Frame(main_frame)
    url_frame.pack(fill=tk.X, pady=5)
    
    url_label = ttk.Label(url_frame, text="视频URL:", width=10)
    url_label.pack(side=tk.LEFT, padx=(0, 5))
    
    url_var = tk.StringVar()
    url_entry = ttk.Entry(url_frame, textvariable=url_var, width=60)
    url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    parse_button = ttk.Button(url_frame, text="解析", command=lambda: parse_video(url_var.get()))
    parse_button.pack(side=tk.LEFT)
    
    # 视频信息区域
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill=tk.X, pady=5)
    
    info_label = ttk.Label(info_frame, text="视频信息:", width=10)
    info_label.pack(side=tk.LEFT, padx=(0, 5), anchor=tk.N)
    
    info_text = scrolledtext.ScrolledText(info_frame, width=70, height=4, font=("Helvetica", 9))
    info_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
    info_text.config(state=tk.DISABLED)
    
    # 缩略图区域
    thumbnail_frame = ttk.Frame(main_frame)
    thumbnail_frame.pack(fill=tk.X, pady=5)
    
    thumbnail_label = ttk.Label(thumbnail_frame, text="缩略图:", width=10)
    thumbnail_label.pack(side=tk.LEFT, padx=(0, 5), anchor=tk.N)
    
    thumbnail_image = None
    thumbnail_canvas = tk.Canvas(thumbnail_frame, width=320, height=180, bg="black")
    thumbnail_canvas.pack(side=tk.LEFT)
    
    # 分辨率选择区域
    res_frame = ttk.Frame(main_frame)
    res_frame.pack(fill=tk.X, pady=5)
    
    res_label = ttk.Label(res_frame, text="分辨率:", width=10)
    res_label.pack(side=tk.LEFT, padx=(0, 5))
    
    resolutions = ['最高质量', '2160p (4K)', '1440p (2K)', '1080p (HD)', '720p', '480p', '360p']
    res_var = tk.StringVar(value='1080p (HD)')
    res_combo = ttk.Combobox(res_frame, textvariable=res_var, values=resolutions, width=15)
    res_combo.pack(side=tk.LEFT)
    
    # 进度条区域
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=10)
    
    progress_label = ttk.Label(progress_frame, text="进度:")
    progress_label.pack(side=tk.LEFT, padx=(0, 5))
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=400)
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # 状态区域
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill=tk.X, pady=5)
    
    status_label = ttk.Label(status_frame, text="状态:", width=10)
    status_label.pack(side=tk.LEFT, padx=(0, 5))
    
    status_var = tk.StringVar(value="就绪")
    status_display = ttk.Label(status_frame, textvariable=status_var, style="Status.TLabel")
    status_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # 按钮区域
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    download_button = ttk.Button(button_frame, text="下载", state=tk.DISABLED, command=start_download)
    download_button.pack(side=tk.LEFT, padx=5)
    
    open_folder_button = ttk.Button(button_frame, text="打开下载文件夹", command=open_download_folder)
    open_folder_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = ttk.Button(button_frame, text="退出", command=root.destroy)
    exit_button.pack(side=tk.RIGHT, padx=5)
    
    # 版本信息
    version_frame = ttk.Frame(main_frame)
    version_frame.pack(fill=tk.X, pady=5)
    
    version_label = ttk.Label(version_frame, text=f"{TOOL_NAME} v{VERSION} | 开发者: {DEVELOPER}", 
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