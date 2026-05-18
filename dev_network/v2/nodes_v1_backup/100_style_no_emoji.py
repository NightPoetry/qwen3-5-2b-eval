"""知识节点：代码中禁用emoji和装饰性内容。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """扫描所有生成代码，移除emoji和装饰性注释。"""
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F6FF]"
    )
    decoration_patterns = [
        r'[/]{2}\s*={3,}.*',        # // ========
        r'[/]{2}\s*-{3,}.*',        # // --------
        r'[/]{2}\s*\*{3,}.*',       # // ********
        r'/\*\s*={3,}.*?\*/',       # /* ====...*/
    ]

    for key in ("html", "css", "js", "raw_html", "raw_css", "raw_js"):
        content = ctx.get(key)
        if not content:
            continue
        # 移除emoji
        cleaned = emoji_pattern.sub("", content)
        # 移除装饰性分隔符注释
        for pat in decoration_patterns:
            cleaned = re.sub(pat, "", cleaned)
        if cleaned != content:
            ctx[key] = cleaned
            ctx.setdefault("_style_fixes", []).append(f"{key}: 移除emoji/装饰")
    return ctx


node = Node(
    id="100",
    name="禁用emoji和装饰",
    trigger={"type": "key_exists", "key": "html"},
    execute=execute,
    refs=["101"],
    metadata={"source": "编程规范/严谨代码风格", "category": "code_quality"},
)
