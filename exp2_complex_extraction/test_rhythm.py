"""
测试 2B 在 record 操作后能否维持循环节奏。
假说：模型在执行 record() 后容易"脱出"工具模式。

测试：相同文档（3个函数），极简vs当前 prompt，多种seed，
      统计 STOP 事件和 record 后是否保持节奏。
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

import requests
from tools import ToolState, execute_tool, make_tool_schemas
from data_generator import generate_python_file
from evaluate import evaluate

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 300
MAX_ROUNDS = 50


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


def run_with_prompt(system, user, text, gt, label, seed):
    state = ToolState(text)
    tools = make_tool_schemas(include_stack=False, include_record=True)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
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
            tool_seq.append(f"STOP")
            if state.cursor < len(text):
                messages.append({
                    "role": "user",
                    "content": "继续。read_next → advance_past。",
                })
            else:
                break
        else:
            break

    found = [r["item"] for r in state.records]
    coverage = round(state.cursor / max(len(text), 1) * 100, 1)
    metrics = evaluate("python_functions", gt, found)
    counts = Counter(tool_seq)

    print(f"  [{label}] seed={seed}: F1={metrics['f1']:.2f} R={metrics['recall']:.2f} "
          f"P={metrics['precision']:.2f} cov={coverage}% rds={rounds} "
          f"stops={stop_count} reads={counts.get('read_next',0)} "
          f"adv={counts.get('advance_past',0)} rec={counts.get('record',0)}")
    return {
        "f1": metrics["f1"],
        "stops": stop_count,
        "coverage": coverage,
        "tool_seq": tool_seq,
    }


SYSTEM_MINIMAL = """\
你是文本扫描器。用工具逐段读取文档。
流程：read_next → advance_past → 重复。done=true → get_records() → 停止。
严禁输出文字，只调用工具。\
"""

USER_MINIMAL = (
    "扫描 Python 文件，找顶级函数名。\n"
    "规则：行的 content 以 'def ' 开头（前面没有空格）→ record(item=函数名, category='function')。\n"
    "现在调用 read_next()。"
)


def main():
    from prompts import SYSTEM_B, TASK_PROMPTS

    seeds = [42, 1, 7, 13, 99, 2024]

    print("=" * 70)
    print("极简 prompt 测试（6 个 seed）")
    print("=" * 70)

    simple_results = []
    for seed in seeds:
        text, gt = generate_python_file(
            n_top_level=5, n_classes=2, n_methods_per_class=3, seed=seed)
        r = run_with_prompt(SYSTEM_MINIMAL, USER_MINIMAL, text, gt,
                           "极简", seed)
        simple_results.append(r)

    print(f"\n极简 prompt 平均 F1: {sum(r['f1'] for r in simple_results)/len(simple_results):.2f}")
    print(f"STOP 次数: {[r['stops'] for r in simple_results]}")

    print("\n" + "=" * 70)
    print("原版 prompt 测试（6 个 seed）")
    print("=" * 70)

    orig_results = []
    for seed in seeds:
        text, gt = generate_python_file(
            n_top_level=5, n_classes=2, n_methods_per_class=3, seed=seed)
        user_orig = TASK_PROMPTS["python_functions"](text, "B")
        r = run_with_prompt(SYSTEM_B, user_orig, text, gt, "原版", seed)
        orig_results.append(r)

    print(f"\n原版 prompt 平均 F1: {sum(r['f1'] for r in orig_results)/len(orig_results):.2f}")
    print(f"STOP 次数: {[r['stops'] for r in orig_results]}")

    print("\n" + "=" * 70)
    print("对比总结")
    print("=" * 70)
    for i, seed in enumerate(seeds):
        s = simple_results[i]
        o = orig_results[i]
        better = "极简" if s["f1"] >= o["f1"] else "原版"
        print(f"  seed={seed:4d}: 极简 F1={s['f1']:.2f}(stops={s['stops']}) "
              f"原版 F1={o['f1']:.2f}(stops={o['stops']}) → {better}")


if __name__ == "__main__":
    main()
