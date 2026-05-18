"""知识节点：反馈学习——从用户纠正和确认中提取规则。

纠正 = 模型做错了，用户告诉正确做法 → 提取"不要X，应该Y"规则
确认 = 模型做了一个非显然的选择，用户肯定了 → 提取"在Z场景下，Y是对的"规则
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    rule = ask(
        "从这段用户反馈中提取一条可复用的规则。\n"
        "如果是纠正：格式为'不要[错误做法]，应该[正确做法]，因为[原因]'\n"
        "如果是确认：格式为'在[场景]下，[做法]是正确的，因为[原因]'\n"
        "如果不包含可提取的规则，回答'无'。",
        f"用户反馈：{task[:500]}",
        max_tokens=100
    ).strip()

    if rule and rule != "无":
        ctx["_learned_rule"] = {
            "rule": rule,
            "source": "user_feedback",
        }
    return ctx

node = Node(id="723", name="反馈学习",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["不对", "不是", "不要", "应该", "正确的是",
                          "记住", "以后", "别再"]},
    execute=execute, refs=["724"],
    metadata={"source": "distillation-pipeline/acquisition", "category": "meta"})
