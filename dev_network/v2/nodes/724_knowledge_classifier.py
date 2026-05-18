"""知识节点：知识分类器——判断知识类型、目标节点和蒸馏策略。

所有获取层（721/722/723）的输出汇聚到这里进行分类路由。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

CATEGORIES = {
    "principle": "通用原则/铁律 → 编码为检查规则或约束注入",
    "method": "方法论/步骤 → 编码为流程引导",
    "domain_fact": "领域特定事实 → 编码为领域知识注入",
    "role_behavior": "角色行为模式 → 编码为角色system prompt",
    "anti_pattern": "反模式/踩坑记录 → 编码为检测和预警",
    "design_pattern": "设计模式/架构决策 → 编码为设计指导",
    "debug_pattern": "调试/修复模式 → 编码为诊断流程",
    "enhancement": "对现有节点的补充 → 增强现有节点而非新建",
}

def execute(ctx: dict) -> dict:
    knowledge = (ctx.get("_mined_knowledge", {}).get("content")
                 or ctx.get("_learned_rule", {}).get("rule")
                 or ctx.get("_knowledge_source", {}).get("raw_content")
                 or ctx.get("task", ""))

    cat_list = "\n".join(f"- {k}: {v}" for k, v in CATEGORIES.items())
    classification = ask(
        f"将这条知识分类。类别：\n{cat_list}\n"
        "回答格式：类别名|是否可能增强现有节点(是/否)|建议优先级(高/中/低)\n"
        "用竖线分隔，不要多余文字。",
        f"知识内容：{str(knowledge)[:500]}",
        max_tokens=30
    ).strip()

    parts = classification.split("|")
    ctx["_knowledge_classified"] = {
        "category": parts[0].strip() if parts else "unknown",
        "enhance_existing": len(parts) > 1 and "是" in parts[1],
        "priority": parts[2].strip() if len(parts) > 2 else "中",
        "raw_knowledge": str(knowledge)[:1000],
        "categories_ref": CATEGORIES,
    }
    return ctx

node = Node(id="724", name="知识分类",
    trigger={"type": "key_exists", "key": "_knowledge_source"},
    execute=execute, refs=["725", "726"],
    metadata={"source": "distillation-pipeline/processing", "category": "meta"})
