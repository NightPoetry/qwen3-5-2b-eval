"""节点：CSS生成 — 模型只看元素用途，不看HTML。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx["task"]
    elements = ctx["contract"]["elements"]
    purpose_list = "\n".join(f'  #{e["id"]}: {e["purpose"]}' for e in elements)

    raw = ask(
        ("你是 CSS 开发者。只输出纯 CSS 代码（不要 HTML）。\n"
         "简洁现代暗色风格，背景#0d1117，文字#c9d1d9，max-width:600px 居中。"),
        (f"为 {task} 编写样式。\n\n"
         f"需要样式的元素：\n{purpose_list}\n\n"
         f"要求：容器居中、输入框全宽、按钮醒目、列表项有间距、暗色主题。"),
        max_tokens=1024
    )
    ctx["raw_css"] = raw
    return ctx


node = Node(
    id="050",
    name="CSS生成",
    trigger={"type": "key_exists", "key": "contract"},
    execute=execute,
    refs=["071"],
)
