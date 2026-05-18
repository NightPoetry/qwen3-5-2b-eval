"""节点：输出保存 — 终端节点，无refs。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node


def execute(ctx: dict) -> dict:
    output_dir = Path(ctx.get("output_dir", "/tmp/v2_output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "index.html": ctx.get("html", ""),
        "style.css": ctx.get("css", ""),
        "app.js": ctx.get("js", ""),
    }

    for name, content in files.items():
        if content:
            (output_dir / name).write_text(content)

    ctx["output_path"] = str(output_dir)
    ctx["output_files"] = list(files.keys())
    return ctx


node = Node(
    id="090",
    name="输出保存",
    trigger={"type": "key_exists", "key": "html"},
    execute=execute,
    refs=["Y20"],  # 终端节点
)
