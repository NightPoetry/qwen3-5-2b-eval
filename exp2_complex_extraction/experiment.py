"""
Main experiment orchestrator.

Runs all three conditions (A / B / C) across multiple tasks and text lengths,
saves results to results/<task>_<length>.json, and prints a summary table.

Usage:
    python experiment.py                    # full run
    python experiment.py --task python      # only python_functions task
    python experiment.py --task html        # only html_headings task
    python experiment.py --task mini        # only minified_python task
    python experiment.py --conditions A B   # skip condition C
    python experiment.py --dry-run          # generate data only, no API calls
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from data_generator import (
    generate_html_file,
    generate_minified_python,
    generate_python_file,
    pad_to_length,
)
from evaluate import evaluate
from prompts import SYSTEM_A, SYSTEM_B, SYSTEM_C, TASK_PROMPTS
from runner import run_condition_a, run_condition_b, run_condition_c

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ── Test matrix ───────────────────────────────────────────────────────────────

# (label, target_chars, generator_kwargs)
TEXT_SIZES = [
    ("2k",  2_000,  {}),
    ("5k",  5_000,  {"n_top_level": 12, "n_classes": 3}),
    ("10k", 10_000, {"n_top_level": 18, "n_classes": 4}),
]

TEXT_SIZES_HTML = [
    ("2k",  2_000,  {"n_headings": 8}),
    ("5k",  5_000,  {"n_headings": 16}),
    ("10k", 10_000, {"n_headings": 24}),
]

TEXT_SIZES_MINI = [
    ("1k", 1_000, {"n_functions": 5}),
    ("2k", 2_000, {"n_functions": 10}),
    ("4k", 4_000, {"n_functions": 18}),
]


# ── Single case runner ────────────────────────────────────────────────────────

def run_case(
    task_type: str,
    size_label: str,
    text: str,
    ground_truth: list,
    conditions: list[str],
    dry_run: bool,
) -> dict:
    system_prompts = {"A": SYSTEM_A, "B": SYSTEM_B, "C": SYSTEM_C}
    task_fn = TASK_PROMPTS[task_type]

    case_result = {
        "task": task_type,
        "size": size_label,
        "text_length": len(text),
        "ground_truth": ground_truth,
        "conditions": {},
    }

    for cond in conditions:
        print(f"  [{task_type} / {size_label} / Condition {cond}]", end=" ", flush=True)
        if dry_run:
            print("(dry-run, skipped)")
            case_result["conditions"][cond] = {"skipped": True}
            continue

        t0 = time.time()
        try:
            user_p = task_fn(text, cond)
            if cond == "A":
                raw = run_condition_a(system_prompts["A"], user_p, task_type)
            elif cond == "B":
                raw = run_condition_b(system_prompts["B"], user_p, text, task_type)
            else:
                raw = run_condition_c(system_prompts["C"], user_p, text, task_type)

            metrics = evaluate(task_type, ground_truth, raw["found"])
            result = {**raw, "metrics": metrics}
            # Remove bulky tool log from top-level summary (kept in full log)
            result.pop("tool_call_log", None)
            elapsed = time.time() - t0
            print(f"F1={metrics['f1']:.2f}  recall={metrics['recall']:.2f}  "
                  f"rounds={raw.get('rounds',1)}  t={elapsed:.0f}s")
        except Exception as e:
            print(f"ERROR: {e}")
            result = {"error": str(e)}

        case_result["conditions"][cond] = result

    return case_result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task",       choices=["python", "html", "mini", "all"], default="all")
    parser.add_argument("--conditions", nargs="+", choices=["A", "B", "C"], default=["A", "B", "C"])
    parser.add_argument("--dry-run",    action="store_true")
    args = parser.parse_args()

    all_results = []

    # ── Python top-level functions ────────────────────────────────────────────
    if args.task in ("python", "all"):
        print("\n=== Task: python_functions ===")
        for label, target, kwargs in TEXT_SIZES:
            code, gt = generate_python_file(**{**{"n_top_level": 8, "n_classes": 2}, **kwargs})
            code = pad_to_length(code, target)
            result = run_case("python_functions", label, code, gt, args.conditions, args.dry_run)
            all_results.append(result)
            out = RESULTS_DIR / f"python_{label}.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # ── HTML headings ─────────────────────────────────────────────────────────
    if args.task in ("html", "all"):
        print("\n=== Task: html_headings ===")
        for label, target, kwargs in TEXT_SIZES_HTML:
            html, gt = generate_html_file(**kwargs)
            html = pad_to_length(html, target, seed=1)
            result = run_case("html_headings", label, html, gt, args.conditions, args.dry_run)
            all_results.append(result)
            out = RESULTS_DIR / f"html_{label}.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # ── Minified Python ───────────────────────────────────────────────────────
    if args.task in ("mini", "all"):
        print("\n=== Task: minified_python ===")
        for label, target, kwargs in TEXT_SIZES_MINI:
            mini, gt = generate_minified_python(**kwargs)
            mini = pad_to_length(mini, target, seed=2)
            result = run_case("minified_python", label, mini, gt, args.conditions, args.dry_run)
            all_results.append(result)
            out = RESULTS_DIR / f"mini_{label}.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # ── Summary table ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"{'Task':<20} {'Size':<6} {'Cond':<5} {'F1':>6} {'Recall':>8} {'Rounds':>7}")
    print("-" * 70)
    for r in all_results:
        for cond, data in r["conditions"].items():
            if data.get("skipped"):
                continue
            m = data.get("metrics", {})
            print(
                f"{r['task']:<20} {r['size']:<6} {cond:<5} "
                f"{m.get('f1', 0):>6.2f} {m.get('recall', 0):>8.2f} "
                f"{data.get('rounds', 1):>7}"
            )
    print("=" * 70)

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\nFull results saved to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
