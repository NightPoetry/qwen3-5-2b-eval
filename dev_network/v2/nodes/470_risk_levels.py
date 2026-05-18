"""知识节点：操作风险分级——用LLM评估代码风险等级。

L0只读 / L1局部写 / L2跨界影响 / L3不可逆破坏
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

def execute(ctx: dict) -> dict:
    js = ctx.get("js", "")
    if not js: return ctx

    result = ask(
        "评估这段代码的最高操作风险等级，等级定义：\n"
        "L0=只读操作（读取DOM、解析数据）\n"
        "L1=局部写入（修改样式、本地存储写入）\n"
        "L2=跨界影响（网络请求、打开窗口、跨域通信）\n"
        "L3=不可逆破坏（清空存储、删除文件、eval执行、SQL删除）\n"
        "回答格式：等级,原因。例如：L2,使用了fetch发起网络请求",
        f"代码：\n{js[:1000]}",
        max_tokens=80
    ).strip()

    level = "L0"
    for l in ["L3", "L2", "L1"]:
        if l in result:
            level = l
            break

    ctx["_risk_levels"] = {level: [result]}
    if level == "L3":
        ctx.setdefault("_risk_alerts", []).append(f"L3不可逆操作: {result}")
    elif level == "L2":
        ctx.setdefault("_risk_alerts", []).append(f"L2跨界操作: {result}")
    return ctx

node = Node(id="470", name="风险分级",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute, refs=["330"],
    metadata={"source": "knowledge/ai-agent-safety", "category": "safety"})
