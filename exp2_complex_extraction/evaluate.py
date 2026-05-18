"""
Evaluation metrics for extraction results.

evaluate_strings  — for function name lists (exact match)
evaluate_headings — for heading lists (level + normalized text match)
evaluate          — unified entry point
"""

import re
import unicodedata


def _normalize(s: str) -> str:
    """Lowercase, strip, collapse whitespace, remove punctuation noise."""
    s = unicodedata.normalize("NFKC", str(s))
    s = s.lower().strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def evaluate_strings(ground_truth: list[str], found: list[str]) -> dict:
    gt_set = {_normalize(x) for x in ground_truth}
    found_norm = [_normalize(x) for x in found]
    found_set = set(found_norm)

    tp = len(gt_set & found_set)
    fp = len(found_set - gt_set)
    fn = len(gt_set - found_set)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "precision": round(precision, 4),
        "recall":    round(recall, 4),
        "f1":        round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
        "ground_truth_count": len(gt_set),
        "found_count": len(found_set),
        "missed":    sorted(gt_set - found_set),
        "spurious":  sorted(found_set - gt_set),
    }


def evaluate_headings(
    ground_truth: list[dict],
    found: list[dict],
) -> dict:
    """
    Match headings by (level, normalized text).
    A heading is correct only if both level and text match.
    """
    def key(h: dict) -> tuple:
        return (int(h.get("level", 0)), _normalize(h.get("text", "")))

    gt_set    = {key(h) for h in ground_truth}
    found_set = {key(h) for h in found}

    tp = len(gt_set & found_set)
    fp = len(found_set - gt_set)
    fn = len(gt_set - found_set)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "precision": round(precision, 4),
        "recall":    round(recall, 4),
        "f1":        round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
        "ground_truth_count": len(gt_set),
        "found_count": len(found_set),
        "missed":   [{"level": k[0], "text": k[1]} for k in sorted(gt_set - found_set)],
        "spurious": [{"level": k[0], "text": k[1]} for k in sorted(found_set - gt_set)],
    }


def evaluate(task_type: str, ground_truth: list, found: list) -> dict:
    if task_type == "html_headings":
        return evaluate_headings(ground_truth, found)
    else:
        return evaluate_strings(ground_truth, found)
