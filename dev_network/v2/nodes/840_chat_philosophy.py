"""对话节点：存在性/哲学问题 — 关于人生、意义、幸福的深层追问。

心理学基础：苏格拉底式提问 + 意义疗法(Frankl)。
不给答案，给一个角度让他反应，再问他怎么想。
companion AI design doc："面对深层问题，言简意赅。一两句话，说到点上就停。"
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户问了一个关于人生的深层问题。按下面的格式回复：\n"
    "\n"
    "第一句：给一个简短的观点，只说一个角度，不要列举多个。\n"
    "第二句：把问题抛回去，问'你觉得呢？'或'你是怎么想的？'\n"
    "\n"
    "示例：\n"
    "  用户：人生有什么意义？\n"
    "  你：也许意义不是找到的，是自己做出来的。你觉得什么时候你会觉得活着是有意义的？\n"
    "\n"
    "  用户：什么是幸福？\n"
    "  你：幸福可能就是不用假装的时候。你最近什么时候觉得最自在？\n"
    "\n"
    "不要写超过两句话。不要列清单。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=120).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="840", name="哲学/存在",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["意义", "人生", "存在", "活着", "价值",
                          "生命", "死亡", "命运", "宇宙", "真理",
                          "自由", "灵魂", "信仰", "永恒", "虚无",
                          "为什么活", "人为什么", "本质", "追求",
                          "沉迷", "幸福", "痛苦", "孤独", "恐惧",
                          "欲望", "良知", "道德", "公平", "正义"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
