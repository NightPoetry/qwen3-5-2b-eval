"""输出节点：代码输出 — 光标锚点，代码流水线终点。"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    return ctx

node = Node(
    id="Y20", name="代码输出",
    trigger={"type": "key_exists", "key": "html"},
    execute=execute,
    refs=["B00", "C00", "D00", "A00"],
    metadata={"category": "output", "layer": "output"})
