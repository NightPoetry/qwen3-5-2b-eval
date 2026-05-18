"""节点：元素提取（Phase 1）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx["task"]
    interactions = ctx["interactions"]

    components = ask(
        "列出交互中涉及的具体UI元素。每行：标签类型 用途。不要解释。",
        (f"应用：{task}\n\n用户交互：\n{interactions}\n\n"
         "列出上述交互中需要的具体HTML元素：\n"
         "格式（每行一个）：\n"
         "  input 用户输入任务文本\n"
         "  button 点击添加\n"
         "  ul 显示列表\n\n"
         "只列出元素："),
        max_tokens=200
    )
    ctx["components"] = components
    return ctx


node = Node(
    id="020",
    name="元素提取",
    trigger={"type": "key_exists", "key": "interactions"},
    execute=execute,
    refs=["030", "110", "130"],
)
