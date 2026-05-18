"""知识节点：Web前端通用模式——API请求/localStorage/静态资源。

在JS生成后验证常见前端陷阱。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    js = ctx.get("js", "")
    if not js: return ctx
    fixes = []

    # fetch不检查.ok
    if "fetch(" in js and ".ok" not in js and "catch" not in js:
        fixes.append("fetch()未检查.ok也无catch——HTTP非2xx时不会throw")

    # JSON.parse不try-catch
    if "JSON.parse" in js and "try" not in js:
        fixes.append("JSON.parse无try-catch——用户可能手改localStorage导致解析失败")

    # localStorage token过期
    if "localStorage" in js and "token" in js.lower():
        fixes.append("localStorage中的token在服务端重启后失效，需验证失败时清除")

    # encodeURIComponent在路径中
    if "encodeURIComponent" in js:
        fixes.append("encodeURIComponent会编码/为%2F，确保后端能解码")

    if fixes:
        ctx.setdefault("_warnings", []).extend(fixes)
    return ctx

node = Node(id="240", name="前端模式检查",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute, refs=["Y30"],
    metadata={"source": "knowledge/web-frontend-embedded", "category": "quality"})
