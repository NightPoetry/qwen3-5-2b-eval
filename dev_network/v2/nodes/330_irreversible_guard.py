"""知识节点：不可逆信息丢失保险——操作前检测是否有不可逆损失。

适用于删除、覆盖、合并等操作。
系统检测不可逆操作 → 要求确认或备份。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

IRREVERSIBLE_PATTERNS = {
    "rm -rf": "递归删除文件系统",
    "DROP TABLE": "删除数据库表",
    "truncate": "清空数据",
    "innerHTML = ''": "清空DOM（已有数据丢失）",
    "localStorage.clear": "清空本地存储",
    "overwrite": "覆盖文件",
    ".remove()": "DOM节点移除",
}

def execute(ctx: dict) -> dict:
    js = ctx.get("js", "")
    if not js: return ctx

    risks = []
    for pattern, desc in IRREVERSIBLE_PATTERNS.items():
        if pattern in js:
            risks.append(f"{desc}({pattern})")

    if risks:
        ctx.setdefault("_irreversible_warnings", []).extend(risks)
    return ctx

node = Node(id="330", name="不可逆操作检测",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute, refs=["Y30"],
    metadata={"source": "Skills/不可逆信息丢失保险", "category": "safety"})
