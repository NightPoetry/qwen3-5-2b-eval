"""内容生成节点 — 模型生成纯文本。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

TOPICS = [
    ("系统编排让2B模型写代码", "小模型通过管线分解完成复杂代码生成"),
    ("可执行知识网络", "从被动数据到主动程序的知识组织范式"),
    ("认知极限实验报告", "2B参数模型的能力边界与绕过策略"),
    ("事件层模板化", "确定性代码取代模型生成达成100%正确"),
    ("网状知识路由", "邻接可见与触发门控让知识按需激活"),
]

def execute(ctx: dict) -> dict:
    if ctx.get("_mode") == "modify":
        return ctx

    intro = ask("只输出纯文本，不要markdown。",
        "写50字技术博客简介：你研究让小型AI模型通过系统编排完成复杂任务。",
        temperature=0.7, max_tokens=100).strip()

    posts = []
    for title, desc in TOPICS:
        summary = ask("只输出一句话（20字以内），纯文本。",
            f"一句话概括：{desc}", temperature=0.7, max_tokens=50
        ).strip().strip('"\'')

        body_raw = ask("技术博客作者。3段正文（每段40-60字），纯文本，段间空行。",
            f"为《{title}》写正文。主题：{desc}", temperature=0.7, max_tokens=300)
        body = [p.strip() for p in body_raw.strip().split("\n") if p.strip()][:3]
        posts.append({"title": title, "summary": summary, "body": body})

    ctx["blog"] = {"intro": intro, "posts": posts, "title": "AI Systems Research"}
    return ctx

node = Node(
    id="010_c", name="内容生成",
    trigger={"type": "key_exists", "key": "_mode"},
    execute=execute, refs=["100_h"],
)
