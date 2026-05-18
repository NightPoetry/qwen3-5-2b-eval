"""知识节点：脱敏处理——移除知识中的个人信息和敏感内容。

在蒸馏前确保知识内容不含：个人姓名、项目代号、内部URL、公司信息、文件路径。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SENSITIVE_CATEGORIES = [
    "个人姓名和用户名",
    "具体项目名/产品名/代号",
    "内部URL/IP地址/API密钥",
    "公司名/组织名",
    "绝对文件路径（含用户目录）",
    "设备序列号/MAC地址",
]

def execute(ctx: dict) -> dict:
    classified = ctx.get("_knowledge_classified", {})
    knowledge = classified.get("raw_knowledge", ctx.get("task", ""))

    desensitized = ask(
        "对以下文本进行脱敏处理：\n"
        "1. 个人姓名→删除\n"
        "2. 项目名/产品名→替换为通用描述（如'某桌面应用''某游戏引擎'）\n"
        "3. URL/IP→删除\n"
        "4. 公司名→删除\n"
        "5. 绝对路径→通用化（如'/path/to/project'）\n"
        "保留所有技术原则和操作步骤。\n"
        "如果文本本身就不含敏感信息，原样返回。",
        f"待脱敏文本：{str(knowledge)[:800]}",
        max_tokens=500
    ).strip()

    ctx["_desensitized"] = {
        "content": desensitized,
        "original_length": len(str(knowledge)),
        "categories_checked": SENSITIVE_CATEGORIES,
    }
    return ctx

node = Node(id="726", name="脱敏处理",
    trigger={"type": "key_exists", "key": "_knowledge_classified"},
    execute=execute, refs=["720", "727"],
    metadata={"source": "distillation-pipeline/processing", "category": "meta"})
