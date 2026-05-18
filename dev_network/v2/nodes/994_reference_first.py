"""知识节点：参考优先原则 — 反复写不对的时候先找参考。

核心：有参考先看参考。反复失败时不要继续盲试。

方法一 示例优先法：有示例->先看示例->按示例开发->别瞎搞
方法二 醉翁之意不在酒法：找不到文档时，下载已对接的项目，从中逆向找对接方法

判断流程：有官方示例?->有就先看; 无就找已对接项目

也适用于代码风格一致性：写入前必须先读取目标文件夹现有文档分析风格特征。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

REFERENCE_SYSTEM = """You are a reference-finding advisor. When someone is stuck repeatedly failing at a task:

REFERENCE-FIRST PRINCIPLE:
- Have official examples? -> Read examples first -> develop following examples -> don't improvise
- No official examples? -> Find existing projects that already solved it -> download -> reverse-engineer their approach

REVERSE ENGINEERING METHOD:
1. Identify a project that already integrates with the target
2. Download/read that project's source code
3. Find how they solved the integration
4. Follow the same approach

CODE STYLE CONSISTENCY:
- Before writing into a folder, READ existing documents first
- Priority: README.md > same-topic docs > same-type docs > recent docs
- Extract style features: heading style, paragraph length, list format, code block style, emphasis usage, tone, length
- Write new content matching the extracted style
- Forbidden: writing without reading first, ignoring README rules, forcing another folder's style

Given the user's situation, identify whether they need a reference, suggest where to find one, and advise the approach."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    advice = ask(
        REFERENCE_SYSTEM,
        f"User is working on: {task[:300]}",
        max_tokens=120
    ).strip()
    ctx["_reference_advice"] = advice
    return ctx

node = Node(id="994", name="参考优先",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["不对", "写不出", "报错", "失败", "不会", "怎么做",
                          "对接", "集成", "integration", "接口"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/参考优先+代码风格一致性", "category": "methodology"})
