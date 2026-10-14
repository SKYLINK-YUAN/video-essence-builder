# -*- coding: utf-8 -*-
"""Step 4: 把 summary.json 渲染为单页 HTML（数据驱动模板，视觉风格固定）。"""
import html
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(_HERE, "template.html")
if not os.path.exists(TEMPLATE_FILE):
    TEMPLATE_FILE = os.path.join(_HERE, "..", "assets", "template.html")


def _esc(s):
    return html.escape(str(s), quote=False)


def render_cards(cards):
    n = len(cards)
    cls = "grid3"
    if n == 2 or (n > 2 and n % 2 == 0 and n % 3 != 0):
        cls = "grid2"
    parts = ['<div class="%s">' % cls]
    for c in cards:
        tag = ('<span class="tag%s">%s</span>' % (" hot" if c.get("hot") else "", _esc(c.get("tag", "")))) if c.get("tag") else ""
        parts.append('<div class="card">%s<div class="t">%s</div><div class="body">%s</div></div>'
                     % (tag, _esc(c.get("t", "")), _esc(c.get("body", ""))))
    parts.append("</div>")
    return "\n".join(parts)


def render_timeline(nodes):
    parts = ['<div class="timeline">']
    for nd in nodes:
        parts.append(
            '<div class="tl-row"><div class="tl-time">%s</div>'
            '<div class="tl-axis"><i></i></div>'
            '<div class="tl-body"><div class="tl-t">%s</div><div class="tl-d">%s</div></div></div>'
            % (_esc(nd.get("time", "")), _esc(nd.get("t", "")), _esc(nd.get("body", ""))))
    parts.append("</div>")
    return "\n".join(parts)


def render_quotes(quotes):
    parts = ['<div class="quotes">']
    for q in quotes:
        parts.append('<div class="quote"><div class="q">%s</div><div class="note">%s</div></div>'
                     % (_esc(q.get("q", "")), _esc(q.get("note", ""))))
    parts.append("</div>")
    return "\n".join(parts)


def render_callout(c):
    accent = " amber" if c.get("accent") == "amber" else ""
    return '<div class="callout%s">%s</div>' % (accent, _esc(c.get("body", "")))


def render_section(sec):
    kind = sec.get("type", "cards")
    if kind == "timeline":
        body = render_timeline(sec.get("nodes", []))
    elif kind == "quotes":
        body = render_quotes(sec.get("quotes", []))
    elif kind == "callout":
        body = render_callout(sec)
    else:
        body = render_cards(sec.get("cards", []))
    lede = '<p class="lede">%s</p>' % _esc(sec.get("lede", "")) if sec.get("lede") else ""
    return (
        '<section id="s%s"><div class="wrap">'
        '<div class="sec-head">'
        '<span class="sec-num">%s</span>'
        '<span class="sec-kicker">%s</span>'
        '<span class="sec-title">%s</span>'
        '</div>%s%s</div></section>'
        % (sec.get("num", "0"), _esc(sec.get("num", "00")),
           _esc(sec.get("kicker", "")), _esc(sec.get("title", "")), lede, body)
    )


def render_summary(summary, out_html):
    """summary: dict；out_html: 输出路径。返回 None。"""
    hero = summary.get("hero", {})
    stats = summary.get("stats", [])
    sections = summary.get("sections", [])

    hero_meta = "".join(
        '<span>%s：<b>%s</b></span>' % (_esc(k), _esc(v)) for k, v in hero.get("info", [])
    )
    hero_stats = "".join(
        '<div class="stat"><div class="n">%s</div><div class="t">%s</div></div>'
        % (_esc(s.get("n", "")), _esc(s.get("t", ""))) for s in stats
    )
    seen_nums, nav_items = set(), []
    for sec in sections:
        num = sec.get("num", "")
        if num and num in seen_nums:
            continue
        seen_nums.add(num)
        nav_items.append('<a href="#s%s">%s %s</a>' % (num, num, sec.get("kicker", "")))
    nav_links = "".join(nav_items) if nav_items else ""
    sections_html = "\n".join(render_section(sec) for sec in sections)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        tpl = f.read()

    repl = {
        "{{DOC_TITLE}}": _esc(summary.get("doc_title", hero.get("title", "AI 讲座精要"))),
        "{{BRAND}}": _esc((summary.get("doc_title", "") or "").split("｜")[0][:8] or "AI 精要"),
        "{{NAV_LINKS}}": nav_links,
        "{{HERO_KICKER}}": _esc(hero.get("kicker", "")),
        "{{HERO_TITLE}}": hero.get("title", ""),           # 允许 <em> 高亮
        "{{HERO_SUB}}": _esc(hero.get("subtitle", "")),
        "{{HERO_META}}": hero_meta,
        "{{HERO_STATS}}": hero_stats,
        "{{SECTIONS}}": sections_html,
        "{{FOOTER}}": _esc(summary.get("footer", "")),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(tpl)
    return out_html


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python render_html.py <summary.json> <out.html>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    out = render_summary(data, sys.argv[2])
    print("HTML:", out)
