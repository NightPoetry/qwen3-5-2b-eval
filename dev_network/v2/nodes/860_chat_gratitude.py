"""对话节点：感谢/赞美 — 用户表达感谢或夸奖。

心理学基础：互惠规范(Gouldner 1960) + 感恩心理学。
接受夸奖要自然，不过度谦虚也不膨胀。
注意：过度迎合(sycophancy)会降低用户的自我反思意愿(2025研究)。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户在感谢你或夸你。\n"
    "像朋友一样自然地接受，说'不客气'或'能帮到你我也开心'。\n"
    "不要过度谦虚说'我做得不好'，也不要太自大。一句话就好。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=50).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="860", name="感谢/赞美",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["谢谢", "感谢", "你真好", "你真棒", "太好了",
                          "辛苦了", "多谢", "谢啦", "感恩", "厉害",
                          "你最好了", "太厉害", "牛", "给力", "棒"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
