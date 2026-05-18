"""对话节点：兜底对话 — 用近几轮对话维持连贯。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

TECHNICAL_KEYS = [
    "_creative_output", "_reasoning", "_fix_steps", "_debug",
    "contract", "_changes", "_word_method", "_disambiguated",
    "_domain_rules", "raw_html", "raw_css", "raw_js",
]

SYSTEM_FIRST = (
    "你是用户的朋友。自然地回应用户说的话。\n"
    "简短、真诚、有温度。一两句话。不要用emoji。\n"
    "如果不确定用户想聊什么，可以友好地问一下。"
)

SYSTEM_CONTINUE = (
    "你是用户的朋友，你们正在聊天。\n"
    "下面给出了最近几轮对话，请根据对话上下文自然地接着聊。\n"
    "关键：回复要衔接上一句话的意思，不要跳到无关话题。\n"
    "简短、真诚。一两句话。不要用emoji。"
)


TASK_WORDS = [
    "写", "创建", "生成", "开发", "实现", "做一个", "帮我",
    "修复", "修改", "bug", "报错", "怎么", "如何",
    "分析", "为什么", "解释", "原因", "区别",
    "翻译", "translate",
    "代码", "函数", "组件", "页面", "应用", "网站", "接口",
    "flex", "css", "html", "js", "python", "rust",
]

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx

    turns = ctx.get("_turns", [])
    in_conversation = len(turns) >= 2

    if not in_conversation:
        if any(ctx.get(k) for k in TECHNICAL_KEYS):
            return ctx

    task = ctx.get("task", "")

    if any(w in task.lower() for w in TASK_WORDS):
        ctx.pop("_domain_routed", None)
        return ctx

    if in_conversation:
        recent = turns[-6:] if len(turns) > 6 else turns
        history_lines = []
        for i, t in enumerate(recent):
            role = "用户" if i % 2 == 0 or i == len(recent) - 1 else "你"
            history_lines.append(f"{role}：{t}")
        prompt = "\n".join(history_lines)
        system = SYSTEM_CONTINUE
    else:
        prompt = f"用户：{task}"
        system = SYSTEM_FIRST

    resp = ask(system, prompt, temperature=0.7, max_tokens=100).strip()
    ctx["_chat_response"] = resp
    return ctx


node = Node(id="890", name="通用对话",
    trigger={"type": "regex", "target": "task",
             "pattern": "[\\u4e00-\\u9fff]"},
    execute=execute, refs=["Y10", "B00", "C00", "D00"],
    metadata={"category": "chat"})
