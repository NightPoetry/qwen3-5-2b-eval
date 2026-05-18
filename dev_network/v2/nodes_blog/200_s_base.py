"""CSS碎片：reset + body + layout"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    v = ctx["v"]
    ctx["css_fragments"]["00_base"] = f"""*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:{v['bg']};color:{v['text2']};line-height:1.7;-webkit-font-smoothing:antialiased}}
.w{{max-width:720px;margin:0 auto;padding:0 24px}}
html{{scroll-behavior:smooth}}
::selection{{background:{v['accent_bg']};color:{v['text']}}}
::-webkit-scrollbar{{width:6px}}::-webkit-scrollbar-thumb{{background:{v['border']};border-radius:3px}}"""
    return ctx

node = Node(id="200_s", name="CSS:base",
    trigger={"type": "key_exists", "key": "v"}, execute=execute,
    refs=["210_s", "220_s", "230_s", "240_s", "250_s", "260_s"])
