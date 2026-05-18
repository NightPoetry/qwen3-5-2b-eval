"""
Test data generator for complex extraction experiments.

Produces three task types, each with deterministic ground truth:
  1. python_functions  — find all top-level function names in Python code
  2. html_headings     — find all headings (level + text) in an HTML document
  3. minified_python   — top-level functions in whitespace-stripped Python

Each generator returns (text: str, ground_truth: list).
"""

import random
import textwrap

# ── Vocabulary ────────────────────────────────────────────────────────────────

_FUNC_NAMES = [
    "calculate_total", "process_batch", "validate_schema", "parse_config",
    "initialize_engine", "cleanup_resources", "generate_report", "fetch_records",
    "update_index", "serialize_payload", "deserialize_response", "authenticate",
    "authorize_request", "log_event", "send_alert", "compress_data",
    "extract_features", "transform_matrix", "aggregate_stats", "filter_outliers",
    "normalize_vector", "cache_result", "invalidate_cache", "retry_request",
    "schedule_job", "cancel_task", "merge_branches", "rebase_commits",
    "diff_snapshots", "restore_backup",
]

_CLASS_NAMES = [
    "DataProcessor", "EventBus", "ConfigManager", "RequestHandler",
    "TaskScheduler", "CacheLayer", "AuthProvider", "MetricsCollector",
]

_NESTED_NAMES = [
    "_helper", "_inner", "_callback", "_reducer", "_transformer",
    "_validator", "_builder", "_resolver",
]

_HEADING_TEXTS = [
    "Introduction", "Overview", "Getting Started", "Installation",
    "Configuration", "Usage", "API Reference", "Examples",
    "Advanced Topics", "Performance", "Security", "Troubleshooting",
    "FAQ", "Changelog", "Contributing", "License",
    "Architecture", "Data Model", "Authentication", "Deployment",
    "Monitoring", "Testing", "Migration Guide", "Appendix",
]

_FILLER_SENTENCES = [
    "This module provides core utilities for data transformation.",
    "All public methods are thread-safe unless otherwise noted.",
    "Raises ValueError if the input does not conform to the schema.",
    "See the configuration reference for available options.",
    "Returns None if the resource could not be located.",
    "Logs a warning when the retry budget is exhausted.",
    "The default timeout is 30 seconds.",
    "Caches results for up to 5 minutes by default.",
]


# ── Python code generator ─────────────────────────────────────────────────────

def _make_docstring(indent: str) -> str:
    sentence = random.choice(_FILLER_SENTENCES)
    return f'{indent}"""{sentence}"""\n'


def _make_function_body(indent: str, add_nested: bool = False) -> str:
    lines = []
    lines.append(f"{indent}result = []")
    lines.append(f"{indent}total = 0")
    lines.append(f"{indent}for i in range(len(data) if hasattr(locals(), 'data') else 10):")
    lines.append(f"{indent}    if i % 2 == 0:")
    lines.append(f"{indent}        total += i * factor if 'factor' in dir() else i")
    lines.append(f"{indent}    else:")
    lines.append(f"{indent}        result.append(i)")
    if add_nested:
        nested = random.choice(_NESTED_NAMES)
        lines.append(f"{indent}def {nested}(x):")
        lines.append(f"{indent}    return x * 2")
        lines.append(f"{indent}result = list(map({nested}, result))")
    lines.append(f"{indent}return result")
    return "\n".join(lines)


def _make_class(class_name: str, method_names: list[str]) -> str:
    lines = [f"class {class_name}:"]
    lines.append(f'    """{random.choice(_FILLER_SENTENCES)}"""')
    lines.append("")
    lines.append("    def __init__(self):")
    lines.append("        self._state = {}")
    lines.append("        self._cache = []")
    lines.append("")
    for m in method_names:
        lines.append(f"    def {m}(self, value=None):")
        lines.append(_make_function_body("        ", add_nested=False))
        lines.append("")
    return "\n".join(lines)


def generate_python_file(
    n_top_level: int = 8,
    n_classes: int = 2,
    n_methods_per_class: int = 3,
    seed: int = 42,
) -> tuple[str, list[str]]:
    """
    Returns (python_source, top_level_function_names).
    Top-level = defined at module scope, not inside a class or another function.
    """
    rng = random.Random(seed)
    available = list(_FUNC_NAMES)
    rng.shuffle(available)

    top_level_names = available[:n_top_level]
    method_pool = available[n_top_level:]

    blocks = []

    # Module header
    blocks.append('"""Auto-generated module for extraction experiments."""\n')
    blocks.append("import os\nimport sys\nimport json\nfrom typing import Any, Optional\n")

    # Interleave top-level functions and classes
    func_idx = 0
    class_idx = 0
    order = (["func"] * n_top_level + ["class"] * n_classes)
    rng.shuffle(order)

    for kind in order:
        if kind == "func":
            name = top_level_names[func_idx]
            func_idx += 1
            has_nested = rng.random() < 0.4
            sig_extras = rng.choice(["", ", timeout=30", ", verbose=False", ", config=None"])
            block = (
                f"def {name}(data{sig_extras}):\n"
                + _make_docstring("    ")
                + _make_function_body("    ", add_nested=has_nested)
                + "\n"
            )
            blocks.append(block)
        else:
            cls_name = _CLASS_NAMES[class_idx % len(_CLASS_NAMES)]
            class_idx += 1
            methods = method_pool[:n_methods_per_class]
            method_pool = method_pool[n_methods_per_class:]
            if not methods:
                continue
            blocks.append(_make_class(cls_name, methods) + "\n")

    # Module-level constants and filler at end
    blocks.append("# ── Constants ────────────────────────────────────────\n")
    blocks.append("DEFAULT_TIMEOUT = 30\nMAX_RETRIES = 3\nVERSION = '1.0.0'\n")

    source = "\n\n".join(blocks)
    return source, sorted(top_level_names)


# ── HTML generator ────────────────────────────────────────────────────────────

def _html_heading(level: int, text: str, indent: str) -> str:
    return f"{indent}<h{level}>{text}</h{level}>"


def _html_paragraph(indent: str) -> str:
    sentence = random.choice(_FILLER_SENTENCES)
    return f"{indent}<p>{sentence} {random.choice(_FILLER_SENTENCES)}</p>"


def generate_html_file(
    n_headings: int = 12,
    seed: int = 42,
) -> tuple[str, list[dict]]:
    """
    Returns (html_source, headings).
    headings is a list of {"level": int, "text": str} dicts in document order.
    """
    rng = random.Random(seed)
    texts = list(_HEADING_TEXTS)
    rng.shuffle(texts)
    texts = (texts * 3)[:n_headings]

    ground_truth = []
    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <title>Experiment Document</title>",
        "</head>",
        "<body>",
    ]

    # Build a realistic hierarchy: one h1, then h2/h3 sections
    heading_idx = 0

    # h1 title
    if heading_idx < n_headings:
        text = texts[heading_idx]
        heading_idx += 1
        lines.append(f"  {_html_heading(1, text, '')}")
        ground_truth.append({"level": 1, "text": text})

    # Sections
    section_count = max(1, (n_headings - 1) // 3)
    for s in range(section_count):
        if heading_idx >= n_headings:
            break
        lines.append("  <section>")
        text = texts[heading_idx]
        heading_idx += 1
        lines.append(f"    {_html_heading(2, text, '')}")
        ground_truth.append({"level": 2, "text": text})

        for _ in range(rng.randint(1, 3)):
            lines.append(_html_paragraph("    "))

        # h3 subsections
        n_sub = rng.randint(1, 2)
        for _ in range(n_sub):
            if heading_idx >= n_headings:
                break
            lines.append("    <div>")
            text = texts[heading_idx]
            heading_idx += 1
            lines.append(f"      {_html_heading(3, text, '')}")
            ground_truth.append({"level": 3, "text": text})
            for _ in range(rng.randint(2, 4)):
                lines.append(_html_paragraph("      "))
            lines.append("    </div>")

        lines.append("  </section>")

    # Any remaining headings at h4
    while heading_idx < n_headings:
        text = texts[heading_idx]
        heading_idx += 1
        lines.append(f"  {_html_heading(4, text, '')}")
        ground_truth.append({"level": 4, "text": text})
        lines.append(_html_paragraph("  "))

    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines), ground_truth


# ── Minified Python generator ─────────────────────────────────────────────────

def generate_minified_python(
    n_functions: int = 6,
    seed: int = 42,
) -> tuple[str, list[str]]:
    """
    Returns (minified_source, function_names).
    Source has NO newlines — functions separated by semicolons.
    Simulates minified/obfuscated code to stress-test boundary detection.
    """
    rng = random.Random(seed)
    available = list(_FUNC_NAMES)
    rng.shuffle(available)
    names = available[:n_functions]

    parts = []
    for name in names:
        # Simple one-liner functions joined with semicolons
        body = "result=[];total=0;[result.append(i) for i in range(10) if i%2==0];return result"
        parts.append(f"def {name}(data,config=None):{body}")

    # Glue with semicolons (no newlines)
    source = ";".join(parts) + ";"
    return source, sorted(names)


# ── Convenience: scale up by repeating/padding ───────────────────────────────

def pad_to_length(text: str, target_chars: int, seed: int = 0) -> str:
    """Repeat filler comments until text reaches roughly target_chars."""
    rng = random.Random(seed)
    while len(text) < target_chars:
        line = f"# {rng.choice(_FILLER_SENTENCES)}\n"
        text += line
    return text


# ── Quick smoke test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    code, gt = generate_python_file(n_top_level=5, n_classes=2)
    print(f"Python ({len(code)} chars), ground truth: {gt}\n")
    print(code[:500])
    print("...")

    html, gt2 = generate_html_file(n_headings=8)
    print(f"\nHTML ({len(html)} chars), ground truth: {gt2}\n")
    print(html[:500])

    mini, gt3 = generate_minified_python(n_functions=4)
    print(f"\nMinified ({len(mini)} chars), ground truth: {gt3}\n")
    print(mini[:300])
