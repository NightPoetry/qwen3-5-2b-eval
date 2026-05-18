"""输出节点：对话输出 — 光标锚点，所有对话的终点。

refs 指向所有域抽象 = 下轮 cursor 可进入任何域。
顺序：B00 > C00 > D00 > A00（技术优先，对话兜底）。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    return ctx

node = Node(
    id="Y10", name="对话输出",
    trigger={"type": "key_exists", "key": "_chat_response"},
    execute=execute,
    refs=["B00", "C00", "D00", "A00"],
    metadata={"category": "output", "layer": "output"})
