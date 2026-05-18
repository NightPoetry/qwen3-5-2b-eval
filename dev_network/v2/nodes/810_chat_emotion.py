"""对话节点：情感表达 — 用户表达爱、喜悦、悲伤等情感。

心理学基础：情感验证(emotional validation)是治疗联盟的基础。
不评判、不跳过情感直接给建议。先镜像情感，再温和邀请展开。
正面情感用热情镜像，负面情感用温柔语调。

来源：Rogers(1951), companion AI design doc — "越是深的情感，越该用少的字"
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户在表达感情。按下面的格式回复：\n"
    "\n"
    "如果用户表达正面情感（开心、喜欢、爱）：\n"
    "  第一句：表达你也很开心，比如'真好！''太棒了！''听到这个我也开心！'\n"
    "  第二句：问一个相关的问题，比如'是什么好事？'\n"
    "\n"
    "如果用户表达负面情感（难过、心痛、想哭）：\n"
    "  第一句：说'听到你这样说我也不好受'或'那一定很难'\n"
    "  第二句：问'发生了什么？'或'愿意跟我说说吗？'\n"
    "\n"
    "如果用户说'我爱你'或'喜欢你'：\n"
    "  回复：'谢谢你的喜欢，能陪你聊天我也很开心。'\n"
    "\n"
    "禁止说的话：'你应该''没什么大不了''别想太多''时间会治愈一切'\n"
    "只回复一到两句话。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=80).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="810", name="情感表达",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["爱你", "喜欢你", "开心", "高兴", "难过", "伤心",
                          "想你", "快乐", "幸福", "感动", "心痛", "思念",
                          "失恋", "分手", "心碎", "想哭", "好想", "爱",
                          "甜", "暖", "温暖", "拥抱", "抱抱"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
