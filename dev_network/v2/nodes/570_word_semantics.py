"""知识节点：词义理解方法论——一个词只有一个真正含义，所有用法都是灵活应用。

五步法：提取真正含义→理解语法用处→语义必然匹配→本义直译验证→灵活应用边界。
三核心动作：统一（多释义归一）、理解（语法真正原因）、验证（真正含义覆盖所有用法）。
本方法是结构主义理解方法在语言语义领域的特例：最少前提=真正含义，最多结论=所有用法。

适用于语义分析、词源探究、介词用法、固定搭配质疑等场景。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

FIVE_STEPS = [
    "1. 提取真正含义（词源/构词分解，不是词典释义）",
    "2. 理解语法用处（这个语法存在的真正原因是什么）",
    "3. 语义必然匹配（词汇含义 + 语法用处 = 用法必然）",
    "4. 本义直译验证（无润色、无延伸、必自洽）",
    "5. 灵活应用边界（一级核心/二级延伸/三级小众）",
]

ANTI_PATTERNS = [
    "堆释义：每次新用法加新释义→先问真正含义能否推出",
    "接受固定搭配：不问语法真正原因→问语义必然",
    "中文释义切割：用翻译反定义→用词源正向提取",
    "跳过验证：不检验真正含义全覆盖→用全用法统一验证",
    "语法终点：用语法规则解释语义→语义优先，语法后置",
]

PREPOSITION_MAP = {
    "for": "定向划拨、主观指派归属",
    "at": "纯客观点位标定，无主观划拨",
    "on": "依附于某载体表面",
    "in": "归入大范围圈层容纳",
}

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    word_match = False
    for kw in ["词", "word", "含义", "为什么用", "介词", "固定搭配", "本义",
               "词源", "语法"]:
        if kw in task:
            word_match = True
            break

    if not word_match:
        return ctx

    # 让模型判断用户问的是哪个词/介词（一件简单事）
    target = ask(
        "用户在问哪个词或介词的含义/用法？只回答那个词，一个词。如果不确定回答'未知'。",
        f"用户说：{task}",
        max_tokens=15
    ).strip()

    ctx["_word_method"] = {
        "target_word": target,
        "steps": FIVE_STEPS,
        "anti_patterns": ANTI_PATTERNS,
        "preposition_ref": PREPOSITION_MAP,
        "core_actions": [
            "统一：多个释义归到同一真正含义的不同灵活应用",
            "理解：明白语法用处的真正原因",
            "验证：用真正含义解释所有用法",
        ],
        "principle": "一个词只有一个真正含义。所有用法都是灵活应用。语义必然 > 固定搭配。",
    }
    return ctx

node = Node(id="570", name="词义理解",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["词义", "词源", "介词", "为什么用", "固定搭配", "本义",
                          "英语", "语法"]},
    execute=execute, refs=["300"],
    metadata={"source": "Skills/词义理解", "category": "reasoning"})
