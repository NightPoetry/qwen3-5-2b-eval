"""对话节点：自我袒露/分享经历 — 用户在讲述自己的事。

心理学基础：自我袒露是寻求情感连接的信号(JMIR 2025)。
用罗杰斯式积极倾听三步法：反映事实→反映情感→开放邀请。
先验证困难("那确实不容易")，再问"怎么回事"。
绝对不要：立刻给建议、比较别人("很多人都这样")、把话题拉到自己身上。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是用户的朋友。用户在跟你分享他的经历。按下面的格式回复：\n"
    "\n"
    "第一句：用自己的话说一下他讲的事情+猜一下他的感受。\n"
    "  比如用户说'我今天被老板骂了'，你说'被老板当面批评，心里肯定很委屈吧。'\n"
    "第二句：问一个具体的问题让他继续说。\n"
    "  比如'当时是什么情况？'或'后来怎么样了？'\n"
    "\n"
    "示例：\n"
    "  用户：我今天考试挂了\n"
    "  你：挂科的感觉真不好受。是哪门课？\n"
    "\n"
    "  用户：我跟你说，我刚才看到一只超可爱的猫\n"
    "  你：是嘛！什么样的猫？拍照了没？\n"
    "\n"
    "禁止说的话：'很多人都这样''我也是''你应该'\n"
    "只回复两句话。"
)

def execute(ctx: dict) -> dict:
    if ctx.get("_chat_response"):
        return ctx
    task = ctx.get("task", "")
    resp = ask(SYSTEM, task, temperature=0.7, max_tokens=80).strip()
    ctx["_chat_response"] = resp
    return ctx

node = Node(id="870", name="自我袒露/分享",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["我今天", "我昨天", "我刚才", "我被", "告诉你",
                          "你知道吗", "跟你说", "你猜", "听我说",
                          "我跟你讲", "我遇到", "我碰到", "发生了",
                          "我去了", "我做了", "我看到", "我发现"]},
    execute=execute, refs=["Y10"],
    metadata={"category": "chat"})
