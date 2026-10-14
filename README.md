# Video Essence Builder · 豆包工作视频转写与精要整理 Skill

把直播录屏、课程回放、会议录像等长视频，整理成逐字稿、结构化重点，以及可阅读、打印的 HTML / PDF 精要报告。

**面向豆包工作（Doubao Work）的 AI 协作流程。** 本 Skill 将本机脚本和豆包云端工具串起来：脚本负责抽音频与排版，豆包工具负责转写，AI 在会话中阅读和总结。

> 这是社区整理的 Skill，不是豆包官方产品。普通豆包聊天窗口未必具备所需工具；能否使用完整流程，取决于你的豆包工作环境是否提供本机执行、音频上传、智能纪要和逐字稿读取能力。

## 适用范围

| 内容 | 可整理的结果 |
| --- | --- |
| 直播录屏、长视频分享 | 主题重点、讲解脉络、观点与时间线 |
| 课程回放、培训录像 | 知识框架、方法步骤、复习提纲 |
| 会议录制 | 讨论重点、明确提出的决策和行动项 |
| 访谈、经验分享 | 观点、案例、原话摘录 |
| 已有逐字稿或智能纪要 | 跳过抽音频与转写，直接总结并渲染 |

目录扫描支持 MP4、MKV、MOV、AVI、FLV、WMV、TS、M4V、WEBM，实际可读格式取决于 ffmpeg。当前扫描为目录第一层，不递归子目录。可批量登记和逐个处理任务，适合 3 小时级长录屏；云端容量与时长上限以实际账号和工具为准。

不适合仅靠画面才能理解的无声视频、要求逐帧分析的操作演示，也不提供说话人身份认证、法庭级转录或保证准确的医疗与投资结论。

## 优点

- **长视频变成可复用资料**：保留逐字稿，再提炼章节、步骤、时间线和重点，便于查找和复习。
- **适合连续处理多份录屏**：任务状态落盘，同一路径重复登记会跳过，已完成的转写与总结可复用。
- **不要求本机独立显卡**：本机只做音频提取和文档渲染，语音转写走豆包云端。
- **当前协作流程无需自行配置模型 API Key**：使用豆包工作已有的转写工具与 AI 会话能力；仍需相应账号、权限，可能受平台额度限制。
- **交付同时照顾阅读和打印**：深墨绿与琥珀配色的 HTML、带 A4 打印样式的 PDF，支持卡片、时间线、引语、提示块。
- **内容与样式分离**：重点以 `summary.json` 保存，修改内容后可重新生成报告，无需重新转写。

## 工作流程

```text
视频 → 本机 ffmpeg 抽音频 → 豆包上传与智能纪要
     → 获取完整逐字稿 → AI 阅读并写 summary.json
     → 本机生成 HTML + PDF → 人工核对并交付
```

这不是解压后自行运行的全自动软件。`FileBatchUpload`、`analyze_audio`、`present_files` 等能力属于宿主 Agent 环境，并未由仓库脚本实现。转写和总结需要 AI 协作。

## 安装到豆包工作

1. 下载仓库中的 [video-essence-builder-skill.zip](video-essence-builder-skill.zip)。
2. 解压，得到顶层 `video-essence-builder/` 文件夹。
3. 将整个文件夹放入你的豆包工作环境所识别的 `.user_skills` 目录；具体目录以该环境的实际配置为准。不要只复制 `SKILL.md`。
4. 在豆包工作中确认 Skill 已识别，并为任务提供本机视频路径或已有逐字稿。
5. 对 AI 说：

```text
使用 video-essence-builder，处理 D:/Videos/课程回放 目录里的视频。
每个视频保留逐字稿，提炼真实重点和行动步骤，生成 HTML 与 A4 PDF。
先检查本机依赖和豆包转写工具是否可用，逐个处理，完成后核对产物。
```

详细执行约定见 [SKILL.md](video-essence-builder/SKILL.md)。仓库整包与 Skill 安装包不同：安装时选内层 `video-essence-builder/`。

## 环境依赖

| 依赖 | 用途与要求 |
| --- | --- |
| Python 3 | 运行脚本；本次发布在 Windows / Python 3.11 检查 |
| ffmpeg、ffprobe | 抽音频与读取时长，推荐放入 PATH；当前时长探测使用 Windows 的 `ffprobe.exe` |
| Chrome / Chromium headless shell | 将 HTML 打印为 PDF；推荐 Playwright headless shell，脚本自动查找 |
| PyMuPDF（可选） | PDF 页数校验，缺少时跳过该项 |
| 豆包工作云端工具 | 音频上传、`analyze_audio` 智能纪要 |
| 已登录且有权限的 lark-cli | 使用 `note +transcript` 获取逐字稿 |

PDF 浏览器可按需安装：

```bash
python -m pip install playwright pymupdf
python -m playwright install chromium --only-shell
```

这些依赖不包含在 ZIP 内。浏览器发现逻辑兼顾 Windows、macOS、Linux，但完整链路主要面向 Windows 豆包工作；其他系统尚未在本次发布中验证。

## 其他 Agent 能不能用？

Codex、Claude Code 等可以复用本地 Python 脚本和 HTML 模板，但不能仅凭安装此 Skill 获得豆包内部转写工具。需要自行接入可用转写方案，并把完整逐字稿交给 AI 总结。

已有 `summary.json` 时，可以只使用渲染功能。此路径无需调用豆包转写工具：

```bash
python examples/render_demo.py
```

该示例全部为虚构内容，输出到 `demo-output/`，需 PDF 浏览器依赖。

## 输出与存储

- 逐字稿：由 Agent 保存到指定路径。
- 中间结果：`summary.json`，便于审阅和修改。
- 最终报告：HTML、PDF。
- 任务记录：Skill 目录下 `data/tasks.json`。
- 报告默认放在 Skill 目录下 `output/`；可用 `AIKIT_OUTPUT_ROOT` 指定报告输出目录。这个变量不会迁移任务记录或音频。

## 使用边界与常见问题

**智能纪要是不是逐字稿？** 不是。纪要文档通常是 AI 总结，应另用 `note +transcript` 获取完整逐字稿。`fetch_transcript.py` 实际读取的是纪要文档正文，不能将其输出直接当作完整逐字稿。

**是不是完全离线？** 不是。抽音频和渲染在本机执行，云端转写需要联网，音频会上传到相应平台。只处理你有权上传和整理的材料。

**可以同时跑很多任务吗？** 建议先顺序处理。当前任务记录采用单个 JSON 文件，未实现多进程锁；并行写入有覆盖风险。

**超大音频怎么办？** 当前抽音频默认 128 kbps AAC，长录屏输出可能较大。Agent 应按实际平台限制压缩或分段，并验证完整性，不能承诺任意大小都可上传。

**失败会自动恢复吗？** 状态和结果保存在本机，Agent 可据此重试；当前脚本不提供完整自动断点恢复。尤其渲染异常时，应检查记录和文件后再推进状态。

**总结能保证准确吗？** 不能。口音、噪声、多人重叠、术语都会影响转写；总结必须依据逐字稿，金额、姓名、日期和原话应回看原始材料。请将内容当作复习与整理辅助。

**需要网页服务吗？** 此发布包是独立 Skill，不包含局域网 Web 管理端，也不包含云端 API 服务。

**旧包的富文本限制？** 本发布沿用用户提供的 Skill 包。正文中的 HTML 标记会被转义，示例使用纯文本；没有将其他工具版本的富文本功能当作此包的能力。

## 仓库结构

```text
README.md
video-essence-builder-skill.zip
video-essence-builder/
  SKILL.md
  scripts/        # 任务管理、音频提取、纪要读取、渲染与协作登记
  assets/template.html
examples/
  summary.json
  render_demo.py
VALIDATION.md
```

## 验证范围

原项目已有长视频处理经验。本次发布只对随包脚本进行语法、音频提取、任务流转与虚构示例 HTML/PDF 冒烟验证；没有重新调用豆包云端转写服务。结果见 [VALIDATION.md](VALIDATION.md)。历史实测不代表每个账号、平台版本和文件都能获得相同效果。

本仓库未附带视频、真实逐字稿、个人纪要、账号凭据或 API Key。豆包、飞书及第三方依赖的名称与标识属于各自权利人。
