"""节点：HTML生成 — 模型只看静态元素契约。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx["task"]
    elements = ctx["contract"]["elements"]

    id_list = ", ".join(f'{e["id"]}({e["tag"]})' for e in elements)
    purpose_list = "\n".join(f'  #{e["id"]}: {e["purpose"]}' for e in elements)

    raw = ask(
        ("你是 HTML 开发者。只输出 HTML 代码。使用中文文本。\n"
         "head 中用 <link rel=\"stylesheet\" href=\"style.css\">。\n"
         "body 末尾用 <script src=\"app.js\"></script>。\n"
         "不写 <style>，不写 inline JS。"),
        (f"创建 {task} 的 HTML 页面。\n\n"
         f"【必须使用以下 ID（不得改名）】：\n{purpose_list}\n\n"
         f"元素标签：{id_list}\n"
         f"页面标题用中文。"),
        max_tokens=1024
    )
    ctx["raw_html"] = raw
    return ctx


node = Node(
    id="040",
    name="HTML生成",
    trigger={"type": "key_exists", "key": "contract"},
    execute=execute,
    refs=["070"],
)
