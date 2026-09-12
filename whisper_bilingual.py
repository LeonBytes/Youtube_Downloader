"""Transcribe English media locally and create an English-Chinese study file."""

import csv
import html
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk


TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-zh"


def timestamp(seconds):
    total = max(0, int(seconds))
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"


def translate_segments(texts, tokenizer, model, torch_module):
    translations = []
    for start in range(0, len(texts), 8):
        batch = texts[start : start + 8]
        encoded = tokenizer(
            batch, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        with torch_module.no_grad():
            generated = model.generate(
                **encoded, max_new_tokens=512, num_beams=4, renormalize_logits=True
            )
        translations.extend(
            tokenizer.batch_decode(generated, skip_special_tokens=True)
        )
    return translations


def write_results(rows, output_base):
    txt_path = output_base.parent / f"{output_base.name}.bilingual.txt"
    csv_path = output_base.parent / f"{output_base.name}.bilingual.csv"
    html_path = output_base.parent / f"{output_base.name}.practice.html"

    with txt_path.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(f"[{row['time']}]\nEN: {row['english']}\n中文: {row['chinese']}\n\n")

    with csv_path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(
            output, fieldnames=("time", "english", "chinese")
        )
        writer.writeheader()
        writer.writerows(rows)

    cards = "\n".join(
        f"""<article class="card">
<div class="time">{html.escape(row['time'])}</div>
<div class="zh">{html.escape(row['chinese'])}</div>
<details><summary>显示英文答案 / Show English</summary>
<div class="en">{html.escape(row['english'])}</div></details>
</article>"""
        for row in rows
    )
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>中译英练习 / Chinese to English Practice</title>
<style>
body{{font:18px/1.6 system-ui,sans-serif;max-width:860px;margin:auto;padding:24px;
background:#f5f7fa;color:#172033}}h1{{font-size:28px}}.card{{background:white;
padding:20px;margin:16px 0;border-radius:12px;box-shadow:0 2px 10px #0001}}
.time{{color:#667085;font-size:14px}}.zh{{font-size:21px;margin:8px 0 14px}}
summary{{cursor:pointer;color:#175cd3}}.en{{margin-top:10px;color:#344054}}
</style></head><body><h1>中译英练习</h1>
<p>先根据中文说出或写出英文，然后展开答案进行对照。</p>{cards}</body></html>"""
    html_path.write_text(page, encoding="utf-8")
    return txt_path, csv_path, html_path


class BilingualTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper 英中转写学习工具")
        self.root.geometry("820x620")
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.model_var = tk.StringVar(value="base")
        self.status_var = tk.StringVar(value="请选择英语音频或视频文件")
        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=18)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="音频或视频 / Media:").grid(
            row=0, column=0, sticky=tk.W, pady=6
        )
        ttk.Entry(frame, textvariable=self.input_var).grid(
            row=0, column=1, sticky=tk.EW, padx=8, pady=6
        )
        ttk.Button(frame, text="选择", command=self.choose_input).grid(
            row=0, column=2, pady=6
        )

        ttk.Label(frame, text="输出文件夹 / Output:").grid(
            row=1, column=0, sticky=tk.W, pady=6
        )
        ttk.Entry(frame, textvariable=self.output_var).grid(
            row=1, column=1, sticky=tk.EW, padx=8, pady=6
        )
        ttk.Button(frame, text="选择", command=self.choose_output).grid(
            row=1, column=2, pady=6
        )

        ttk.Label(frame, text="Whisper 模型 / Model:").grid(
            row=2, column=0, sticky=tk.W, pady=6
        )
        ttk.Combobox(
            frame,
            textvariable=self.model_var,
            values=("tiny", "base", "small", "medium", "large"),
            state="readonly",
            width=12,
        ).grid(row=2, column=1, sticky=tk.W, padx=8, pady=6)
        ttk.Label(
            frame, text="small/medium 更准确，但需要更多内存和时间"
        ).grid(row=3, column=1, sticky=tk.W, padx=8)

        self.start_button = ttk.Button(
            frame, text="开始转写与翻译", command=self.start
        )
        self.start_button.grid(row=4, column=0, pady=14, sticky=tk.W)
        ttk.Label(frame, textvariable=self.status_var).grid(
            row=4, column=1, columnspan=2, sticky=tk.W, padx=8
        )

        self.preview = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.preview.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW)

    def choose_input(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Media", "*.mp3 *.m4a *.wav *.flac *.ogg *.mp4 *.mkv *.webm"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.input_var.set(path)
            if not self.output_var.get():
                self.output_var.set(str(Path(path).parent))

    def choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)

    def set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    def start(self):
        source = Path(self.input_var.get().strip()).expanduser()
        if not source.is_file():
            messagebox.showerror("文件错误", "请选择有效的音频或视频文件。")
            return
        output_dir = Path(self.output_var.get().strip()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        self.start_button.configure(state=tk.DISABLED)
        self.preview.delete("1.0", tk.END)
        threading.Thread(
            target=self.process,
            args=(source, output_dir, self.model_var.get()),
            daemon=True,
        ).start()

    def process(self, source, output_dir, whisper_model_name):
        try:
            self.set_status("正在加载本地 Whisper 模型…")
            import torch
            import whisper
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            device = "cuda" if torch.cuda.is_available() else "cpu"
            speech_model = whisper.load_model(whisper_model_name, device=device)
            self.set_status("正在识别英语语音…")
            result = speech_model.transcribe(
                str(source),
                language="en",
                task="transcribe",
                fp16=device == "cuda",
                verbose=False,
            )
            segments = [
                segment
                for segment in result.get("segments", [])
                if segment.get("text", "").strip()
            ]
            if not segments:
                raise RuntimeError("Whisper 没有识别到可用的英语语音。")

            self.set_status("正在加载本地英译中模型…")
            tokenizer = AutoTokenizer.from_pretrained(TRANSLATION_MODEL)
            translation_model = AutoModelForSeq2SeqLM.from_pretrained(
                TRANSLATION_MODEL
            )
            translation_model.eval()
            english = [segment["text"].strip() for segment in segments]
            self.set_status(f"正在翻译 {len(english)} 个片段…")
            chinese = translate_segments(
                english, tokenizer, translation_model, torch
            )
            rows = [
                {
                    "time": f"{timestamp(segment['start'])}–{timestamp(segment['end'])}",
                    "english": en,
                    "chinese": zh,
                }
                for segment, en, zh in zip(segments, english, chinese)
            ]
            paths = write_results(rows, output_dir / source.stem)
            preview = "\n\n".join(
                f"[{row['time']}]\nEN: {row['english']}\n中文: {row['chinese']}"
                for row in rows
            )
            self.root.after(0, self.finish, preview, paths)
        except Exception as error:
            self.root.after(0, self.fail, str(error))

    def finish(self, preview, paths):
        self.preview.insert(tk.END, preview)
        self.status_var.set("完成：已生成对照文本、CSV 和练习网页")
        self.start_button.configure(state=tk.NORMAL)
        messagebox.showinfo(
            "完成",
            "已生成：\n" + "\n".join(str(path) for path in paths),
        )

    def fail(self, error):
        self.status_var.set("处理失败")
        self.start_button.configure(state=tk.NORMAL)
        messagebox.showerror("处理失败", error)


if __name__ == "__main__":
    app_root = tk.Tk()
    BilingualTranscriber(app_root)
    app_root.mainloop()
