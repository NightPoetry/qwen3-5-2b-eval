"""输出保存 — 终端节点。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    html = ctx.get("html", "")
    if not html: return ctx
    out = Path(ctx.get("output_dir", "/tmp/blog"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    ctx["output_path"] = str(out)
    return ctx

node = Node(id="900_o", name="输出保存",
    trigger={"type": "key_exists", "key": "html"},
    execute=execute, refs=[])
