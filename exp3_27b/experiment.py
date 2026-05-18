"""
27B 并发全量实验。

并发设计：
  - 任务级并发：所有 (task, size, condition) 用例同时投入线程池。
  - 流水线并发：同一文档可切段，多 worker 同时读取各自分段，结果合并。
    （通过 --split N 控制，N=1 表示不切段，即完整文档模式）

用法：
    python experiment.py [--tasks all|python|html|mini] [--conds A B C]
                         [--split N] [--workers N] [--seeds N [N ...]]
                         [--dry-run]
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).parent.parent / "exp2_complex_extraction"))

import config as cfg
import runner as _runner

_runner.API_URL         = cfg.API_URL
_runner.MODEL_NAME      = cfg.MODEL_NAME
_runner.REQUEST_TIMEOUT = cfg.REQUEST_TIMEOUT

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

from runner import run_condition_a, run_condition_b, run_condition_c
from prompts import SYSTEM_A, SYSTEM_B, SYSTEM_C, TASK_PROMPTS
from evaluate import evaluate
from data_generator import (
    generate_python_file, generate_html_file,
    generate_minified_python, pad_to_length,
)

# ── 尺寸配置 ────────────────────────────────────────────────────────────────

SIZES = {
    "python": {
        "small":  dict(n_top_level=5,  n_classes=2, n_methods_per_class=3),
        "medium": dict(n_top_level=10, n_classes=4, n_methods_per_class=4),
        "large":  dict(n_top_level=15, n_classes=6, n_methods_per_class=5),
    },
    "html": {
        "small":  dict(n_headings=10),
        "medium": dict(n_headings=25),
        "large":  dict(n_headings=50),
    },
    "mini": {
        "small":  dict(n_functions=5),
        "medium": dict(n_functions=12),
        "large":  dict(n_functions=20),
    },
}

TASK_KEYS = {
    "python": "python_functions",
    "html":   "html_headings",
    "mini":   "minified_python",
}

SYSTEMS = {"A": SYSTEM_A, "B": SYSTEM_B, "C": SYSTEM_C}

# ── 文档切段工具 ─────────────────────────────────────────────────────────────

def split_text_by_lines(text: str, n_parts: int) -> list[tuple[int, int, str]]:
    """
    把文本按行均分为 n_parts 段。
    返回 [(start_line_1indexed, end_line_1indexed, section_text), ...]
    """
    if n_parts <= 1:
        total = text.count("\n") + 1
        return [(1, total, text)]
    lines = text.split("\n")
    chunk = max(1, len(lines) // n_parts)
    sections = []
    for i in range(n_parts):
        lo = i * chunk
        hi = lo + chunk if i < n_parts - 1 else len(lines)
        section_text = "\n".join(lines[lo:hi])
        sections.append((lo + 1, hi, section_text))
    return sections


# ── 单用例执行 ───────────────────────────────────────────────────────────────

def run_case(task: str, size: str, cond: str, seed: int, n_split: int) -> dict:
    task_key = TASK_KEYS[task]
    gen_kwargs = SIZES[task][size]

    if task == "python":
        text, gt = generate_python_file(seed=seed, **gen_kwargs)
    elif task == "html":
        text, gt = generate_html_file(seed=seed, **gen_kwargs)
    else:
        text, gt = generate_minified_python(seed=seed, **gen_kwargs)

    t0 = time.time()

    if cond == "A":
        user_p = TASK_PROMPTS[task_key](text, "A")
        result = run_condition_a(SYSTEM_A, user_p, task_key)
        found = result["found"]

    elif cond == "B":
        sections = split_text_by_lines(text, n_split)
        all_found: list = []
        total_calls = 0
        total_rounds = 0
        covered_chars = 0

        with ThreadPoolExecutor(max_workers=len(sections)) as sec_ex:
            futs = {}
            for start_line, end_line, sec_text in sections:
                user_p = TASK_PROMPTS[task_key](sec_text, "B")
                f = sec_ex.submit(run_condition_b, SYSTEM_B, user_p, sec_text, task_key)
                futs[f] = sec_text
            for f in as_completed(futs):
                r = f.result()
                all_found.extend(r["found"])
                total_calls  += r["tool_calls"]
                total_rounds += r["rounds"]
                covered_chars += r["cursor_final"]

        # 去重（保序）
        seen = set()
        found = [x for x in all_found if not (x in seen or seen.add(x))]
        result = {
            "condition": "B",
            "found": found,
            "rounds": total_rounds,
            "tool_calls": total_calls,
            "elapsed_s": round(time.time() - t0, 2),
            "n_sections": len(sections),
        }

    else:  # C
        sections = split_text_by_lines(text, n_split)
        all_found = []

        with ThreadPoolExecutor(max_workers=len(sections)) as sec_ex:
            futs = [sec_ex.submit(
                run_condition_c, SYSTEM_C,
                TASK_PROMPTS[task_key](sec_text, "C"),
                sec_text, task_key
            ) for _, _, sec_text in sections]
            for f in as_completed(futs):
                all_found.extend(f.result()["found"])

        seen = set()
        found = [x for x in all_found if not (x in seen or seen.add(x))]
        result = {
            "condition": "C",
            "found": found,
            "elapsed_s": round(time.time() - t0, 2),
            "n_sections": len(sections),
        }

    metrics = evaluate(task_key, gt, found)
    return {
        "task": task, "size": size, "condition": cond, "seed": seed,
        "gt": gt,
        **result,
        **metrics,
    }


# ── 主程序 ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks",   nargs="+", default=["all"])
    ap.add_argument("--conds",   nargs="+", default=["A", "B", "C"])
    ap.add_argument("--seeds",   nargs="+", type=int, default=[42])
    ap.add_argument("--split",   type=int, default=1,
                    help="把文档切成 N 段并行读取（1=不切段）")
    ap.add_argument("--workers", type=int, default=cfg.MAX_WORKERS,
                    help="案例级并发线程数")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tasks = ["python", "html", "mini"] if "all" in args.tasks else args.tasks
    sizes = ["small", "medium", "large"]

    cases = [
        (task, size, cond, seed)
        for task in tasks
        for size in sizes
        for cond in args.conds
        for seed in args.seeds
    ]

    print(f"Model  : {cfg.MODEL_NAME}  (@{cfg.API_URL})")
    print(f"Cases  : {len(cases)}  Workers: {args.workers}  Split: {args.split}")
    print()

    if args.dry_run:
        for c in cases:
            print(f"  {c}")
        return

    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    results = []
    lock = Lock()
    done_count = 0

    def run_and_save(case):
        nonlocal done_count
        task, size, cond, seed = case
        try:
            r = run_case(task, size, cond, seed, args.split)
        except Exception as e:
            r = {"task": task, "size": size, "condition": cond, "seed": seed, "error": str(e)}
        with lock:
            results.append(r)
            done_count += 1
            f1  = r.get("f1", -1)
            cov = r.get("coverage_pct", "?")
            print(f"[{done_count:3d}/{len(cases)}] {task:8s} {size:7s} {cond}  "
                  f"F1={f1:.2f}  cov={cov}%  {r.get('found', r.get('error', ''))}")
        return r

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run_and_save, c) for c in cases]
        for _ in as_completed(futs):
            pass

    elapsed = time.time() - t_start
    avg_f1 = sum(r.get("f1", 0) for r in results) / max(len(results), 1)
    print(f"\n完成 {len(results)} 个用例  平均 F1={avg_f1:.2f}  总耗时={elapsed:.0f}s")

    out_path = out_dir / f"results_{int(time.time())}.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"结果已保存至 {out_path}")


if __name__ == "__main__":
    main()
