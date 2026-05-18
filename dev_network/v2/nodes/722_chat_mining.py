"""知识节点：对话挖掘——从聊天记录中提取可复用的知识模式。

检测对话中值得蒸馏的信号：用户纠正、反复出现的问题、有效解决方案、确认的非显然做法。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

MINING_SIGNALS = [
    "用户纠正：'不是这样的''不要这么做''应该用X而不是Y'",
    "反复出现：同类问题在多次对话中重复",
    "有效方案：用户确认'对''就是这样''完美'的解决路径",
    "非显然做法：用户接受了一个违反直觉的方案",
    "失败模式：某种方法反复失败的记录",
]

def execute(ctx: dict) -> dict:
    content = ctx.get("_chat_history", ctx.get("task", ""))

    analysis = ask(
        "分析这段对话内容，提取值得保留的知识。关注以下信号：\n"
        "1. 用户纠正了哪些错误认知？\n"
        "2. 哪些解决方案被确认有效？\n"
        "3. 有没有违反直觉但正确的做法？\n"
        "4. 有没有反复失败的模式？\n"
        "如果没有值得提取的知识，回答'无'。\n"
        "如果有，用一句话描述核心知识点。",
        f"对话内容：{str(content)[:800]}",
        max_tokens=150
    ).strip()

    if analysis and analysis != "无":
        ctx["_mined_knowledge"] = {
            "content": analysis,
            "source": "chat_mining",
            "signals": MINING_SIGNALS,
        }
    return ctx

node = Node(id="722", name="对话挖掘",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["聊天记录", "对话历史", "之前说过", "上次",
                          "回顾", "复盘"]},
    execute=execute, refs=["724"],
    metadata={"source": "distillation-pipeline/acquisition", "category": "meta"})
