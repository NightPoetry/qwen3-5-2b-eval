"""知识节点：暗色主题CSS基础变量注入。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

DARK_THEME_VARS = """
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #21262d;
  --text-primary: #f0f6fc;
  --text-secondary: #c9d1d9;
  --text-muted: #8b949e;
  --text-dim: #484f58;
  --border: #21262d;
  --accent: #388bfd;
  --success: #3dba78;
  --warning: #e8853a;
  --error: #f85149;
  --radius: 6px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
}
"""


def execute(ctx: dict) -> dict:
    css = ctx.get("css", "")
    if not css:
        return ctx

    # 检查是否已有CSS变量定义
    if ":root" in css and "--" in css:
        return ctx

    # 检查是否是暗色主题(背景色深)
    if re.search(r'background[^;]*#[0-2][0-2a-f]', css) or "dark" in ctx.get("task", "").lower():
        # 注入CSS变量
        ctx["css"] = DARK_THEME_VARS + "\n" + css
        ctx.setdefault("_style_fixes", []).append("注入暗色主题CSS变量")

    return ctx


node = Node(
    id="120",
    name="暗色主题变量",
    trigger={"type": "regex", "target": "css", "pattern": "background[^;]*#[0-2]"},
    execute=execute,
    refs=["121"],
    metadata={"source": "UI设计/语义一致", "category": "visual"},
)
