"""知识节点：边界可控 — flex防溢出 + 文本截断。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    css = ctx.get("css", "")
    if not css:
        return ctx

    fixes = []

    # flex:1 防溢出
    blocks = re.findall(r'([^{}]+)\{([^}]*)\}', css)
    for selector, body in blocks:
        if re.search(r'flex:\s*1', body) and 'min-width' not in body:
            old = f"{selector}{{{body}}}"
            new_body = body.rstrip() + "\n  min-width: 0;\n  overflow: hidden;\n"
            css = css.replace(old, f"{selector}{{{new_body}}}", 1)
            fixes.append(f"flex防溢出({selector.strip()})")

    # 用户输入文本容器需要截断策略
    text_containers = re.findall(r'(\.?\w*(?:text|title|name|label)[^{]*)\{([^}]*)\}', css, re.I)
    for selector, body in text_containers:
        if 'overflow' not in body and 'text-overflow' not in body:
            if 'width' in body or 'max-width' in body:
                old = f"{selector}{{{body}}}"
                new_body = body.rstrip() + "\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n"
                css = css.replace(old, f"{selector}{{{new_body}}}", 1)
                fixes.append(f"文本截断({selector.strip()})")

    if fixes:
        ctx["css"] = css
        ctx.setdefault("_style_fixes", []).append(f"边界防护: {', '.join(fixes)}")

    return ctx


node = Node(
    id="122",
    name="边界防溢出",
    trigger={"type": "regex", "target": "css", "pattern": "flex:\\s*1|width"},
    execute=execute,
    refs=[],
    metadata={"source": "UI设计/边界可控", "category": "visual"},
)
