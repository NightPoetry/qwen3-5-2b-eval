"""知识节点：严谨代码风格 — 禁emoji/装饰/废话日志/感叹号。

融合：严谨代码风格原则（极简/精确/纯粹，任何与逻辑无关的内容都是噪音）。
禁止项：emoji、装饰性分隔线、废话文档、日志装饰(===)、感叹号/语气词、commit emoji。
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """扫描所有生成代码，移除emoji、装饰性内容和日志装饰。"""
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F6FF]"
    )
    decoration_patterns = [
        r'[/]{2}\s*={3,}.*',        # // ========
        r'[/]{2}\s*-{3,}.*',        # // --------
        r'[/]{2}\s*\*{3,}.*',       # // ********
        r'/\*\s*={3,}.*?\*/',       # /* ====...*/
    ]
    # 日志装饰模式
    log_decoration_patterns = [
        r'print\s*\(\s*["\']={3,}',            # print("====...")
        r'print\s*\(\s*["\']>{3,}',            # print(">>>...")
        r'print\s*\(\s*["\']-{3,}',            # print("---...")
        r'console\.log\s*\(\s*["\']={3,}',     # console.log("====...")
        r'console\.log\s*\(\s*["\']>{3,}',     # console.log(">>>...")
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
        # 移除日志装饰行
        for pat in log_decoration_patterns:
            cleaned = re.sub(pat + r'.*', "", cleaned)
        if cleaned != content:
            ctx[key] = cleaned
            ctx.setdefault("_style_fixes", []).append(f"{key}: 移除emoji/装饰/日志装饰")
    return ctx


node = Node(
    id="100",
    name="禁用emoji和装饰",
    trigger={"type": "key_exists", "key": "html"},
    execute=execute,
    refs=["101"],
    metadata={"source": "Guild/严谨代码风格", "category": "code_quality"},
)
