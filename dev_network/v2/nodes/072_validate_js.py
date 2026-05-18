"""节点：JS验证 + 知识卡009(可逆不弹confirm)。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node


def execute(ctx: dict) -> dict:
    raw = ctx.get("raw_js", "")
    issues = []

    # [知识卡009] 移除可逆操作的confirm
    confirm_pattern = r'if\s*\(\s*confirm\s*\([^)]*\)\s*\)\s*\{'
    if re.search(confirm_pattern, raw):
        raw = re.sub(confirm_pattern, '{', raw)
        issues.append("移除可逆操作confirm()")

    ctx["js"] = raw
    ctx["js_issues"] = issues
    return ctx


node = Node(
    id="072",
    name="JS验证+知识卡",
    trigger={"type": "key_exists", "key": "raw_js"},
    execute=execute,
    refs=["080", "101", "140"],
)
