"""知识节点：节点代码合成——根据分类和脱敏后的知识生成节点Python代码。

这是蒸馏管线的核心输出：把知识变成可执行的.py节点文件代码。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

NODE_TEMPLATE = '''"""知识节点：{name}——{description}
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        "{system_prompt}",
        f"{{input_field}}：{{task}}",
        max_tokens={max_tokens}
    ).strip()
    ctx["{output_key}"] = result
    return ctx

node = Node(id="{node_id}", name="{name}",
    trigger={{"type": "keyword", "target": "task",
             "keywords": {keywords}}},
    execute=execute, refs={refs},
    metadata={{"source": "{source}", "category": "{category}"}})
'''

def execute(ctx: dict) -> dict:
    classified = ctx.get("_knowledge_classified", {})
    desensitized = ctx.get("_desensitized", {}).get("content", "")
    category = classified.get("category", "unknown")
    dup_check = ctx.get("_duplicate_check", {})

    if dup_check.get("action") == "skip":
        ctx["_synthesized"] = {"action": "skip", "reason": "already covered"}
        return ctx

    design = ask(
        "根据知识内容，设计一个可执行节点。回答以下字段（用|分隔）：\n"
        "节点名称(4字以内)|一句话描述|5个触发关键词(逗号分隔)|"
        "system prompt核心内容(编码知识精华,100字以内)|输出key名",
        f"知识类别：{category}\n脱敏内容：{desensitized[:500]}",
        max_tokens=200
    ).strip()

    parts = design.split("|")
    ctx["_synthesized"] = {
        "action": dup_check.get("action", "create"),
        "design": design,
        "name": parts[0].strip() if parts else "未命名",
        "description": parts[1].strip() if len(parts) > 1 else "",
        "keywords": parts[2].strip() if len(parts) > 2 else "",
        "system_prompt": parts[3].strip() if len(parts) > 3 else "",
        "output_key": parts[4].strip() if len(parts) > 4 else "_result",
        "template": NODE_TEMPLATE,
        "category": category,
    }
    return ctx

node = Node(id="727", name="节点代码合成",
    trigger={"type": "key_exists", "key": "_desensitized"},
    execute=execute, refs=["728"],
    metadata={"source": "distillation-pipeline/generation", "category": "meta"})
