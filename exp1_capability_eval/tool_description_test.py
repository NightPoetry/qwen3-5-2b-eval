"""
Tool Description Quality Test — Qwen3.5 2B (remote server)

Compares 4 description styles across 20 math questions of 4 types:
  A — Direct arithmetic       ("what is 347 * 29")
  B — One-step word problem   ("I have X items at price Y, total cost?")
  C — Multi-step word problem (must derive formula first)
  D — Formula / applied math  (physics, geometry, finance)

Styles tested:
  EN-STRONG    — English, mandatory language
  CN-WEAK      — Chinese, vague
  CN-STRONG    — Chinese, mandatory language
  CN-PATCHED   — CN-STRONG + extra rule for word problems
"""

import json
import os
import requests
from collections import defaultdict

API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"

# ── Tool definitions ──────────────────────────────────────────────────────────

def make_tool(description: str, param_description: str) -> dict:
    return {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": param_description,
                    },
                },
                "required": ["expression"],
            },
        },
    }


TOOL_EN_STRONG = make_tool(
    description=(
        "REQUIRED: You MUST call this tool for ANY arithmetic computation — "
        "multiplication, division, addition, subtraction, or combinations. "
        "Do NOT compute numbers yourself; always delegate to this tool."
    ),
    param_description=(
        "The exact arithmetic expression. Numbers and operators only, "
        "e.g. '347 * 29', '(128 * 3) - 45'. No words or units."
    ),
)

TOOL_CN_WEAK = make_tool(
    description="一个计算器，可以用来计算数学表达式。",
    param_description="数学表达式，例如 '347 * 29'",
)

TOOL_CN_STRONG = make_tool(
    description=(
        "【必须调用】遇到任何数值计算（加减乘除、百分比、多步运算）时，"
        "必须调用此工具，不得自行心算或推导。"
        "触发条件：只要问题涉及具体数字的运算，无论简单还是复杂，都必须使用此工具。"
        "禁止在不调用此工具的情况下给出任何计算结果。"
    ),
    param_description=(
        "标准数学表达式，只含数字和运算符，例如 '87 * 4.5'、'3 * 128 - 45'。"
        "不要包含汉字、单位或文字说明。"
    ),
)

TOOL_CN_PATCHED = make_tool(
    description=(
        "【必须调用】遇到任何数值计算（加减乘除、百分比、多步运算）时，"
        "必须调用此工具，不得自行心算或推导。"
        "触发条件：只要问题涉及具体数字的运算，无论简单还是复杂，都必须使用此工具。"
        "禁止在不调用此工具的情况下给出任何计算结果。"
        "对于需要先理解题意再列算式的文字题，请先在脑中列出算式，"
        "然后将完整算式作为 expression 传入本工具，不得跳过调用直接给答案。"
    ),
    param_description=(
        "标准数学表达式，只含数字和运算符，例如 '87 * 4.5'、'3 * 128 - 45'。"
        "对于多步计算，请写成完整表达式如 '(50 * 12) * 1.08'，不要省略任何步骤。"
        "不要包含汉字、单位或文字说明。"
    ),
)

STYLES = [
    ("EN-STRONG",  TOOL_EN_STRONG),
    ("CN-WEAK",    TOOL_CN_WEAK),
    ("CN-STRONG",  TOOL_CN_STRONG),
    ("CN-PATCHED", TOOL_CN_PATCHED),
]

# ── 20 Test cases ─────────────────────────────────────────────────────────────
# type: A=direct arithmetic, B=one-step word, C=multi-step word, D=applied formula

TEST_CASES = [
    # ── Type A: Direct arithmetic ─────────────────────────────────────────────
    {"type": "A", "q": "What is 347 multiplied by 29?",                          "key": "347"},
    {"type": "A", "q": "Calculate 1024 divided by 32.",                           "key": "1024"},
    {"type": "A", "q": "What is 568 plus 437 minus 129?",                         "key": "568"},
    {"type": "A", "q": "Compute 75 squared.",                                      "key": "75"},
    {"type": "A", "q": "What is 2 to the power of 10?",                           "key": "2"},

    # ── Type B: One-step word problem ─────────────────────────────────────────
    {"type": "B", "q": "I buy 14 notebooks at $3.50 each. What is the total cost?",          "key": "14"},
    {"type": "B", "q": "A farmer harvests 860 kg of wheat per hectare over 7 hectares. Total yield?", "key": "860"},
    {"type": "B", "q": "A rope is 48.6 meters long and cut into 9 equal pieces. How long is each?",   "key": "48"},
    {"type": "B", "q": "There are 365 days in a year. How many hours is that?",               "key": "365"},
    {"type": "B", "q": "A shirt costs $45. It is on sale at 20% off. What is the sale price?", "key": "45"},

    # ── Type C: Multi-step word problem ──────────────────────────────────────
    {"type": "C", "q": "I have 3 boxes, each containing 128 items. I remove 45 items total. How many remain?",     "key": "128"},
    {"type": "C", "q": "A store sold 200 units at $15 each. The cost of goods was $1800. What is the profit?",     "key": "200"},
    {"type": "C", "q": "A rectangle is 34 cm wide and 52 cm long. What is its perimeter?",                         "key": "34"},
    {"type": "C", "q": "I earn $3200/month. I save 25% and spend the rest. How much do I spend per year?",         "key": "3200"},
    {"type": "C", "q": "A class has 36 students. 1/4 are absent. How many students are present?",                  "key": "36"},

    # ── Type D: Applied formula ───────────────────────────────────────────────
    {"type": "D", "q": "A train travels at 87 km/h for 4.5 hours. Total distance?",                                "key": "87"},
    {"type": "D", "q": "A circle has radius 6 cm. What is its area? (use π ≈ 3.14159)",                           "key": "6"},
    {"type": "D", "q": "I invest $5000 at 4% simple interest for 3 years. How much interest do I earn?",           "key": "5000"},
    {"type": "D", "q": "Water flows at 2.5 liters/second into a 900-liter tank. How many minutes to fill it?",     "key": "900"},
    {"type": "D", "q": "A car uses 7.5 liters per 100 km. How many liters for a 340 km trip?",                     "key": "340"},
]

# ── API call ──────────────────────────────────────────────────────────────────

def ask(question: str, tool: dict) -> dict:
    resp = requests.post(API_URL, json={
        "model":       MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": question},
        ],
        "tools":       [tool],
        "tool_choice": "auto",
        "temperature": 0.0,
        "max_tokens":  256,
    }, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]


def classify(choice: dict, key: str) -> dict:
    finish = choice["finish_reason"]
    msg    = choice["message"]
    if finish == "tool_calls" and msg.get("tool_calls"):
        tc   = msg["tool_calls"][0]
        args = json.loads(tc["function"]["arguments"])
        expr = args.get("expression", "")
        return {"called": True, "expr": expr, "key_ok": key in expr}
    return {"called": False, "expr": "", "key_ok": False,
            "text": (msg.get("content") or "")[:80]}


# ── Runner ────────────────────────────────────────────────────────────────────

def run():
    print("=" * 70)
    print("  Tool Description Quality Test — Qwen3.5 2B")
    print(f"  Server : {API_URL}")
    print(f"  Styles : {[s for s,_ in STYLES]}  |  Questions: {len(TEST_CASES)}")
    print("=" * 70)

    # results[style][type] = [bool, ...]
    results = {s: defaultdict(list) for s, _ in STYLES}

    for qi, tc in enumerate(TEST_CASES, 1):
        print(f"\n[Q{qi:02d}][{tc['type']}] {tc['q']}")
        print("  " + "─" * 64)
        for style, tool in STYLES:
            r = classify(ask(tc["q"], tool), tc["key"])
            results[style][tc["type"]].append(r["called"])
            if r["called"]:
                ok = "✓" if r["key_ok"] else "~"
                print(f"  {style:<12} → CALLED   calculate({r['expr']!r}) {ok}")
            else:
                print(f"  {style:<12} → skipped  \"{r.get('text','')[:60]}\"")

    # ── Summary ───────────────────────────────────────────────────────────────
    types   = ["A", "B", "C", "D"]
    n_each  = {t: sum(1 for tc in TEST_CASES if tc["type"] == t) for t in types}
    total   = len(TEST_CASES)

    print("\n" + "=" * 70)
    print("  SUMMARY — call rate by style and question type")
    print(f"  {'Style':<13} {'All':>5}  " + "  ".join(f"[{t}]({n_each[t]}q)" for t in types))
    print("  " + "─" * 60)

    for style, _ in STYLES:
        all_calls  = [v for t in types for v in results[style][t]]
        all_pct    = int(sum(all_calls) / len(all_calls) * 100)
        type_strs  = []
        for t in types:
            vals = results[style][t]
            pct  = int(sum(vals) / len(vals) * 100) if vals else 0
            bar  = "█" * sum(vals) + "░" * (len(vals) - sum(vals))
            type_strs.append(f"{bar} {pct:3}%")
        print(f"  {style:<13} {all_pct:4}%  " + "  ".join(type_strs))

    print()
    print("  Question types:")
    print("  A = Direct arithmetic  B = One-step word  C = Multi-step word  D = Applied formula")

    # Highlight patch effect on type C
    print()
    cn_s_c  = int(sum(results["CN-STRONG"]["C"])  / n_each["C"] * 100)
    cn_p_c  = int(sum(results["CN-PATCHED"]["C"]) / n_each["C"] * 100)
    delta   = cn_p_c - cn_s_c
    sign    = "+" if delta >= 0 else ""
    print(f"  Patch effect on Type C (multi-step word problems):")
    print(f"    CN-STRONG  → {cn_s_c}%")
    print(f"    CN-PATCHED → {cn_p_c}%  ({sign}{delta}%)")
    print("=" * 70)


if __name__ == "__main__":
    run()
