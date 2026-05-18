"""
2B能力多角度测试 — 通过v2引擎90节点网络测试。

测试维度：
  1. 代码生成（待办应用）
  2. 对话/推理（分析问题）
  3. 词义理解（英语语义）
  4. 内容创作（博客文章）
  5. 调试诊断（给出bug描述）
  6. 交互设计（设计用户流程）
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine import Engine
from llm import ask

DIVIDER = "=" * 60


def load_engine():
    engine = Engine()
    engine.load_from_dir(Path(__file__).parent / "nodes")
    return engine


def test_conversation():
    """测试1：多轮对话能力（每轮独立隔离调用）"""
    print(f"\n{DIVIDER}")
    print("测试1：对话能力（隔离对话，每轮一个简单问题）")
    print(DIVIDER)

    turns = [
        ("回答用户的问题。用中文。一句话。",
         "什么是系统编排？"),
        ("回答用户的问题。用中文。一句话。",
         "它和直接让AI一次性完成任务有什么区别？"),
        ("回答用户的问题。用中文。一句话。",
         "2B参数的模型能做什么不能做什么？"),
    ]

    for i, (sys_msg, user_msg) in enumerate(turns):
        reply = ask(sys_msg, user_msg, temperature=0.3, max_tokens=100)
        print(f"  Q{i+1}: {user_msg}")
        print(f"  A{i+1}: {reply.strip()}")
        print()


def test_reasoning(engine):
    """测试2：推理/分析能力（通过节点网络）"""
    print(f"\n{DIVIDER}")
    print("测试2：推理分析（引擎触发推理节点链）")
    print(DIVIDER)

    ctx = {
        "task": "分析一下为什么小模型做不好组合任务",
        "_entry": "300",
    }

    # 手动触发推理节点链
    for nid in ["300", "301", "380"]:
        node = engine.nodes.get(nid)
        if node and engine.check_trigger(node, ctx):
            ctx = node.execute(ctx)
            print(f"  [{nid}] {node.name}")

    if ctx.get("_reasoning"):
        r = ctx["_reasoning"]
        print(f"\n  原始问题: {r.get('original', '')}")
        print(f"  结构化重述: {r.get('restated', '')}")
        print(f"  问题分类: {r.get('classification', '')}")

    if ctx.get("_design_principles"):
        print(f"\n  激活的认知解构原则:")
        for p in ctx["_design_principles"][:3]:
            print(f"    - {p}")


def test_word_understanding(engine):
    """测试3：词义理解"""
    print(f"\n{DIVIDER}")
    print("测试3：词义理解（引擎触发词义节点）")
    print(DIVIDER)

    ctx = {
        "task": "为什么appointment用for而不是at？分析一下for的真正含义",
        "_entry": "570",
    }

    node = engine.nodes.get("570")
    if node and engine.check_trigger(node, ctx):
        ctx = node.execute(ctx)

    if ctx.get("_word_method"):
        wm = ctx["_word_method"]
        print(f"  方法: {wm['principle']}")
        print(f"  五步法:")
        for s in wm["steps"]:
            print(f"    {s}")

    # 让模型回答这个具体问题
    answer = ask(
        "你是词义分析师。用词源分析法回答。50字以内。",
        "for的真正含义是什么？为什么appointment用for不用at？",
        temperature=0.3, max_tokens=100
    )
    print(f"\n  模型回答: {answer.strip()}")


def test_code_generation(engine):
    """测试4：代码生成（通过完整管线）"""
    print(f"\n{DIVIDER}")
    print("测试4：代码生成（完整管线，节点展开）")
    print(DIVIDER)

    ctx = {
        "task": "待办事项 Web 应用",
        "output_dir": str(Path(__file__).parent / "output_test"),
        "_entry": "010",
    }

    result = engine.run("010", ctx)
    engine.print_trace()

    if result.get("output_path"):
        out = Path(result["output_path"])
        for f in ["index.html", "style.css", "app.js"]:
            fp = out / f
            if fp.exists():
                print(f"  {f}: {fp.stat().st_size} bytes")

    activated = len(engine.trace)
    print(f"\n  激活节点数: {activated}")


def test_debug_diagnosis(engine):
    """测试5：调试诊断"""
    print(f"\n{DIVIDER}")
    print("测试5：调试诊断（给出bug描述，看系统怎么展开）")
    print(DIVIDER)

    ctx = {
        "task": "修复一个bug：页面上的列表数据刷新后消失了，localStorage里有数据但页面显示空白",
        "_entry": "600",
    }

    for nid in ["600", "420", "140", "350"]:
        node = engine.nodes.get(nid)
        if node and engine.check_trigger(node, ctx):
            ctx = node.execute(ctx)
            print(f"  [{nid}] {node.name}")

    if ctx.get("_fix_steps"):
        print(f"\n  Fix模式展开({len(ctx['_fix_steps'])}步):")
        for step in ctx["_fix_steps"][:4]:
            par = " [可并行]" if step.get("parallel") else ""
            print(f"    {step['id']} ({step['actor']}): {step['name']}{par}")
            print(f"         {step['action']}")

    if ctx.get("_debug"):
        print(f"\n  症状描述: {ctx['_debug'].get('symptom', '')}")


def test_interaction_design(engine):
    """测试6：交互设计"""
    print(f"\n{DIVIDER}")
    print("测试6：交互设计（触发交互规则节点）")
    print(DIVIDER)

    ctx = {
        "task": "设计一个在线文档编辑器的保存和协作交互",
        "interactions": "用户输入文本 → 实时保存\n用户添加评论 → 通知协作者\n用户删除段落 → 可撤销",
        "_entry": "230",
    }

    for nid in ["230", "231", "232", "560"]:
        node = engine.nodes.get(nid)
        if node and engine.check_trigger(node, ctx):
            ctx = node.execute(ctx)
            print(f"  [{nid}] {node.name}")

    if ctx.get("_interaction_review"):
        print(f"\n  交互审查:")
        for r in ctx["_interaction_review"]:
            print(f"    - {r}")

    contract = ctx.get("contract", {})
    patterns = contract.get("interaction_patterns", [])
    if patterns:
        print(f"\n  注入的交互模式({len(patterns)}条):")
        for p in patterns[:5]:
            print(f"    - {p}")

    if ctx.get("_design_principles"):
        print(f"\n  不可逆保险原则:")
        for p in ctx.get("_design_principles", [])[:3]:
            print(f"    - {p}")


def test_creative_writing():
    """测试7：内容创作"""
    print(f"\n{DIVIDER}")
    print("测试7：内容创作（模型独立完成文本生成）")
    print(DIVIDER)

    prompts = [
        ("技术博客作者。用中文写3句话，简洁有深度。",
         "写一段关于'为什么2B模型需要系统编排'的开头段落"),
        ("诗人。写四行现代诗，意象简洁。",
         "以'节点与连接'为主题写一首短诗"),
        ("产品文案。一句话卖点。",
         "为'可执行知识网络引擎'写一句产品口号"),
    ]

    for sys_msg, user_msg in prompts:
        result = ask(sys_msg, user_msg, temperature=0.7, max_tokens=150)
        print(f"\n  任务: {user_msg}")
        print(f"  输出: {result.strip()}")


def main():
    engine = load_engine()
    print(f"v2引擎已加载 {len(engine.nodes)} 个节点\n")

    # 不需要API调用的测试先跑
    test_reasoning(engine)
    test_word_understanding(engine)
    test_debug_diagnosis(engine)
    test_interaction_design(engine)

    # 需要API调用的测试
    print(f"\n{'#' * 60}")
    print("以下测试需要2B模型API调用")
    print(f"{'#' * 60}")

    test_conversation()
    test_creative_writing()

    # 代码生成放最后（最耗时）
    test_code_generation(engine)

    print(f"\n{DIVIDER}")
    print("全部测试完成")
    print(DIVIDER)


if __name__ == "__main__":
    main()
