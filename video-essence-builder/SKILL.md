---
name: video-essence-builder
description: 批量把直播录屏/长视频变成「重点精要」HTML+PDF 报告。当用户要处理一堆 3 小时级直播录屏、录像、课程回放、会议录制的重点提取与精要整理时使用（触发词：视频精要、直播重点、录屏整理、逐字稿转精要、批量视频总结）。四步流水线：①ffmpeg 抽音频 ②豆包云端转写逐字稿 ③AI 总结重点成 summary.json ④渲染为深墨绿+琥珀风格的 HTML 与 A4 PDF。
---

# Video Essence Builder

把长视频批量加工成「重点精要」HTML/PDF。整个流程 6 步，其中抽音频与渲染由本 skill 脚本确定性执行，云端转写与重点总结由 AI Agent 在会话中完成。

## 流程概览

1. **登记任务** → `tasks.py add_task(视频路径)`
2. **抽音频** → `extract_audio.py`（ffmpeg，16kHz 单声道 m4a）
3. **云端转写**（AI 环节）→ 上传音频 → 豆包智能纪要（逐字稿 + 章节/决策/金句）
4. **重点总结**（AI 环节）→ 通读逐字稿与纪要 → 写 `summary.json`
5. **渲染** → `agent_steps.render()` → HTML + PDF
6. **交付** → `present_files` 交付两个产物

## 环境依赖

- Python 3；可选 `pymupdf`（PDF 页数校验，缺则跳过）
- `ffmpeg` + `ffprobe`（脚本自动发现 PATH 或常见安装位置）
- Chrome headless shell（`render_pdf.py` 自动发现 `~/AppData/Local/ms-playwright/chromium_headless_shell-*`）
- 豆包云端工具（转写环节）：`FileBatchUpload` 上传音频、`analyze_audio` 生成智能纪要、`lark-cli note +transcript` 拉逐字稿

## 使用步骤

### Step 1 登记任务

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); import tasks as T; t=T.add_task(r'<视频绝对路径>'); print(t['id'])"
```

按视频路径去重：重复添加返回 None。批量场景先 `tasks.scan_videos(folder)` 得到目录下全部视频，逐个登记。

### Step 2 抽音频

```bash
python scripts/extract_audio.py <视频路径> [音频输出目录]
```

输出两行：`AUDIO: <m4a路径>` 与 `DURATION_SEC: <秒>`。随后登记：

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); import tasks as T; T.update_task('<task_id>', audio_path=r'<m4a>', duration_sec=<秒>, status='audio_done')"
```

### Step 3 云端转写（AI 环节）

1. 用 `FileBatchUpload` 上传 m4a 得到 URL。
2. 调 `analyze_audio(audio_uri=<URL>)`，等待智能纪要生成完成（status=Finished），得到纪要 docx 链接与 `note_id`。
3. 读纪要 docx（含 AI 总结：智能章节、关键决策、金句时刻）——这是总结的重要底稿。
4. 拉完整逐字稿：unified 类型纪要必须走 `lark-cli note +transcript --note-id <note_id>`，落盘为 `.md`（行格式 `@说话人 时间`）。纪要 docx 正文不含逐字稿。
5. 登记结果：

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); import agent_steps as A; A.mark_transcribed('<task_id>', r'<逐字稿md>', '<纪要docxURL>', '<note_id>')"
```

### Step 4 重点总结（AI 环节）

1. 通读完整逐字稿与智能纪要，提炼真实重点（不编造未讲内容）。
2. 按下方 schema 组织 summary.json，调用：

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); import agent_steps as A; A.mark_summarized('<task_id>', { ...summary dict... })"
```

### Step 5 渲染

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); import agent_steps as A; A.render('<task_id>')"
```

产物：`output/<task_id>/<标题>.html` 与 `<标题>.pdf`（A4）。渲染后自检：浏览器截图核对首页满页、无横向滚动、时间轴连续；PDF 用 pymupdf 渲染页面对比。

### Step 6 交付

- 用 `present_files` 交付 HTML 与 PDF（一次调用）。
- 若用户要求飞书云文档版，用 `lark-cli drive +import --type docx` 导入，或经 lark-doc 重建。

## summary.json Schema

| 字段 | 类型 | 说明 |
|---|---|---|
| `doc_title` | str | 文档标题 |
| `hero.kicker / title / subtitle / info` | str / list | title 支持 `<em>关键词</em>` 高亮；info 为 `[["标签","值"],...]` |
| `stats` | list | 关键数字条：`{"n":"8年","t":"说明"}` |
| `sections[]` | list | 章节；字段 `num`(编号)/`kicker`/`title`/`lede`/`type` |
| sections[].type=cards | — | `cards:[{tag,t,body,hot?}]`（3 卡自动三列、2 卡两列） |
| sections[].type=timeline | — | `nodes:[{time,t,body}]` |
| sections[].type=quotes | — | `quotes:[{q,note}]` |
| sections[].type=callout | — | `body` + 可选 `accent:"amber"` |
| `footer` | str | 文末来源/免责声明 |

章节编号可重复（如两个 `05`），导航自动去重。

## 模板与样式

- 模板：`assets/template.html`（深墨绿 hero 满页 + 琥珀强调 + 衬线标题；A4 打印样式、卡片防断页、横向容器换行不滚动全部内联）。
- `render_html.py` 优先读同目录 `template.html`，无则读 `../assets/template.html`（skill 自包含）。

## 关键约定与坑

- **逐字稿入口**：智能纪要 docx 只有 AI 总结；完整逐字稿必须走 unified note 的 `note +transcript`。
- **Windows 编码**：PowerShell 管道/重定向会破坏 UTF-8；文件读写一律用 Python 显式 `encoding='utf-8'`，脚本输出用 `python -c` 读取。
- **产物位置**：默认 `output/`（skill 目录内）；可用环境变量 `AIKIT_OUTPUT_ROOT=D:/...` 覆盖到用户指定目录。
- **内容口径**：心理/医疗/投资类直播总结，footer 必须写「不构成医疗/投资建议」类免责；重点必须来自逐字稿，不可编造。
- **PDF 自检**：hero 必须满页无大片留白；时间轴轴线为容器级贯穿线；任何横向滚动容器都会在 PDF 截断，模板已规避，改动模板后需复检。
