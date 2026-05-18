"""
测试极简 prompt 是否足以让 2B 完成任务。

对比当前 15 行 prompt vs 极简 3 句话 prompt。
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
MAX_ROUNDS = 80


SYSTEM_SIMPLE = """\
你是文本扫描器。系统加载了一段文本，你必须用工具逐段读取。

工作流程：read_next → 检查内容 → record（如有发现）→ advance_past → 重复。
done=true 时调用 get_records() 然后停止。严禁输出文字，只调用工具。\
"""

USER_SIMPLE = (
    "扫描 Python 文件，找所有顶级函数名。\n"
    "规则：行首是 'def '（前面没有空格）→ 顶级函数，调用 record(item=函数名, category='function')。\n"
    "行首有空格的 def → 不是顶级函数，跳过。\n"
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


def run_test(system, user, text, gt, label, seed):
    state = ToolState(text)
    tools = make_tool_schemas(include_stack=False, include_record=True)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    rounds = 0
    tool_seq = []

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
            tool_seq.append(f"STOP({finish})")
            if state.cursor < len(text):
                pct = round(state.cursor / len(text) * 100)
                messages.append({
                    "role": "user",
                    "content": f"继续。read_next → advance_past。进度 {pct}%。",
                })
            else:
                break
        else:
            break

    found = [r["item"] for r in state.records]
    coverage = round(state.cursor / max(len(text), 1) * 100, 1)
    metrics = evaluate("python_functions", gt, found)
    counts = Counter(tool_seq)

    print(f"\n  [{label}] seed={seed}")
    print(f"  GT:    {gt}")
    print(f"  Found: {found}")
    print(f"  F1={metrics['f1']:.2f}  R={metrics['recall']:.2f}  P={metrics['precision']:.2f}")
    print(f"  Coverage: {coverage}%  Rounds: {rounds}")
    print(f"  Tools: {dict(counts)}")
    stops = [x for x in tool_seq if x.startswith("STOP")]
    if stops:
        print(f"  STOPs: {len(stops)}")
    return metrics["f1"]


def main():
    from prompts import SYSTEM_B, TASK_PROMPTS

    seeds = [42, 1, 7]
    n_top, n_cls, n_mth = 5, 2, 3

    for seed in seeds:
        text, gt = generate_python_file(
            n_top_level=n_top, n_classes=n_cls,
            n_methods_per_class=n_mth, seed=seed)

        print(f"\n{'='*50}")
        print(f"seed={seed}  lines={text.count(chr(10))}  chars={len(text)}  gt={len(gt)} functions")
        print(f"{'='*50}")

        user_orig = TASK_PROMPTS["python_functions"](text, "B")

        f1_orig = run_test(SYSTEM_B, user_orig, text, gt, "原版 prompt", seed)
        f1_simple = run_test(SYSTEM_SIMPLE, USER_SIMPLE, text, gt, "极简 prompt", seed)

        delta = f1_simple - f1_orig
        print(f"\n  对比: 原版 F1={f1_orig:.2f} → 极简 F1={f1_simple:.2f}  (Δ={delta:+.2f})")


if __name__ == "__main__":
    main()
