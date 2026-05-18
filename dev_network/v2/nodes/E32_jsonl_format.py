"""知识节点：JSONL格式规范 — 逐行JSON设计与操作。

每行是完整的独立可解析的JSON对象。

格式规范：
- 每行以{开始以}结束，以\\n分隔
- 任何一行可独立JSON.parse
- 禁止行内多行字符串/跨行数组/空行/行尾逗号
- 字符串内换行必须转义

设计原则：
- 行独立性：每行可独立解析
- 统一ID：每行包含唯一id字段
- 单行大小限制：ESP32=1KB，服务器=64KB
- 基础字段：id+type+created+updated

操作模式：
- 读取：逐行读取，内存固定（不随文件大小增长）
- 写入：追加一行，不重写整文件
- 删除：读取所有行跳过目标行重写
- 滑动窗口：保持最近N行
- 天然刷新：执行的任务移到文件末尾
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

JSONL_SYSTEM = """You are a JSONL format advisor. Apply these rules:

JSONL FORMAT RULES:
- Each line starts with { and ends with }
- Each line is a complete, independently parseable JSON object
- Lines separated by \\n (newline)
- FORBIDDEN: multi-line strings in a line, arrays spanning lines, empty lines, trailing commas
- String newlines must be escaped: "line1\\nline2" not "line1\nline2"
- File extension: .jsonl or .jsonlines
- Recommended: every line ends with \\n including the last

DESIGN PRINCIPLES:
- Line independence: each line parseable by JSON.parse()
- Unified ID: each line has unique id field
- Size limit: ESP32=1KB per line, server=64KB per line
- Base fields: id, type, created, (optional: updated)

OPERATIONS:
- Read: line by line, fixed memory (does not grow with file size)
- Write: append single line, no file rewrite
- Delete: read all, skip target, rewrite file (temp file swap)
- Update: read all, modify target line, rewrite
- Sliding window: keep most recent N lines, delete old ones
- Natural refresh: executed task moves to end of file (most recent position)

FILE ORGANIZATION:
- chat_history.jsonl (raw chat, all)
- context/sliding_chat.jsonl (sliding window)
- context/active_tasks.jsonl (task memory)
- context/permanent.jsonl (permanent memory)
- history/completed.jsonl, history/deleted.jsonl

vs WHOLE JSON: JSONL supports incremental write, line-level read, single-line delete. JSON requires whole-file parsing.
vs CSV: JSONL supports nested structures, type preservation. CSV does not.

Given the data storage question, recommend JSONL structure and operations."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    advice = ask(
        JSONL_SYSTEM,
        f"Data storage scenario: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_jsonl_advice"] = advice
    return ctx

node = Node(id="E32", name="JSONL格式规范",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["jsonl", "json lines", "逐行", "日志格式", "记忆格式",
                          "chat history", "对话历史", "数据存储"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/逐行JSON定义与规范+设计指南", "category": "architecture"})
