"""知识节点：词义消歧——区分同一词在不同上下文中的含义。

当任务描述中有歧义词时，让模型做消歧（一个简单问题）。
核心原则：一个词只有一个真正含义，所有用法都是灵活应用。
消歧是确定当前上下文中哪个灵活应用在生效。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

AMBIGUOUS_TERMS = {
    "绑定": ["数据绑定(data binding)", "事件绑定(addEventListener)", "音视频绑定(linkId)"],
    "模型": ["AI模型(LLM)", "数据模型(schema)", "心理模型(mental model)"],
    "状态": ["应用状态(state)", "UI状态(class)", "网络状态(connection)"],
    "渲染": ["DOM渲染(render)", "视频渲染(export)", "服务端渲染(SSR)"],
    "路由": ["URL路由(router)", "知识路由(knowledge routing)", "API路由(endpoint)"],
    "验证": ["表单验证(validation)", "身份验证(authentication)", "测试验证(verification)"],
    "链接": ["超链接(href)", "数据关联(ref)", "网络连接(socket)"],
    "节点": ["DOM节点(element)", "知识节点(knowledge node)", "网络节点(server)"],
    "容器": ["DOM容器(div)", "Docker容器(container)", "依赖注入容器(DI)"],
}

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    found_ambiguous = []

    for term, meanings in AMBIGUOUS_TERMS.items():
        if term in task:
            found_ambiguous.append((term, meanings))

    if not found_ambiguous:
        return ctx

    # 对每个歧义词，让模型消歧（一次一个简单问题）
    disambiguated = {}
    for term, meanings in found_ambiguous:
        options = " / ".join(meanings)
        result = ask(
            f"在下面的上下文中，'{term}'最可能指哪个含义？从选项中选一个，只回答选项。",
            f"上下文：{task}\n选项：{options}",
            max_tokens=30
        ).strip()
        disambiguated[term] = result

    ctx["_disambiguated"] = disambiguated
    return ctx

node = Node(id="310", name="词义消歧",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["绑定", "模型", "状态", "渲染", "路由", "验证"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "词义理解/skill", "category": "reasoning"})
