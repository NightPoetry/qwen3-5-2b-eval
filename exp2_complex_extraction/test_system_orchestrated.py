"""
系统编排架构测试。

核心思想：模型做不好的事不让它做。
  - 确定性操作（筛选、判断缩进、记录）→ 系统/代码处理
  - 需要理解的操作（导航、名称提取）→ 模型处理，且上下文隔离

模型的唯一任务：循环 read_next → advance_past（已验证 100% 可靠）
系统在 runner 层完成：候选筛选 → 展开提取 → 自动记录
"""

import json
import sys
import re
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

import requests
from tools import ToolState, execute_tool, make_tool_schemas
from data_generator import generate_python_file
from evaluate import evaluate

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 120
MAX_ROUNDS = 80


def mini_chat(question: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "只回答问题，不要解释。尽量用一个词回答。"},
            {"role": "user", "content": question},
        ],
        "temperature": 0.0,
        "max_tokens": 32,
    }
    resp = requests.post(API_URL, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


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
    for attempt in range(3):
        try:
            resp = requests.post(API_URL, json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json()["choices"][0]
        except requests.HTTPError:
            if attempt < 2:
                import time; time.sleep(2)
                continue
            raise


# ── 系统层：确定性操作 ──────────────────────────────────────────────────

def system_filter_candidates(lines: list[dict], task: str) -> list[dict]:
    """确定性筛选：哪些行是候选目标。纯代码逻辑，不需要模型。"""
    if task == "python_functions":
        return [l for l in lines if l["content"].startswith("def ")]
    elif task == "html_headings":
        return [l for l in lines
                if re.match(r'^\s*<h[1-6]', l["content"], re.IGNORECASE)]
    elif task == "minified_python":
        return [l for l in lines if "def " in l["content"]]
    return []


def system_extract_name(line_content: str, task: str) -> dict | None:
    """用隔离微对话提取名称。模型只回答一个简单问题。"""
    if task == "python_functions":
        q = f"'{line_content}' 是函数定义。函数名紧跟 'def ' 出现，在 '(' 之前。函数名是？"
        name = mini_chat(q).strip().strip("'\"` ").split("(")[0].split(" ")[0]
        if name and name.isidentifier():
            return {"item": name, "category": "function"}
    elif task == "html_headings":
        m = re.match(r'<h([1-6])[^>]*>(.*?)</h\1>', line_content.strip(), re.I)
        if m:
            text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            return {"item": text, "category": f"h{m.group(1)}"}
    return None


# ── 主测试 ──────────────────────────────────────────────────────────────

def run_test(seed, n_top=5, n_cls=2, n_mth=3, task_key="python_functions"):
    text, gt = generate_python_file(
        n_top_level=n_top, n_classes=n_cls,
        n_methods_per_class=n_mth, seed=seed)

    state = ToolState(text)
    # 模型只需要导航工具，不需要 record（系统自动记录）
    tools = make_tool_schemas(include_stack=False, include_record=False)

    system = """\
你是文本导航器。用工具逐段读取文档，直到读完为止。

每轮只做两件事：
1. read_next()
2. advance_past(to_line=<advance_target>)

done=true 时停止。严禁输出文字。\
"""
    user = "开始。调用 read_next()。"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    rounds = 0
    tool_seq = []
    extract_calls = 0

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
                result_str = execute_tool(state, fn, args)

                # 系统层拦截 read_next 结果
                if fn == "read_next":
                    result_dict = json.loads(result_str)
                    if result_dict.get("content_type") == "lines":
                        candidates = system_filter_candidates(
                            result_dict["lines"], task_key)
                        for cand in candidates:
                            extract_calls += 1
                            extracted = system_extract_name(
                                cand["content"], task_key)
                            if extracted:
                                state.record(extracted["item"],
                                           extracted["category"])
                                print(f"    R{rounds} L{cand['line']}: "
                                      f"'{cand['content'][:40]}' "
                                      f"→ {extracted['item']}")

                tool_seq.append(fn)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_str,
                })

            if state.cursor >= len(text):
                break
        elif finish in ("stop", "length"):
            tool_seq.append("STOP")
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
    metrics = evaluate(task_key, gt, found)
    counts = Counter(tool_seq)

    print(f"  seed={seed}: F1={metrics['f1']:.2f} R={metrics['recall']:.2f} "
          f"P={metrics['precision']:.2f} cov={coverage}% rds={rounds} "
          f"extracts={extract_calls}")
    print(f"    read={counts.get('read_next',0)} "
          f"advance={counts.get('advance_past',0)} "
          f"stops={counts.get('STOP',0)}")
    if metrics['f1'] < 1.0:
        print(f"    GT:    {gt}")
        print(f"    Found: {found}")
    return metrics


def main():
    seeds = [42, 1, 7, 13, 99, 2024]

    print("=" * 60)
    print("系统编排架构")
    print("模型: 纯导航 (read→advance)")
    print("系统: 筛选(确定性) → 提取(隔离微对话) → 记录(自动)")
    print("=" * 60)

    all_metrics = []
    for seed in seeds:
        m = run_test(seed)
        all_metrics.append(m)

    avg_f1 = sum(m["f1"] for m in all_metrics) / len(all_metrics)
    avg_r = sum(m["recall"] for m in all_metrics) / len(all_metrics)
    avg_p = sum(m["precision"] for m in all_metrics) / len(all_metrics)
    perfect = sum(1 for m in all_metrics if m["f1"] >= 0.99)

    print(f"\n{'='*60}")
    print(f"平均: F1={avg_f1:.2f}  R={avg_r:.2f}  P={avg_p:.2f}")
    print(f"完美率: {perfect}/{len(seeds)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
