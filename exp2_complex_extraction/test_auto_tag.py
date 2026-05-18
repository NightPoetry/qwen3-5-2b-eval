"""
测试自动标注模式：read_next 返回的行自带 ★目标 标记。
模型只需 read → (看到★目标就 record) → advance → 循环。
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


SYSTEM_AUTO = """\
你是文本扫描器。用工具逐段处理文档。

每轮：
1. read_next() 读取一批内容
2. 检查返回的 lines：带 ★目标 标记的行 → 调用 record(item=该行的item, category=该行的category)
3. advance_past(to_line=<advance_target>)
4. done=true → get_records()；done=false → 回到第1步

严禁输出文字，只调用工具。\
"""

USER_AUTO = "开始扫描。调用 read_next()。"


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
                              include_analyze=False)
    messages = [
        {"role": "system", "content": SYSTEM_AUTO},
        {"role": "user", "content": USER_AUTO},
    ]

    rounds = 0
    tool_seq = []
    stop_count = 0

    while rounds < MAX_ROUNDS:
        rounds += 1
        try:
            choice = chat(messages, tools=tools)
        except Exception as e:
            print(f"    API error at round {rounds}: {e}")
            break

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
                    "content": "继续。read_next → record(★目标) → advance_past。",
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
    print(f"    read={counts.get('read_next',0)} "
          f"record={counts.get('record',0)} "
          f"advance={counts.get('advance_past',0)}")
    if found != sorted(found):
        print(f"    GT:    {gt}")
        print(f"    Found: {found}")
    return metrics["f1"], coverage, stop_count


def main():
    seeds = [42, 1, 7, 13, 99, 2024]

    print("=" * 60)
    print("自动标注模式 (★目标)")
    print("read_next 自动标记目标行，模型只看标记 record")
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
