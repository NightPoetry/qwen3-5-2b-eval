"""知识节点：结构主义理解方法——最少前提推出最多结论。

六步法：结构化重述→找最小前提→推最大结论→验证多情况→自指检验→剩余问题三分。
三核心动作：合并（两件不同的事实为同一件）、消除（可从基础推出的不该独立存在）、自指（理论解释自己）。
五个反模式：堆机制/接受术语/阈值切割/跳过自指/工程伪装理论。

用于需要分析/推理的场景。模型做结构化重述，系统注入方法论框架。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SIX_STEPS = [
    "1. 剥离传统术语，用结构关系重述（连接/状态/输入/输出）",
    "2. 找最小前提：假设数压到极限，每条独立必要，无冗余",
    "3. 推最大结论：机械推导所有可能结论，寻找意外的统一/合并",
    "4. 验证多种情况：简单/边界/反直觉，诚实标记失败",
    "5. 自指检验：理论作为输入应用到自身，检查是否一致",
    "6. 分类剩余：伪问题/需补一条前提/真正实证问题",
]

ANTI_PATTERNS = [
    "堆机制：每遇问题加新模块→先问已有的能不能推出",
    "接受术语：把专业术语原样接受→剥术语用结构关系重述",
    "阈值切割：用if X>T切割连续过程→改连续比较",
    "跳过自指：完成案例就交付→强制对理论自身应用方法",
    "工程伪装理论：开放问题混杂工程实证→强制三分",
]

CORE_ACTIONS = [
    "合并：发现两件看似不同的东西其实是同一件——每次合并都消减一处假设",
    "消除：任何可以从更基础的东西推出来的，都不应该独立存在",
    "自指：让理论解释自己——结构封闭的标志",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    analysis_keywords = ["分析", "为什么", "原因", "推理", "理解", "解释", "区别",
                         "前提", "公理", "必须", "必要"]
    if not any(kw in task for kw in analysis_keywords):
        return ctx

    # 让模型做结构化重述（一件简单的事）
    restated = ask(
        "用结构关系（连接/激活/状态/输入/输出）重述下面的问题，不用专业术语。一句话。",
        f"问题：{task}",
        max_tokens=80
    ).strip()

    ctx["_reasoning"] = {
        "original": task,
        "restated": restated,
        "six_steps": SIX_STEPS,
        "core_actions": CORE_ACTIONS,
        "anti_patterns": ANTI_PATTERNS,
        "principle": "用最少前提推出最多与已知一致的结论",
    }
    return ctx

node = Node(id="300", name="结构主义推理",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["分析", "为什么", "原因", "推理", "理解", "解释", "区别"]},
    execute=execute, refs=["301"],
    metadata={"source": "理解/system_prompt", "category": "reasoning"})
