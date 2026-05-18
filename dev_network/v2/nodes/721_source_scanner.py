"""知识节点：知识源扫描——从多种来源检测可蒸馏的新知识。

扫描文档目录、对话记录、执行日志，找出尚未被节点网络覆盖的知识。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SOURCE_TYPES = {
    "document": "md/txt文件，Guild/Skills/knowledge等目录下的知识文档",
    "chat_log": "对话历史中反复出现的模式、用户纠正、有效解决方案",
    "exec_trace": "节点执行轨迹中的失败/降级/缺失信号",
    "feedback": "用户明确反馈：修正、确认、新需求",
    "external": "API文档、开源项目README、技术博客等外部来源",
}

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    source_list = "\n".join(f"- {k}: {v}" for k, v in SOURCE_TYPES.items())

    source_type = ask(
        "判断这段内容来自哪种知识来源。\n"
        f"来源类型：\n{source_list}\n"
        "只回答类型名（document/chat_log/exec_trace/feedback/external）。",
        f"内容：{task[:400]}",
        max_tokens=15
    ).strip()

    ctx["_knowledge_source"] = {
        "type": source_type,
        "raw_content": task[:1000],
        "source_types": SOURCE_TYPES,
    }
    return ctx

node = Node(id="721", name="知识源扫描",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["学习", "记住", "提取", "发现", "观察到",
                          "经验", "教训", "模式", "规律"]},
    execute=execute, refs=["724"],
    metadata={"source": "distillation-pipeline/acquisition", "category": "meta"})
