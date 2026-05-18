"""
在 27B 上用 Condition A（全文直接问答）扫描不同文档长度，找 F1 开始下降的临界点。

策略：
  固定 n_top_level=15（目标数量适中），通过 pad_to_length 把文档填充到不同长度，
  使目标函数散落在越来越长的文档中，模拟真实的"大海捞针"场景。

用法：
    python find_breakpoint.py
"""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "exp2_complex_extraction"))

import config as cfg
import runner as _runner

_runner.API_URL         = cfg.API_URL
_runner.MODEL_NAME      = cfg.MODEL_NAME
_runner.REQUEST_TIMEOUT = cfg.REQUEST_TIMEOUT

_orig_chat = _runner._chat
def _chat_27b(messages, tools=None):
    import requests
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

from runner import run_condition_a
from prompts import SYSTEM_A, TASK_PROMPTS
from evaluate import evaluate
from data_generator import generate_python_file, pad_to_length

# ── 扫描配置 ────────────────────────────────────────────────────────────────
# 每组固定一个变量，改变另一个，用多个 seed 评估稳定性

# 组 A：固定目标数量=5，增加文档长度（pad filler）
GROUP_A = [
    ("A-4k",   5, 0, 0,  4_000),
    ("A-10k",  5, 0, 0, 10_000),
    ("A-20k",  5, 0, 0, 20_000),
    ("A-40k",  5, 0, 0, 40_000),
    ("A-80k",  5, 0, 0, 80_000),
]

# 组 B：固定文档长度~11k（自然长度），增加目标函数数量
GROUP_B = [
    ("B-5f",   5, 2, 3, 0),
    ("B-10f", 10, 3, 3, 0),
    ("B-15f", 15, 4, 4, 0),
    ("B-20f", 20, 5, 4, 0),
    ("B-25f", 25, 6, 4, 0),
]

SEEDS = [42, 1, 7]  # 多个 seed 评估稳定性


def run_one(label: str, n_top: int, n_cls: int, n_mth: int,
            pad_target: int, seed: int) -> dict:
    text, gt = generate_python_file(
        n_top_level=n_top, n_classes=n_cls,
        n_methods_per_class=n_mth, seed=seed,
    )
    if pad_target > len(text):
        text = pad_to_length(text, pad_target, seed=seed)
    user_p = TASK_PROMPTS["python_functions"](text, "A")
    result = run_condition_a(SYSTEM_A, user_p, "python_functions")
    metrics = evaluate("python_functions", gt, result["found"])
    return {
        "label": label, "seed": seed,
        "chars": len(text), "lines": text.count("\n"),
        "n_gt": len(gt), "found": result["found"],
        **metrics,
    }


def main():
    print(f"Model: {cfg.MODEL_NAME}  seeds={SEEDS}")
    print(f"\n{'Label':8s}  {'Chars':>8s}  {'Lines':>6s}  {'nGT':>4s}  "
          f"F1(s42) F1(s1)  F1(s7)  avg_F1")
    print("-" * 72)

    for group_name, group in [("── 组A：固定5个目标，增加文档长度", GROUP_A),
                               ("── 组B：固定~11k长度，增加目标数量", GROUP_B)]:
        print(f"\n{group_name}")
        for row in group:
            label, n_top, n_cls, n_mth, pad = row
            f1s = []
            chars = lines = n_gt = 0
            for seed in SEEDS:
                try:
                    r = run_one(label, n_top, n_cls, n_mth, pad, seed)
                    f1s.append(r["f1"])
                    chars, lines, n_gt = r["chars"], r["lines"], r["n_gt"]
                except Exception as e:
                    f1s.append(-1)
                    print(f"  {label} seed={seed} ERROR: {e}", flush=True)
            avg = sum(x for x in f1s if x >= 0) / max(sum(1 for x in f1s if x >= 0), 1)
            f1_strs = "  ".join(f"{f:.2f}" if f >= 0 else " ERR" for f in f1s)
            print(f"{label:8s}  {chars:>8,d}  {lines:>6d}  {n_gt:>4d}  "
                  f"{f1_strs}  avg={avg:.2f}", flush=True)


if __name__ == "__main__":
    main()
