"""知识节点：事实校准 — 检查生成内容中的不准确声明。

用于内容生成场景（博客、文档）：
检查模型输出的文本中是否有未经验证的数字/比较/声明。
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

# 需要校准的模式
SUSPECT_PATTERNS = [
    (r'\d+[%倍x×]', "含有数字比较/百分比——需验证来源"),
    (r'(?:最|第一|唯一|首个)', "含有极端声明——需验证"),
    (r'(?:matches|approaches|接近|超过|碾压)', "含有比较性声明——需验证基线"),
    (r'(?:所有|总是|从不|绝对|肯定)', "含有全称断言——需谨慎"),
]


def execute(ctx: dict) -> dict:
    """扫描模型生成的文本内容，标记需校准项。"""
    # 检查所有可能含文本描述的字段
    text_fields = ["intro", "posts", "content_text"]
    calibration_warnings = []

    for field in text_fields:
        content = ctx.get(field)
        if not content:
            continue

        text = str(content)
        for pattern, reason in SUSPECT_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                calibration_warnings.append(f"{field}: {reason} ({matches[:3]})")

    if calibration_warnings:
        ctx.setdefault("_calibration", []).extend(calibration_warnings)

    return ctx


node = Node(
    id="160",
    name="事实校准",
    trigger={"type": "keyword", "target": "_input",
             "keywords": ["博客", "文章", "报告", "介绍", "blog"]},
    execute=execute,
    refs=[],
    metadata={"source": "校准/system_prompt", "category": "reasoning"},
)
