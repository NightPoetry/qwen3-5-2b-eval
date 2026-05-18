"""知识节点：模块化架构 — 大文件拆分为子模块 + snapshot锁定。

适用场景：生成的代码超过合理复杂度时，建议拆分。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查生成的JS是否过长，建议拆分。"""
    js = ctx.get("js", "")
    if not js:
        return ctx

    lines = js.split("\n")
    if len(lines) > 150:
        ctx.setdefault("_warnings", []).append(
            f"JS代码{len(lines)}行，建议拆分为多文件模块"
        )
        # 给出拆分建议
        ctx.setdefault("_suggestions", []).append({
            "type": "split_files",
            "reason": "单文件过长，可拆分为 data.js + render.js + events.js",
            "threshold": 150,
            "current": len(lines),
        })

    return ctx


node = Node(
    id="200",
    name="模块化检查",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=[],
    metadata={"source": "Tool架构重构工程师", "category": "architecture"},
)
