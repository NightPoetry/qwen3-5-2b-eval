"""
单条用例快速验证——确认 27B 模型能正常走完工具循环。

用法：
    python run_one.py [--task python|html|mini] [--cond A|B|C] [--seed N]
"""

import argparse
import sys
import os
from pathlib import Path
from collections import Counter

# 复用 exp2 的核心模块
sys.path.insert(0, str(Path(__file__).parent.parent / "exp2_complex_extraction"))

import config as cfg

# 注入 27B 配置（含 max_tokens patch）
import runner as _runner
_runner.API_URL         = cfg.API_URL
_runner.MODEL_NAME      = cfg.MODEL_NAME
_runner.REQUEST_TIMEOUT = cfg.REQUEST_TIMEOUT

_orig_chat = _runner._chat
def _chat_27b(messages, tools=None):
    import requests, json as _json
    payload = {
        "model":       _runner.MODEL_NAME,
        "messages":    messages,
        "temperature": 0.0,
        "max_tokens":  cfg.MAX_TOKENS,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    resp = requests.post(_runner.API_URL, json=payload, timeout=_runner.REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]
_runner._chat = _chat_27b
_runner.MAX_ROUNDS = cfg.MAX_ROUNDS

from runner import run_condition_a, run_condition_b, run_condition_c
from prompts import SYSTEM_A, SYSTEM_B, SYSTEM_C, TASK_PROMPTS
from evaluate import evaluate
from data_generator import generate_python_file, generate_html_file, generate_minified_python


GENERATORS = {
    "python": lambda seed: generate_python_file(n_top_level=5, n_classes=2, n_methods_per_class=3, seed=seed),
    "html":   lambda seed: generate_html_file(n_headings=10, seed=seed),
    "mini":   lambda seed: generate_minified_python(n_functions=5, seed=seed),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="python", choices=["python", "html", "mini"])
    ap.add_argument("--cond", default="B", choices=["A", "B", "C"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n_top", type=int, default=5,  help="顶级函数数量（python任务）")
    ap.add_argument("--n_cls", type=int, default=2,  help="类数量（python任务）")
    ap.add_argument("--n_mth", type=int, default=3,  help="每类方法数（python任务）")
    args = ap.parse_args()

    task_key = {"python": "python_functions", "html": "html_headings", "mini": "minified_python"}[args.task]
    if args.task == "python":
        text, gt = generate_python_file(
            n_top_level=args.n_top, n_classes=args.n_cls,
            n_methods_per_class=args.n_mth, seed=args.seed)
    else:
        text, gt = GENERATORS[args.task](args.seed)
    user_p = TASK_PROMPTS[task_key](text, args.cond)

    print(f"Model : {cfg.MODEL_NAME}  (@{cfg.API_URL})")
    print(f"Task  : {task_key}  Condition: {args.cond}  Seed: {args.seed}")
    print(f"GT    : {gt}")
    print(f"Lines : {text.count(chr(10))}  Chars: {len(text)}")
    print()

    if args.cond == "A":
        result = run_condition_a(SYSTEM_A, user_p, task_key)
    elif args.cond == "B":
        result = run_condition_b(SYSTEM_B, user_p, text, task_key,
                                 history_window=cfg.HISTORY_WINDOW)
    else:
        result = run_condition_c(SYSTEM_C, user_p, text, task_key)

    metrics = evaluate(task_key, gt, result["found"])

    print(f"Found : {result['found']}")
    print(f"F1={metrics['f1']:.2f}  R={metrics['recall']:.2f}  P={metrics['precision']:.2f}")

    if args.cond in ("B", "C"):
        print(f"Coverage: {result['coverage_pct']}%  Rounds: {result['rounds']}")
        if "tool_call_log" in result:
            call_names = Counter(c["tool"] for c in result["tool_call_log"])
            print(f"Tool calls: {dict(call_names)}")


if __name__ == "__main__":
    main()
