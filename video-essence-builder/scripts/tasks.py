# -*- coding: utf-8 -*-
"""任务状态机与持久化：管理视频批处理任务的流转状态。"""
import json
import os
import time
import uuid

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

# 状态流转：pending -> extracting -> audio_done -> transcribing -> transcribed -> summarizing -> summarized -> rendering -> done
# 任一步失败置 error；error 可重置回上一稳定态重试。
STATUSES = [
    "pending",        # 已登记，待抽音频
    "extracting",     # 抽音频中（工具本地执行）
    "audio_done",     # 音频已抽出，待云端转写
    "transcribing",   # 转写中（云端/agent 驱动）
    "transcribed",    # 逐字稿已落盘，待总结
    "summarizing",    # 总结中（agent 执行）
    "summarized",     # 总结完成，待渲染
    "rendering",      # 生成 HTML/PDF 中
    "done",           # 全部完成
    "error",          # 失败
]

# 每个状态下，任务里可用的"下一步动作"（供 UI 展示按钮）
ACTIONS = {
    "pending":      ["extract_audio"],
    "audio_done":   ["transcribe"],
    "transcribed":  ["summarize"],
    "summarized":   ["render"],
    "error":        ["retry_prev"],
    "done":         ["open_output"],
}


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("tasks", [])
    except Exception:
        return []


def save_tasks(tasks):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = TASKS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks}, f, ensure_ascii=False, indent=2)
    os.replace(tmp, TASKS_FILE)


def new_task_id():
    return "t" + time.strftime("%Y%m%d") + "_" + uuid.uuid4().hex[:6]


def add_task(video_path):
    """登记一个视频任务；同名视频已存在时返回 None。"""
    video_path = os.path.abspath(video_path)
    tasks = load_tasks()
    for t in tasks:
        if t.get("video_path") == video_path:
            return None
    task = {
        "id": new_task_id(),
        "title": os.path.splitext(os.path.basename(video_path))[0],
        "video_path": video_path,
        "video_size_mb": round(os.path.getsize(video_path) / 1048576, 1) if os.path.exists(video_path) else None,
        "status": "pending",
        "audio_path": None,
        "transcript_path": None,
        "summary_json": None,
        "output_html": None,
        "output_pdf": None,
        "error": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def get_task(task_id):
    for t in load_tasks():
        if t["id"] == task_id:
            return t
    return None


def update_task(task_id, **fields):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t.update(fields)
            t["updated_at"] = _now()
            save_tasks(tasks)
            return t
    return None


def set_status(task_id, status, error=None):
    fields = {"status": status}
    if error is not None:
        fields["error"] = error
    return update_task(task_id, **fields)


def scan_videos(folder):
    """扫描目录下常见视频格式文件，返回路径列表。"""
    exts = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".ts", ".m4v", ".webm"}
    out = []
    if not os.path.isdir(folder):
        return out
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name)
        if os.path.isfile(p) and os.path.splitext(name)[1].lower() in exts:
            out.append(p)
    return out
