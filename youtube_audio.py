"""A small GUI for downloading audio from YouTube with yt-dlp."""

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlparse

import yt_dlp


def is_valid_youtube_url(url):
    """Return True for common YouTube video URL hosts."""
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    return parsed.scheme in {"http", "https"} and host in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    }


class AudioDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Downloader / YouTube 音频下载器")
        self.root.geometry("620x320")
        self.root.minsize(560, 300)

        self.url_var = tk.StringVar()
        self.format_var = tk.StringVar(value="mp3")
        self.quality_var = tk.StringVar(value="192")
        self.output_var = tk.StringVar(
            value=os.path.abspath(os.path.join(os.getcwd(), "downloads"))
        )
        self.status_var = tk.StringVar(value="Ready / 就绪")
        self.progress_var = tk.DoubleVar(value=0)

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="YouTube URL:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=8
        )
        ttk.Entry(frame, textvariable=self.url_var).grid(
            row=0, column=1, columnspan=2, sticky=tk.EW, pady=8
        )

        ttk.Label(frame, text="Format / 格式:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=8
        )
        format_box = ttk.Combobox(
            frame,
            textvariable=self.format_var,
            values=("mp3", "m4a", "wav", "best"),
            state="readonly",
            width=12,
        )
        format_box.grid(row=1, column=1, sticky=tk.W, pady=8)
        format_box.bind("<<ComboboxSelected>>", self.update_quality_state)

        ttk.Label(frame, text="Quality / 音质:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 10), pady=8
        )
        self.quality_box = ttk.Combobox(
            frame,
            textvariable=self.quality_var,
            values=("320", "256", "192", "128", "96"),
            state="readonly",
            width=12,
        )
        self.quality_box.grid(row=2, column=1, sticky=tk.W, pady=8)
        ttk.Label(frame, text="kbps").grid(row=2, column=2, sticky=tk.W, pady=8)

        ttk.Label(frame, text="Save to / 保存到:").grid(
            row=3, column=0, sticky=tk.W, padx=(0, 10), pady=8
        )
        ttk.Entry(frame, textvariable=self.output_var).grid(
            row=3, column=1, sticky=tk.EW, pady=8
        )
        ttk.Button(frame, text="Browse / 浏览", command=self.choose_output).grid(
            row=3, column=2, padx=(8, 0), pady=8
        )

        ttk.Progressbar(
            frame, variable=self.progress_var, maximum=100
        ).grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady=(14, 6))
        ttk.Label(frame, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=3, sticky=tk.W
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(18, 0))
        self.download_button = ttk.Button(
            button_frame,
            text="Download Audio / 下载音频",
            command=self.start_download,
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame,
            text="Open Folder / 打开文件夹",
            command=self.open_output_folder,
        ).pack(side=tk.LEFT, padx=5)

    def update_quality_state(self, _event=None):
        state = "disabled" if self.format_var.get() == "best" else "readonly"
        self.quality_box.configure(state=state)

    def choose_output(self):
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)

    def start_download(self):
        url = self.url_var.get().strip()
        if not is_valid_youtube_url(url):
            messagebox.showerror(
                "Invalid URL / 链接无效", "Please enter a valid YouTube URL."
            )
            return

        output_dir = os.path.abspath(os.path.expanduser(self.output_var.get().strip()))
        if not output_dir:
            messagebox.showerror("Error / 错误", "Please select an output folder.")
            return

        os.makedirs(output_dir, exist_ok=True)
        self.progress_var.set(0)
        self.status_var.set("Starting download... / 正在开始下载…")
        self.download_button.configure(state=tk.DISABLED)

        threading.Thread(
            target=self.download_audio,
            args=(url, output_dir, self.format_var.get(), self.quality_var.get()),
            daemon=True,
        ).start()

    def download_audio(self, url, output_dir, audio_format, quality):
        options = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
        }

        if audio_format != "best":
            options["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": quality,
                }
            ]

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            self.root.after(0, self.download_complete)
        except Exception as error:
            self.root.after(0, self.download_failed, str(error))

    def progress_hook(self, data):
        if data.get("status") == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                percent = downloaded * 100 / total
                self.root.after(0, self.progress_var.set, percent)
                self.root.after(
                    0,
                    self.status_var.set,
                    f"Downloading / 正在下载: {percent:.1f}%",
                )
        elif data.get("status") == "finished":
            self.root.after(
                0,
                self.status_var.set,
                "Converting audio... / 正在转换音频…",
            )

    def download_complete(self):
        self.progress_var.set(100)
        self.status_var.set("Download complete / 下载完成")
        self.download_button.configure(state=tk.NORMAL)
        messagebox.showinfo(
            "Complete / 完成", "Audio download completed. / 音频下载完成。"
        )

    def download_failed(self, error):
        self.status_var.set("Download failed / 下载失败")
        self.download_button.configure(state=tk.NORMAL)
        messagebox.showerror("Download failed / 下载失败", error)

    def open_output_folder(self):
        output_dir = os.path.abspath(os.path.expanduser(self.output_var.get().strip()))
        os.makedirs(output_dir, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(output_dir)
        elif sys.platform == "darwin":
            subprocess.run(["open", output_dir], check=False)
        else:
            subprocess.run(["xdg-open", output_dir], check=False)


if __name__ == "__main__":
    app_root = tk.Tk()
    AudioDownloader(app_root)
    app_root.mainloop()
