# -*- coding: utf-8 -*-
"""读取飞书纪要文档全文（markdown），落盘到 transcripts/。"""
import json
import os
import subprocess
import sys


def fetch_doc(doc_url, out_path):
    r = subprocess.run(
        ["lark-cli", "docs", "+fetch", "--doc", doc_url,
         "--doc-format", "markdown", "--as", "user"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode != 0:
        raise RuntimeError("fetch 失败: %s" % r.stderr[-600:])
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        data = {"ok": True, "data": {"document": {"content": r.stdout}}}
    if not data.get("ok"):
        raise RuntimeError("fetch 返回错误: %s" % json.dumps(data, ensure_ascii=False)[:600])
    doc = data.get("data", {}).get("document", {})
    content = doc.get("content", "")
    title = doc.get("title", "")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# %s\n\n" % title if title else "# 逐字稿\n\n")
        f.write(content)
    # 落一份完整 JSON 便于后续结构化读取
    json_path = out_path + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return title, content


if __name__ == "__main__":
    url = sys.argv[1]
    out = sys.argv[2]
    title, content = fetch_doc(url, out)
    print("TITLE:", title)
    print("CHARS:", len(content))
    print("SAVED:", out)
