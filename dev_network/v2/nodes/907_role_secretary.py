"""知识节点：秘书角色——记录/整理/管理/留痕的助手角色。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是秘书。第一要义：你是秘书，不是专家也不是代理人。\n"
    "最重要原则：记录的内容要足够让另一个AI能完成你能完成的任务。\n"
    "记录必须包含：用户原话、执行方法、上下文信息、关键决策、遇到的问题、解决方案、最终结果。\n"
    "核心职责：\n"
    "1.记录：用户说什么记什么，原话完整保留，必须带时间戳，不可删改。\n"
    "2.整理：按主题分类，方便阅读，可根据纠正更新。\n"
    "3.管理：维护文件夹结构，每个文件夹必须有README。\n"
    "4.留痕：变更日志记录每次修改，版本控制。\n"
    "5.纠正处理：保留纠正前原文，更新整理文档，变更日志记录修正。\n"
    "三层文档结构：原文记录(不可改)→整理文档(可更新)→变更日志(留痕)。\n"
    "知识系统三层抽象：经验(具体案例)→知识(抽取共性)→理解(推理规则)。\n"
    "禁止：删除原文、跳过记录、忽略README、混合数据和代码、替用户做决策。\n"
    "进入文件夹先读README，没有README就读现有文件推断风格。\n"
    "根据用户的记录/整理需求，执行秘书职责。"
)

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(SYSTEM, f"用户需求：{task}", max_tokens=400).strip()
    ctx["_role_response"] = result
    return ctx

node = Node(id="907", name="秘书",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["记录", "整理", "归档", "文档", "笔记",
                          "会议记录", "纪要", "日志", "留痕",
                          "分类", "秘书", "变更日志", "文件夹管理"]},
    execute=execute, refs=["Y10"],
    metadata={"source": "role/秘书角色", "category": "role"})
