"""节点：ID一致性验证（跨文件）。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Node


def execute(ctx: dict) -> dict:
    contract = ctx.get("contract", {})
    html = ctx.get("html", "")
    js = ctx.get("js", "")
    issues = []

    if not html or not js:
        return ctx

    elements = contract.get("elements", [])
    js_refs = set(re.findall(r'getElementById\([\'"](\w+)[\'"]\)', js))

    for elem in elements:
        eid = elem["id"]
        tag = elem["tag"]

        # HTML检查
        if not re.search(rf'id=[\'\"]{eid}[\'\"' + r']', html):
            pos = html.find("</body>")
            if pos < 0:
                pos = len(html)
            if tag == "input":
                new_elem = f'    <input type="text" id="{eid}">\n'
            elif tag == "button":
                new_elem = f'    <button id="{eid}"></button>\n'
            else:
                new_elem = f'    <{tag} id="{eid}"></{tag}>\n'
            html = html[:pos] + new_elem + html[pos:]
            issues.append(f"HTML补#{eid}")

        # JS检查
        if eid not in js_refs:
            line = f"const {eid} = document.getElementById('{eid}');\n"
            dom_match = re.search(
                r"(addEventListener\(['\"]DOMContentLoaded['\"].*?(?:=>|function)\s*\{?\s*\n)", js
            )
            pos = dom_match.end() if dom_match else 0
            js = js[:pos] + line + js[pos:]
            js_refs.add(eid)
            issues.append(f"JS补#{eid}")

    ctx["html"] = html
    ctx["js"] = js
    ctx["id_issues"] = issues
    return ctx


node = Node(
    id="080",
    name="ID一致性验证",
    trigger={
        "type": "condition",
        "expr": "'html' in dir() or 'html' in ctx" if False else "True",
    },
    execute=execute,
    refs=["090"],
)

# 修正trigger：当html和js都准备好时触发
node.trigger = {"type": "key_exists", "key": "js"}
node.refs = ["090", "190", "200", "210"]
