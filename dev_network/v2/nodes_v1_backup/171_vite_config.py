"""知识节点：Vite配置适配 — base路径/资源加载。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """为Tauri/嵌入式场景生成正确的资源引用。"""
    html = ctx.get("html", "")
    if not html:
        return ctx

    # 确保所有资源引用使用相对路径
    import re
    # /assets/xxx → ./assets/xxx
    fixed = re.sub(r'((?:src|href)=["\'])/', r'\1./', html)
    if fixed != html:
        ctx["html"] = fixed
        ctx.setdefault("_style_fixes", []).append("资源路径改为相对路径(./)")

    return ctx


node = Node(
    id="171",
    name="资源路径修正",
    trigger={"type": "regex", "target": "html", "pattern": "(?:src|href)=[\"']/[^/]"},
    execute=execute,
    refs=[],
    metadata={"source": "Tauri桌面应用工程师/Vite", "category": "platform"},
)
