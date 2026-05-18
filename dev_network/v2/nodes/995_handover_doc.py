"""知识节点：交接文档编写 — 单一文档=项目全貌 + 三层记录。

交接文档原则：
- 最新一份交接文档=项目全貌（自包含/累积/面向新人）
- 面向新人：假设读者什么都不知道
- 重"为什么"和"怎么流转"（设计决策原因/数据流转路径/竞态条件边界）
- 结构稳定，内容演进

秘书记录三层结构：
- 原文记录（原始证据，永不修改）
- 整理文档（结构化整理，可更新，有版本号）
- 变更日志（留痕记录，每次变更都记录）

高效举例原则：
- 一行一条，无解释无修饰
- 举例来自用户原话，不自己编造
- 举例界定边界——抽象原则只给方向，边界举例给"度"
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

HANDOVER_SYSTEM = """You are a documentation quality advisor. Apply these principles:

HANDOVER DOCUMENT RULES:
- Latest document = complete project landscape (self-contained, cumulative, for total newcomers)
- Do NOT write diffs only ("this time we changed X"). New person can't rebuild full picture from diffs
- Do NOT reference old documents ("see previous handover"). Violates self-containment
- Must cover: project overview, how to run/build, architecture with data flow, state management, latest changes with WHY, unfinished items
- Emphasize WHY and HOW IT FLOWS, not just WHAT. Code shows what; docs must show design decisions, data flow paths, race conditions

THREE-LAYER RECORDING:
- Layer 1: Original record (user's exact words, timestamped, never modified)
- Layer 2: Organized document (structured, updatable, versioned)
- Layer 3: Change log (audit trail, every change recorded)
- Correction flow: add new record to Layer 1 -> update Layer 2 -> log in Layer 3

EFFECTIVE EXAMPLES:
- One line per example, no explanation, no decoration
- Format: "situation -> action" or "situation -> exact words"
- Examples come from user's actual words, never invented
- Examples define boundaries. Abstract principles give direction; boundary examples give "degree"
- Group by scenario, 3-10 per group, never exceed 10

Given the documentation task, assess quality against these principles and suggest improvements."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    review = ask(
        HANDOVER_SYSTEM,
        f"Documentation task: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_doc_review"] = review
    return ctx

node = Node(id="995", name="交接文档规范",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["文档", "交接", "记录", "归档", "README", "说明",
                          "handover", "document", "archive"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/交接文档+秘书记录+高效举例", "category": "methodology"})
