# -*- coding: utf-8 -*-
"""Step 5: 用本机 Chrome headless shell 把 HTML 转为 PDF（A4 打印样式已在模板中）。
跨平台查找：Windows/macOS/Linux 的 Playwright headless shell；找不到时回退系统 chrome。"""
import glob
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

_EXE_NAMES = ["chrome-headless-shell.exe", "chrome-headless-shell"]


def _find_in(dirpath, names):
    for n in names:
        p = os.path.join(dirpath, n)
        if os.path.exists(p):
            return p
    return None


def find_shell():
    home = os.path.expanduser("~")
    sysname = platform.system()
    roots = []
    if sysname == "Windows":
        roots.append(os.path.join(os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local")), "ms-playwright"))
    elif sysname == "Darwin":
        roots.append(os.path.join(home, "Library", "Caches", "ms-playwright"))
    else:
        roots.append(os.path.join(home, ".cache", "ms-playwright"))
    for root in roots:
        hits = sorted(glob.glob(os.path.join(root, "chromium_headless_shell-*")), reverse=True)
        for d in hits:
            exe = _find_in(d, _EXE_NAMES)
            if exe:
                return exe
            # macOS/Linux 下 shell 可执行文件在平台子目录内
            for sub in os.listdir(d):
                subp = os.path.join(d, sub)
                if os.path.isdir(subp):
                    exe = _find_in(subp, _EXE_NAMES)
                    if exe:
                        return exe
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        exe = shutil.which(name)
        if exe:
            return exe
    raise RuntimeError("未找到 chrome/chrome-headless-shell，请安装 Playwright 的 chromium headless shell 或 Chrome")


def html_to_pdf(html_path, pdf_path, timeout=300):
    """返回 (页数, 文件大小KB)。"""
    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)
    shell = find_shell()
    url = Path(html_path).as_uri()          # file:/// 自动百分号编码中文路径
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    cmd = [shell, "--disable-gpu", "--no-pdf-header-footer",
           "--print-to-pdf=" + pdf_path, url]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    if proc.returncode != 0 or not os.path.exists(pdf_path):
        raise RuntimeError("转 PDF 失败: %s" % proc.stderr[-600:])
    try:
        import pymupdf
        d = pymupdf.open(pdf_path)
        pages = d.page_count
        d.close()
    except Exception:
        pages = None
    return pages, round(os.path.getsize(pdf_path) / 1024)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python render_pdf.py <in.html> <out.pdf>")
        sys.exit(1)
    pages, kb = html_to_pdf(sys.argv[1], sys.argv[2])
    print("PDF:", sys.argv[2])
    print("PAGES:", pages)
    print("SIZE_KB:", kb)
