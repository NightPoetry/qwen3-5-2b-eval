"""知识节点：精简废话注释，只保留解释非显而易见逻辑的注释。"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

# 废话注释模式（中英文）
USELESS_PATTERNS = [
    r'//\s*遍历.*',
    r'//\s*获取.*元素.*',
    r'//\s*返回.*结果.*',
    r'//\s*创建.*变量.*',
    r'//\s*定义.*函数.*',
    r'//\s*设置.*值.*',
    r'//\s*初始化.*',
    r'//\s*This (is|creates|returns|gets|sets).*',
    r'//\s*Loop through.*',
    r'//\s*Get the.*',
    r'/\*\*?\s*\n\s*\*\s*(获取|设置|创建|返回|遍历).*\n\s*\*/',
]


def execute(ctx: dict) -> dict:
    js = ctx.get("js", "")
    if not js:
        return ctx

    lines = js.split("\n")
    result = []
    removed = 0

    for line in lines:
        stripped = line.strip()
        is_useless = False
        for pat in USELESS_PATTERNS:
            if re.match(pat, stripped):
                is_useless = True
                removed += 1
                break
        if not is_useless:
            result.append(line)

    if removed > 0:
        ctx["js"] = "\n".join(result)
        ctx.setdefault("_style_fixes", []).append(f"移除{removed}条废话注释")

    return ctx


node = Node(
    id="101",
    name="精简废话注释",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute,
    refs=[],
    metadata={"source": "编程规范/严谨代码风格", "category": "code_quality"},
)
