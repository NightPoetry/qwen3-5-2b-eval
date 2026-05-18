"""知识节点：失效模式与恢复——当模型输出崩溃时的恢复策略。

系统层兜底：模型输出混乱时，回退到已知安全状态。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    # 检测各类失效
    failures = []

    js = ctx.get("js", ctx.get("raw_js", ""))
    html = ctx.get("html", ctx.get("raw_html", ""))
    css = ctx.get("css", ctx.get("raw_css", ""))

    # JS中混入HTML
    if js and "<html" in js.lower():
        failures.append("JS中混入HTML")
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', js, re.DOTALL)
        if scripts:
            ctx["js"] = max(scripts, key=len).strip()

    # CSS中混入HTML
    if css and "<html" in css.lower():
        failures.append("CSS中混入HTML")

    # HTML完全为空或只有markdown
    if html and "<html" not in html.lower() and "```" in html:
        failures.append("HTML输出为markdown而非HTML")
        blocks = re.findall(r'```html?\n(.*?)```', html, re.DOTALL)
        if blocks:
            ctx["html"] = blocks[0]

    # JS输出为空但应有内容
    if not js and ctx.get("contract", {}).get("events"):
        failures.append("JS为空但契约中有事件定义")

    if failures:
        ctx.setdefault("_failures_recovered", []).extend(failures)

    return ctx

node = Node(id="350", name="失效恢复",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/失效模式与恢复", "category": "safety"})
