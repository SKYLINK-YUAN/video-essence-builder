"""Render the fictional demo without uploading audio or contacting Doubao."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'video-essence-builder' / 'scripts'))
from render_html import render_summary
from render_pdf import html_to_pdf

summary = json.loads((root / 'examples' / 'summary.json').read_text(encoding='utf-8'))
out = root / 'demo-output'
out.mkdir(exist_ok=True)
render_summary(summary, str(out / 'demo.html'))
pages, size = html_to_pdf(str(out / 'demo.html'), str(out / 'demo.pdf'))
print(f'HTML/PDF ready: {out}; pages={pages}; size_kb={size}')
