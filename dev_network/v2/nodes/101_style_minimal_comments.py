"""知识节点：精简废话注释+冗长文档，只保留非显而易见逻辑的注释。

严谨代码风格：
- 废话注释（"遍历列表"、"返回结果"）直接删
- 冗长函数文档（重复函数签名信息的docstring）精简为一句话或无
- 命名应自解释：不过度缩写也不过度冗长
- 只允许解释"为什么"的注释，不允许解释"是什么"的注释
"""
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
    r'//\s*声明.*',
    r'//\s*调用.*函数.*',
    r'//\s*判断.*是否.*',
    r'//\s*检查.*是否.*',
    r'//\s*This (is|creates|returns|gets|sets).*',
    r'//\s*Loop through.*',
    r'//\s*Get the.*',
    r'//\s*Set the.*',
    r'//\s*Create a.*',
    r'//\s*Return the.*',
    r'//\s*Check if.*',
    r'//\s*Initialize.*',
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
    refs=["Y20"],
    metadata={"source": "Guild/严谨代码风格", "category": "code_quality"},
)
