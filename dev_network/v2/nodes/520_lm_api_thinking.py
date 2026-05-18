"""知识节点：LM thinking/streaming模式——思考模型与SSE流式的陷阱。

融合：Qwen3.x thinking坑 + SSE流式工具调用参数累积 + 分层上下文注入设计
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

THINKING_KNOWLEDGE = """你是LLM推理模式专家。根据以下知识判断任务涉及的思考模型/流式处理问题。

## Thinking模式
- Qwen3.x API必须显式发enable_thinking:true否则content为空
- 不发或发false→content空，reasoning_content输出JSON垃圾
- 本地推理框架UI聊天默认发true，所以UI正常但API不正常
- tool_calls可能出现在reasoning_content而非tool_calls字段——需fallback XML解析
- 诊断4步：curl最简→逐个加参数→对比UI→检查reasoning vs content

## SSE流式tool_call参数累积（关键）
- 流式模式下tool_calls的arguments分块到达(delta)，不是一次性完整返回
- 第一个delta包含id和name，arguments通常为空字符串""
- 后续delta只包含arguments的增量片段（几字符到几十字符）
- 最后一个delta的finish_reason="tool_calls"表示流结束
- 必须累积所有arguments delta拼接完成后再JSON.parse
- 只读第一个chunk会得到空参数，工具调用完全失败
- 这是OpenAI兼容API的标准SSE协议行为，与模型无关

## 流式模式vs非流式行为差异
- stream:true + tool_choice:auto可能不调工具→用required强制
- streaming和non-streaming行为可能不一致
- 非流式调用正常+流式失败=你的SSE解析逻辑有bug

## 分层上下文注入
- 按变化频率分层：稳定内容→system前缀（利用缓存），动态内容→用户消息前（高优先级）
- 冲突时通过位置+显式声明双重保证优先级
- 工具调用说明放动态上下文末尾紧贴用户消息
- 功能命名反映作用范围不是技术机制
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        THINKING_KNOWLEDGE +
        "\n分析以下任务涉及的思考模型/流式处理问题，给出具体建议（每条一行，不超过4条）。"
        "如果不涉及这些问题，回答'无相关问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无相关问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="520", name="LM thinking/streaming",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["thinking", "enable_thinking", "qwen", "reasoning",
                          "tool_call", "content为空", "SSE", "delta",
                          "arguments", "流式", "stream", "上下文注入",
                          "system prompt", "context injection"]},
    execute=execute, refs=["395"],
    metadata={"source": "Guild/AI与LLM应用/SSE流式+分层上下文+thinking", "category": "domain_ai"})
