"""节点：HTML验证修复 — 确定性操作。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node


def execute(ctx: dict) -> dict:
    raw = ctx.get("raw_html", "")
    issues = []

    # 去 markdown
    if "```" in raw:
        blocks = re.findall(r'```(?:\w+)?\n(.*?)```', raw, re.DOTALL)
        if blocks:
            raw = blocks[0]

    # DOCTYPE
    if "<!DOCTYPE" not in raw.upper():
        raw = "<!DOCTYPE html>\n" + raw
        issues.append("添加DOCTYPE")

    # viewport
    if "viewport" not in raw:
        pos = raw.find("<head")
        if pos >= 0:
            close = raw.find(">", pos)
            if close >= 0:
                meta = '\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                raw = raw[:close+1] + meta + raw[close+1:]
                issues.append("添加viewport")

    # charset
    if "charset" not in raw.lower():
        pos = raw.find("<head")
        if pos >= 0:
            close = raw.find(">", pos)
            if close >= 0:
                raw = raw[:close+1] + '\n    <meta charset="UTF-8">' + raw[close+1:]
                issues.append("添加charset")

    # 重复ID修复
    id_occurrences = re.findall(r'<(\w+)[^>]*\bid=[\'"](\w+)[\'"]', raw)
    id_counts = {}
    for tag, eid in id_occurrences:
        id_counts.setdefault(eid, []).append(tag)
    for eid, tags in id_counts.items():
        if len(tags) > 1:
            for wtag in ("div", "section", "article", "main", "header", "footer", "nav"):
                if wtag in tags:
                    raw = re.sub(rf'(<{wtag})\s+id=[\'\"]{eid}[\'\"]([\s>])', rf'\1\2', raw, count=1)
                    issues.append(f"移除{wtag}上的重复ID#{eid}")
                    break

    ctx["html"] = raw
    ctx["html_issues"] = issues
    return ctx


node = Node(
    id="070",
    name="HTML验证",
    trigger={"type": "key_exists", "key": "raw_html"},
    execute=execute,
    refs=["080", "100"],
)
