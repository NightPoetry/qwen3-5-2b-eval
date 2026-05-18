"""
测试 Condition B+（带 analyze_line 判断工具）。
模型只需要：循环 + 调用 analyze_line + 根据结果 record。
不需要自己判断什么是顶级函数。
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

import requests
from tools import ToolState, execute_tool, make_tool_schemas, ANALYZERS
from data_generator import generate_python_file
from evaluate import evaluate

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 300
MAX_ROUNDS = 80


SYSTEM_BPLUS = """\
你是文本扫描器。系统加载了一段文本，你用工具逐段处理。

每轮流程（严禁跳过任何步骤）：
1. read_next() 读取下一批
2. 对每行调用 analyze_line(content=<行内容>)
3. 如果返回 is_target=true，按 action 指示调用 record()
4. advance_past(to_line=<advance_target>)
5. done=true → get_records()；done=false → 回到第1步

严禁输出文字，只调用工具。\
"""

USER_BPLUS = (
    "扫描文档，找出所有目标条目。\n"
    "对每行调用 analyze_line() 让系统帮你判断。\n"
    "现在调用 read_next() 开始。"
)


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


def run_test(text, gt, seed, task_key="python_functions"):
    state = ToolState(text)
    state._analyzer = ANALYZERS[task_key]
    tools = make_tool_schemas(include_stack=False, include_record=True,
                              include_analyze=True)
    messages = [
        {"role": "system", "content": SYSTEM_BPLUS},
        {"role": "user", "content": USER_BPLUS},
    ]

    rounds = 0
    tool_seq = []
    stop_count = 0

    while rounds < MAX_ROUNDS:
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
            stop_count += 1
            tool_seq.append("STOP")
            if state.cursor < len(text):
                messages.append({
                    "role": "user",
                    "content": "继续。read_next → analyze_line → advance_past。",
                })
            else:
                break
        else:
            break

    found = [r["item"] for r in state.records]
    coverage = round(state.cursor / max(len(text), 1) * 100, 1)
    metrics = evaluate(task_key, gt, found)
    counts = Counter(tool_seq)

    print(f"  seed={seed}: F1={metrics['f1']:.2f} R={metrics['recall']:.2f} "
          f"P={metrics['precision']:.2f} cov={coverage}% rds={rounds} "
          f"stops={stop_count}")
    print(f"    tools: read={counts.get('read_next',0)} "
          f"analyze={counts.get('analyze_line',0)} "
          f"record={counts.get('record',0)} "
          f"advance={counts.get('advance_past',0)}")
    return metrics["f1"], coverage, stop_count


def main():
    seeds = [42, 1, 7, 13, 99, 2024]

    print("=" * 60)
    print("Condition B+ (analyze_line 判断工具)")
    print("模型不需要自己判断，只需 read → analyze → record → advance")
    print("=" * 60)

    f1s = []
    for seed in seeds:
        text, gt = generate_python_file(
            n_top_level=5, n_classes=2, n_methods_per_class=3, seed=seed)
        f1, cov, stops = run_test(text, gt, seed)
        f1s.append(f1)

    avg = sum(f1s) / len(f1s)
    print(f"\n平均 F1: {avg:.2f}")
    print(f"各 seed F1: {[f'{f:.2f}' for f in f1s]}")
    perfect = sum(1 for f in f1s if f >= 0.99)
    print(f"完美率: {perfect}/{len(f1s)}")


if __name__ == "__main__":
    main()
