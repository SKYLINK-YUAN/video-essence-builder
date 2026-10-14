# -*- coding: utf-8 -*-
"""Step 1: 从视频抽取音频（ffmpeg）。输出 16kHz 单声道 m4a，体积小且转写友好。"""
import os
import shutil
import subprocess


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    # 常见本地安装路径兜底
    candidates = [
        r"D:\pythoncut\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise RuntimeError("未找到 ffmpeg，请安装并加入 PATH，或在 pipeline/extract_audio.py 中配置路径")


def extract_audio(video_path, out_dir, ffmpeg=None, keep_m4a=True):
    """抽取音频。返回 (audio_path, duration_sec)。
    duration_sec 由 ffprobe 读取，读不到时为 None。
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError("视频不存在: %s" % video_path)
    os.makedirs(out_dir, exist_ok=True)
    ffmpeg = ffmpeg or find_ffmpeg()
    base = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(out_dir, base + ".m4a")

    cmd = [
        ffmpeg, "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "aac", "-b:a", "128k",
        "-progress", "pipe:1", "-nostats",
        audio_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0 or not os.path.exists(audio_path):
        raise RuntimeError("抽音频失败: %s" % (proc.stderr[-800:] if proc.stderr else "unknown"))

    duration = _probe_duration(video_path, ffmpeg)
    return audio_path, duration


def _probe_duration(video_path, ffmpeg):
    """用 ffprobe 读取视频时长（秒）。"""
    ffprobe = os.path.join(os.path.dirname(ffmpeg), "ffprobe.exe")
    if not os.path.exists(ffprobe):
        return None
    try:
        cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return round(float(out.stdout.strip()), 1)
    except Exception:
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python extract_audio.py <视频路径> [输出目录]")
        sys.exit(1)
    video = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "audio")
    audio, dur = extract_audio(video, out)
    print("AUDIO:", audio)
    print("DURATION_SEC:", dur)
