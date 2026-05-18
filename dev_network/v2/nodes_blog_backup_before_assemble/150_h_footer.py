"""HTML碎片：footer"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify": return ctx
    ctx["html_fragments"]["footer"] = """<footer><div class="w">Powered by 2B Model + Executable Knowledge Network</div></footer>"""
    return ctx

node = Node(id="150_h", name="HTML:footer",
    trigger={"type": "key_exists", "key": "v"}, execute=execute, refs=["200_s"])
