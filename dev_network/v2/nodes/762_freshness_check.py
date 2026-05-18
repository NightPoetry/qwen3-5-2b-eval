"""知识节点：新鲜度检查——检测过时或失效的节点知识。

知识会过时：API变更、框架升级、方法论被更好的替代。
过时的节点比缺失的节点更危险——它给出错误的确定性答案。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

STALENESS_SIGNALS = [
    "节点引用的API/框架版本已过时（如Tauri v1→v2）",
    "节点推荐的做法被新的最佳实践取代",
    "节点假设的运行环境已不存在",
    "用户多次在该节点激活后纠正其输出",
    "节点内的规则与新增节点的规则矛盾",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    assessment = ask(
        "判断以下节点知识是否可能过时：\n"
        "过时信号：\n" + "\n".join(f"- {s}" for s in STALENESS_SIGNALS) + "\n\n"
        "回答：新鲜/可能过时/确定过时，加一句原因。",
        f"节点内容：{task[:500]}",
        max_tokens=60
    ).strip()

    ctx["_freshness"] = {
        "assessment": assessment,
        "stale": "过时" in assessment,
    }
    return ctx

node = Node(id="762", name="新鲜度检查",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["过时", "outdated", "更新", "版本", "升级",
                          "已弃用", "deprecated"]},
    execute=execute, refs=["721"],
    metadata={"source": "distillation-pipeline/self-improvement", "category": "meta"})
