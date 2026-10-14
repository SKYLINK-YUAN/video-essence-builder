# -*- coding: utf-8 -*-
"""Agent 协作步骤：AI 环节（云端转写、重点总结）由 Agent 在会话中执行，
完成后调用本模块登记结果、推进任务状态，并触发 HTML/PDF 渲染。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tasks as T
from render_html import render_summary
from render_pdf import html_to_pdf

OUTPUT_ROOT = os.environ.get("AIKIT_OUTPUT_ROOT") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def task_dir(task_id):
    d = os.path.join(OUTPUT_ROOT, task_id)
    os.makedirs(d, exist_ok=True)
    return d


def mark_transcribed(task_id, transcript_path, note_doc_url, note_id):
    """转写完成：登记逐字稿路径与纪要链接，audio_done -> transcribed"""
    return T.update_task(task_id, status="transcribed",
                         transcript_path=transcript_path,
                         note_doc_url=note_doc_url, note_id=note_id)


def mark_summarized(task_id, summary):
    """总结完成：写入 summary.json，transcribed -> summarized"""
    d = task_dir(task_id)
    path = os.path.join(d, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return T.update_task(task_id, status="summarized", summary_json=path)


def render(task_id):
    """渲染 HTML + PDF：summarized -> done"""
    task = T.get_task(task_id)
    if not task or not task.get("summary_json"):
        raise RuntimeError("任务不存在或尚未总结: %s" % task_id)
    T.set_status(task_id, "rendering")
    d = task_dir(task_id)
    title = task["title"]
    out_html = os.path.join(d, title + ".html")
    out_pdf = os.path.join(d, title + ".pdf")
    with open(task["summary_json"], "r", encoding="utf-8") as f:
        summary = json.load(f)
    render_summary(summary, out_html)
    pages, kb = html_to_pdf(out_html, out_pdf)
    T.update_task(task_id, status="done", output_html=out_html, output_pdf=out_pdf,
                  pdf_pages=pages, pdf_size_kb=kb)
    return {"html": out_html, "pdf": out_pdf, "pages": pages, "size_kb": kb}
