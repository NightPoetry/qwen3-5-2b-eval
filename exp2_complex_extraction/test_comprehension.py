"""
诊断 2B 模型对不同复杂度指令的理解能力。

测试维度：
  1. 简单循环：能否维持 read→advance→read 节奏
  2. 条件判断：能否区分顶级函数 vs 方法
  3. 多步协议：能否同时 record + advance
  4. 恢复能力：打断节奏后能否恢复

用法：
    python test_comprehension.py [--test all|loop|judge|recover]
"""

import argparse
import json
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tools import ToolState, execute_tool, make_tool_schemas
from data_generator import generate_python_file

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 300


def chat(messages, tools=None):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 1024,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    resp = requests.post(API_URL, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]


# ── 测试 1：纯循环能力（最简单的任务，看能否维持节奏）────────────────

def test_loop_rhythm(n_functions=3, seed=42):
    """最简场景：3 个函数，只看模型能否完成 read→advance→read 循环。"""
    text, gt = generate_python_file(n_top_level=n_functions, n_classes=0,
                                     n_methods_per_class=0, seed=seed)

    # 极简 prompt——只要求循环，不要求记录
    system = "你是文本处理助手。用工具逐段读取文档，读完为止。"
    user = (
        "请用工具读完整个文档。每轮：\n"
        "1. 调用 read_next()\n"
        "2. 调用 advance_past(to_line=<advance_target>)\n"
        "3. done=false → 重复；done=true → 停止\n\n"
        "现在开始。"
    )

    state = ToolState(text)
    tools = make_tool_schemas(include_stack=False, include_record=False)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    rounds = 0
    max_rounds = 30
    tool_seq = []

    while rounds < max_rounds:
        rounds += 1
        choice = chat(messages, tools=tools)
        finish = choice["finish_reason"]
        msg = choice["message"]

        if finish == "tool_calls":
            tcs = msg.get("tool_calls", [])
            messages.append({
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": tcs,
            })
            for tc in tcs:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                result = execute_tool(state, fn, args)
                tool_seq.append(fn)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            if state.cursor >= len(text):
                break
        else:
            tool_seq.append(f"STOP({finish})")
            break

    coverage = round(state.cursor / max(len(text), 1) * 100, 1)
    print(f"\n=== 测试1: 纯循环 (n_func={n_functions}, seed={seed}) ===")
    print(f"Lines: {text.count(chr(10))}  Chars: {len(text)}")
    print(f"Rounds: {rounds}  Coverage: {coverage}%")
    print(f"Tool sequence: {' → '.join(tool_seq)}")
    ok = coverage >= 95
    print(f"结论: {'✓ 能维持循环' if ok else '✗ 循环中断'}")
    return ok


# ── 测试 2：条件判断能力（非工具模式，直接问）────────────────────────

def test_judgment():
    """直接给几行代码，问哪些是顶级函数，测试判断能力。"""
    code_lines = [
        "def authenticate(user, pw):",
        "    def _hash(s):",
        "class Server:",
        "    def handle(self, req):",
        "def process_batch(items):",
        "        def inner():",
        "import os",
        "def log_event(msg):",
    ]
    expected = ["authenticate", "process_batch", "log_event"]

    prompt = (
        "以下是 Python 代码的若干行（每行前标注了编号）：\n\n"
        + "\n".join(f"  {i+1}. {line}" for i, line in enumerate(code_lines))
        + "\n\n"
        "规则：顶级函数 = 行首无任何空格且以 'def ' 开头的行。\n"
        "请只输出顶级函数名，用 JSON 列表格式：[\"name1\", \"name2\", ...]"
    )

    choice = chat([
        {"role": "system", "content": "你是精确的代码分析助手，只输出 JSON。"},
        {"role": "user", "content": prompt},
    ])
    text = choice["message"].get("content", "")

    import re
    found = []
    for m in re.finditer(r'\[.*?\]', text, re.DOTALL):
        try:
            found = json.loads(m.group())
            break
        except json.JSONDecodeError:
            continue
    found = [str(x).strip() for x in found]

    print(f"\n=== 测试2: 条件判断 ===")
    print(f"Expected: {expected}")
    print(f"Got:      {found}")
    print(f"Raw:      {text[:200]}")
    ok = set(found) == set(expected)
    print(f"结论: {'✓ 判断正确' if ok else '✗ 判断错误'}")
    return ok


# ── 测试 3：完整协议（record + advance，最小文档）────────────────────

def test_full_protocol(seed=42):
    """3 个顶级函数的小文档，用完整 Condition B 协议，看能否 record 全部。"""
    text, gt = generate_python_file(n_top_level=3, n_classes=0,
                                     n_methods_per_class=0, seed=seed)

    from prompts import SYSTEM_B, TASK_PROMPTS
    user_p = TASK_PROMPTS["python_functions"](text, "B")

    state = ToolState(text)
    tools = make_tool_schemas(include_stack=True, include_record=True)
    messages = [
        {"role": "system", "content": SYSTEM_B},
        {"role": "user", "content": user_p},
    ]

    rounds = 0
    max_rounds = 40
    tool_seq = []

    while rounds < max_rounds:
        rounds += 1
        choice = chat(messages, tools=tools)
        finish = choice["finish_reason"]
        msg = choice["message"]

        if finish == "tool_calls":
            tcs = msg.get("tool_calls", [])
            messages.append({
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": tcs,
            })
            for tc in tcs:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                result = execute_tool(state, fn, args)
                tool_seq.append(fn)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            called = [tc["function"]["name"] for tc in tcs]
            if "get_records" in called:
                break
            if state.cursor >= len(text):
                break
        elif finish in ("stop", "length"):
            tool_seq.append(f"STOP({finish})")
            if state.cursor < len(text):
                pct = round(state.cursor / len(text) * 100)
                messages.append({
                    "role": "user",
                    "content": f"文档仅读了 {pct}%，继续工作循环：read_next → 处理 → advance_past。",
                })
            else:
                break
        else:
            break

    found = [r["item"] for r in state.records]
    coverage = round(state.cursor / max(len(text), 1) * 100, 1)

    from evaluate import evaluate
    metrics = evaluate("python_functions", gt, found)

    print(f"\n=== 测试3: 完整协议 (seed={seed}) ===")
    print(f"GT:    {gt}")
    print(f"Found: {found}")
    print(f"F1={metrics['f1']:.2f}  R={metrics['recall']:.2f}  P={metrics['precision']:.2f}")
    print(f"Coverage: {coverage}%  Rounds: {rounds}")
    print(f"Tool sequence: {' → '.join(tool_seq[:30])}{'...' if len(tool_seq) > 30 else ''}")
    ok = metrics["f1"] >= 0.9
    print(f"结论: {'✓ 协议执行正确' if ok else '✗ 协议执行失败'}")
    return ok


# ── 测试 4：恢复能力（跑几轮后注入干扰，看能否恢复）────────────────

def test_recovery(seed=1):
    """用 seed=1（已知失败的种子），看加了防护后能否恢复。"""
    text, gt = generate_python_file(n_top_level=3, n_classes=0,
                                     n_methods_per_class=0, seed=seed)

    from prompts import SYSTEM_B, TASK_PROMPTS
    user_p = TASK_PROMPTS["python_functions"](text, "B")

    state = ToolState(text)
    tools = make_tool_schemas(include_stack=True, include_record=True)
    messages = [
        {"role": "system", "content": SYSTEM_B},
        {"role": "user", "content": user_p},
    ]

    rounds = 0
    max_rounds = 40
    tool_seq = []

    while rounds < max_rounds:
        rounds += 1
        choice = chat(messages, tools=tools)
        finish = choice["finish_reason"]
        msg = choice["message"]

        if finish == "tool_calls":
            tcs = msg.get("tool_calls", [])
            messages.append({
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": tcs,
            })
            for tc in tcs:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                result = execute_tool(state, fn, args)
                tool_seq.append(fn)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            called = [tc["function"]["name"] for tc in tcs]
            if "get_records" in called:
                break
            if state.cursor >= len(text):
                break
        elif finish in ("stop", "length"):
            tool_seq.append(f"STOP({finish})")
            if state.cursor < len(text):
                pct = round(state.cursor / len(text) * 100)
                messages.append({
                    "role": "user",
                    "content": f"文档仅读了 {pct}%，继续工作循环：read_next → 处理 → advance_past。",
                })
            else:
                break
        else:
            break

    found = [r["item"] for r in state.records]
    coverage = round(state.cursor / max(len(text), 1) * 100, 1)

    from evaluate import evaluate
    metrics = evaluate("python_functions", gt, found)

    print(f"\n=== 测试4: 恢复能力 (seed={seed}) ===")
    print(f"GT:    {gt}")
    print(f"Found: {found}")
    print(f"F1={metrics['f1']:.2f}  R={metrics['recall']:.2f}  P={metrics['precision']:.2f}")
    print(f"Coverage: {coverage}%  Rounds: {rounds}")
    print(f"Tool sequence: {' → '.join(tool_seq[:40])}{'...' if len(tool_seq) > 40 else ''}")

    read_count = tool_seq.count("read_next")
    adv_count = tool_seq.count("advance_past")
    print(f"read_next: {read_count}  advance_past: {adv_count}  ratio: {read_count}/{max(adv_count,1)}")
    ok = metrics["f1"] >= 0.9
    print(f"结论: {'✓ 恢复成功' if ok else '✗ 恢复失败'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", default="all",
                    choices=["all", "loop", "judge", "full", "recover"])
    args = ap.parse_args()

    results = {}
    if args.test in ("all", "loop"):
        results["loop_s42"] = test_loop_rhythm(n_functions=3, seed=42)
        results["loop_s1"] = test_loop_rhythm(n_functions=3, seed=1)
        results["loop_s7"] = test_loop_rhythm(n_functions=3, seed=7)

    if args.test in ("all", "judge"):
        results["judge"] = test_judgment()

    if args.test in ("all", "full"):
        results["full_s42"] = test_full_protocol(seed=42)
        results["full_s1"] = test_full_protocol(seed=1)
        results["full_s7"] = test_full_protocol(seed=7)

    if args.test in ("all", "recover"):
        results["recover_s1"] = test_recovery(seed=1)
        results["recover_s7"] = test_recovery(seed=7)

    print("\n" + "=" * 50)
    print("总结")
    print("=" * 50)
    for name, ok in results.items():
        print(f"  {name:20s} {'✓' if ok else '✗'}")


if __name__ == "__main__":
    main()
