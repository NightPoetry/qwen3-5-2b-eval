"""知识节点：交互式调试——先关再加/隔离变量/二分定位/mock隔离。

当用户报告"不对""出bug了"时的诊断方法论。
反模式：让用户当测试员/用DOM事件模拟/console.log调试/改完宣布修好/只测happy path。
正解：先搭调试设施再修bug，数据证明>视觉印象。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

DEBUG_METHODS = [
    "先关再加：关掉怀疑的组件，看问题是否消失→隔离变量",
    "二分定位：对半注释代码，看问题在上半还是下半",
    "最小复现：去掉一切无关代码，只留问题相关的最小集",
    "从现象推根因：不被用户的猜测带偏，从实际现象独立推理",
    "多个错误分主次：先判断哪些是同一根因的不同表现",
    "mock隔离：分别测试前端和后端链路，不在混合状态中猜",
    "数据证明：修复前后用数值对比（如streamDeltas: 1→13），不靠目视",
]

DEBUG_ANTI_PATTERNS = [
    "让用户当测试员：改完说你试试→自己操作读结果截图",
    "DOM事件模拟：el.click()在不同WebView不可靠→直接调用业务函数",
    "console.log调试：AI读不到浏览器控制台→可远程读取的结构化日志",
    "改完宣布修好：没有验证→用数据或截图证明",
    "只测happy path：忽略边缘场景→mock模拟各种异常",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    if not any(kw in task for kw in ["bug", "错", "问题", "不对", "坏了", "修"]):
        return ctx

    # 让模型做现象描述（一件简单事）
    symptom = ask(
        "用一句话描述用户遇到的问题现象。只描述现象不猜原因。",
        f"用户说：{task}",
        max_tokens=50
    ).strip()

    ctx["_debug"] = {
        "symptom": symptom,
        "methods": DEBUG_METHODS,
        "anti_patterns": DEBUG_ANTI_PATTERNS,
        "principle": "先搭调试设施再修bug——没有观测能力的修复是盲修",
    }
    return ctx

node = Node(id="420", name="交互式调试",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["bug", "错", "问题", "不对", "坏了", "修复", "调试"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "Skills/交互调试+knowledge/debugging", "category": "quality"})
