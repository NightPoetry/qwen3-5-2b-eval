"""知识节点：自循环调试——AI自主调试闭环基础设施。

核心思想：AI辅助开发中最大瓶颈是"AI改代码→用户手动测试→口述现象→AI猜测"的反馈环路。
将测试能力交给AI自己可以把环路从分钟级压缩到秒级。

三个支柱：可观测（远程日志）、可操控（API触发操作）、可模拟（mock外部依赖）。
融合：self-loop-debugging
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SELFLOOP_KNOWLEDGE = """你是自主调试闭环专家。根据以下知识分析调试瓶颈。

## 调试基础设施三支柱
- 可观测：日志缓冲在内存中通过HTTP端点暴露（console.log对AI无用——AI读不到浏览器控制台）
- 可操控：应用状态暴露到全局变量后通过eval端点读写，等价用户所有UI操作
- 可模拟：mock和真实端点使用相同协议（SSE mock要发data:...格式，不能只返回JSON）
- 缺任何一个都无法形成完整闭环

## 日志系统
- 日志结构：时间戳+级别+标签+消息+可选附加数据。标签用于过滤
- 容量上限（如2000条循环缓冲）防内存泄漏，支持since/tag/level/limit过滤
- HTTP轮询已够用，调试不需毫秒级实时性

## 远程控制
- eval端点用.then()而非await（new Function不支持顶层await）
- 多客户端共用dev server时eval需target参数区分目标

## 量化验证
- 测试结果写到全局变量，用eval端点读取。结构化数据比截图或口述可靠无数倍
- 时间分布是流式问题最关键指标：一次性到达vs逐步流式不需要看UI就能下结论
- 修复前后必须用相同测试方法对比，不凭感觉说"好像修好了"

## WebView特殊行为
- macOS WKWebView的fetch ReadableStream会缓冲整个响应体
- 同一chunk中>3个事件时，事件间插入await setTimeout(0)让出主线程
"""

def execute(ctx: dict) -> dict:
    errors = ctx.get("_errors", [])
    failures = ctx.get("_failures_recovered", [])

    if not errors and not failures:
        return ctx

    # 收集错误信息
    error_summary = []
    for err in errors:
        error_summary.append(f"节点{err.get('node','?')}报错: {err.get('error','?')}")
    for f in failures:
        error_summary.append(f"已恢复的失效: {f}")

    # LLM诊断根因
    result = ask(
        SELFLOOP_KNOWLEDGE +
        "\n根据以下系统内部错误，诊断根因并建议修复方向（不超过3条建议）。",
        f"错误列表：\n" + "\n".join(error_summary),
        max_tokens=200
    ).strip()

    ctx["_self_diagnosis"] = error_summary
    ctx["_self_diagnosis_advice"] = result
    return ctx

node = Node(id="450", name="自循环诊断",
    trigger={"type": "key_exists", "key": "_errors"},
    execute=execute, refs=["420"],
    metadata={"source": "knowledge/self-loop-debugging", "category": "meta"})
