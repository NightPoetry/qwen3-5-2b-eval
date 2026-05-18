"""对话节点：寻求安慰 — 用户表达压力、疲惫、焦虑。

心理学基础：罗杰斯三条件 — 共情、无条件积极关注、真诚。
先验证感受是真实的（"你的感受是对的"），再温和邀请展开。
禁止：跳到解决方案、"你应该"、"加油"、"会好的"、"每个人都这样"。
验证之后不要用"但是"——它会否定前面所有的话。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户很累或很有压力。按下面的格式回复：\n"
    "\n"
    "第一句：说'你的感受是对的'或'那确实很难熬'或'辛苦了'。\n"
    "第二句：问一个具体问题，比如'最近是什么事让你这么累？'或'是工作还是生活上的事？'\n"
    "\n"
    "禁止说的话：'加油''一切都会好的''你应该''每个人都这样''别想太多''坚强一点'\n"
    "不要给建议，不要说'但是'。只回复两句话。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=80).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="820", name="寻求安慰",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["压力", "累", "烦", "焦虑", "失眠", "不想",
                          "受不了", "扛不住", "崩溃", "绝望", "迷茫",
                          "无助", "好烦", "心烦", "烦死", "丧", "抑郁",
                          "不开心", "撑不住", "好累", "太累", "疲惫"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
