"""知识节点：抗乱码 — UTF-8多字节截断防御。

核心：AI写入文件的每个字符都必须完整。工具层面的字节截断是系统性风险。
乱码进入提示词会污染AI对话上下文，引发连锁错误。

防御原则：
1. 写入后立即校验：grep -rn $'\\xef\\xbf\\xbd' (U+FFFD替换字符)
2. 关键内容写后回读：抽查关键中文短语
3. 避免极长字符串中嵌入中文（>500字符截断风险上升）
4. 批量写入逐文件校验

JSONL规范（逐行JSON）：
- 每行以{开始以}结束，可独立JSON.parse
- 字符串内换行必须转义
- 每行有唯一id字段
- 追加写入（不重写整文件）
- 滑动窗口保持最近N行
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查生成代码中是否有UTF-8截断痕迹和JSONL格式问题。"""
    issues = []

    for key in ("html", "css", "js", "raw_html", "raw_css", "raw_js"):
        content = ctx.get(key, "")
        if not content:
            continue

        # 检查U+FFFD替换字符（UTF-8截断的标志）
        if "�" in content:
            count = content.count("�")
            issues.append(f"{key}: 发现{count}处U+FFFD替换字符——UTF-8截断")

        # 检查中文字符完整性（多字节字符后跟异常字节）
        try:
            content.encode("utf-8").decode("utf-8")
        except UnicodeError:
            issues.append(f"{key}: UTF-8编码/解码异常——可能有截断")

    # 检查JSONL格式的输出（如果有）
    jsonl = ctx.get("jsonl", "")
    if jsonl:
        lines = jsonl.strip().split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                issues.append(f"JSONL第{i+1}行: 空行——JSONL不允许空行")
                continue
            if not line.startswith("{") or not line.endswith("}"):
                issues.append(f"JSONL第{i+1}行: 不以{{开始或不以}}结束——非完整JSON对象")
            if line.endswith("},"):
                issues.append(f"JSONL第{i+1}行: 末尾有逗号——不是完整JSON")

    if issues:
        ctx.setdefault("_warnings", []).extend(issues)

    return ctx

node = Node(id="997", name="抗乱码校验",
    trigger={"type": "key_exists", "key": "html"},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/抗乱码+逐行JSON", "category": "code_quality"})
