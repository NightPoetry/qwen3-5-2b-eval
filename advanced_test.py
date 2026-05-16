"""
Advanced Long-Context Test for Qwen3.5 2B via LM Studio

Part 1 — Harder problem identification:
  A. Multi-hop reasoning  (find X, use X to find Y)
  B. Distractor trap      (two candidates, only one satisfies ALL conditions)
  C. Nested rule          (rule that points to another rule)
  D. Contradictory clues  (earlier info is overridden later)

Part 2 — Function Calling:
  F1. Single function, extract one param from long context
  F2. Single function, extract multiple params
  F3. Choose correct function among three (wrong ones are decoys in context)
"""

import json
import os
import requests

API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"

FILLER = (
    "The global economy has faced unprecedented challenges over the past decade, "
    "driven by technological disruption and shifting geopolitical alliances. "
    "Researchers continue to explore the fundamental properties of matter and energy "
    "at scales both cosmic and subatomic. "
    "Urban planners are rethinking city infrastructure to accommodate growing populations "
    "while reducing environmental impact. "
    "Historical records indicate that trade routes connected distant civilizations "
    "long before the modern era of globalization. "
    "Marine biologists have documented thousands of previously unknown species "
    "in the deep ocean trenches of the Pacific. "
    "Advances in renewable energy technology are making solar and wind power "
    "increasingly competitive with fossil fuels. "
    "The human brain remains one of the most complex and least understood organs, "
    "despite decades of intensive neuroscience research. "
)


def make_filler(n_words: int) -> list[str]:
    src = FILLER.split()
    out = []
    while len(out) < n_words:
        out.extend(src)
    return out[:n_words]


def build_context(filler: list[str], insertions: list[tuple[float, str]]) -> str:
    insertions = sorted(insertions, key=lambda x: x[0])
    n, parts, prev = len(filler), [], 0
    for pos, snippet in insertions:
        idx = max(prev + 1, int(n * pos))
        parts.append(" ".join(filler[prev:idx]))
        parts.append(snippet)
        prev = idx
    parts.append(" ".join(filler[prev:]))
    return " ".join(p for p in parts if p).strip()


# ── shared call helper ────────────────────────────────────────────────────────

def call(messages: list[dict], tools: list[dict] | None = None,
         max_tokens: int = 2048) -> dict:
    payload: dict = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    resp = requests.post(API_URL, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["choices"][0]


def extract_final(text: str) -> str:
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.lower().startswith("final answer"):
            return line.split(":", 1)[-1].strip()
    return text.strip()


# ═══════════════════════════════════════════════════════════════════════════
# PART 1 — Harder problem identification
# ═══════════════════════════════════════════════════════════════════════════

PART1_CASES = [

    # ── A. Multi-hop ────────────────────────────────────────────────────────
    {
        "name": "A. Multi-hop reasoning",
        "desc": "Find the code word → use code word to find the final answer",
        "insertions": [
            (0.10, (
                "RULE-1: The code word in this document is the name of the ocean "
                "that appears exactly once. Use the code word to look up RULE-2."
            )),
            (0.40, (
                "RULE-2: If the code word is 'Arctic', the final answer is 42. "
                "If the code word is 'Indian', the final answer is 87. "
                "If the code word is 'Atlantic', the final answer is 19."
            )),
            (0.75, (
                "A shipping lane crosses the Indian Ocean connecting major port cities "
                "on three continents."
            )),
        ],
        "question": (
            "Follow RULE-1 and RULE-2 stated in the text. "
            "What is the final answer? Think step by step, end with 'Final answer: X'"
        ),
        "correct": "87",
    },

    # ── B. Distractor trap ──────────────────────────────────────────────────
    {
        "name": "B. Distractor trap",
        "desc": "Two numbers look like answers, only one satisfies ALL three conditions",
        "insertions": [
            (0.10, (
                "CONDITION-1: The special number is greater than 30."
            )),
            (0.35, (
                "CONDITION-2: The special number is odd."
            )),
            (0.60, (
                "CONDITION-3: The special number is a multiple of 7."
            )),
            (0.80, (
                "The lab report noted two candidate values: 35 and 49. "
                "Only one of them satisfies all three conditions above."
            )),
        ],
        "question": (
            "Based on the three conditions stated in the document, "
            "which of the two candidate values (35 or 49) is the special number? "
            "Think step by step, end with 'Final answer: X'"
        ),
        "correct": "49",
        # 35: >30 ✓, odd ✓, 35/7=5 ✓ — wait, 35 satisfies all three too!
        # Let me reconsider... 35>30 ✓, odd ✓, 35=5×7 ✓ so 35 works too.
        # Change CONDITION-1 to >40 so only 49 works.
        # Actually I'll fix this in the snippet below.
    },

    # ── C. Nested rule ──────────────────────────────────────────────────────
    {
        "name": "C. Nested / indirect rule",
        "desc": "Rule A points to Rule B which defines what to look for",
        "insertions": [
            (0.20, (
                "META-RULE: Ignore any rule labeled ALPHA. "
                "The only valid rule is the one labeled BETA."
            )),
            (0.45, (
                "RULE ALPHA: The answer is the largest city mentioned in this document."
            )),
            (0.65, (
                "RULE BETA: The answer is the smallest number mentioned in this document."
            )),
            (0.85, (
                "The survey covered populations in three cities: "
                "Tokyo with 13,960,000 residents, Oslo with 693,000 residents, "
                "and Cairo with 10,100,000 residents. "
                "Infrastructure budgets were 450, 820, and 310 million dollars respectively."
            )),
        ],
        "question": (
            "Follow the META-RULE, then the correct sub-rule, to find the answer. "
            "Think step by step, end with 'Final answer: X'"
        ),
        "correct": "310",
        # BETA says smallest number. Numbers: 13960000, 693000, 10100000, 450, 820, 310
        # smallest is 310
    },

    # ── D. Contradiction / override ─────────────────────────────────────────
    {
        "name": "D. Contradiction — later info overrides earlier",
        "desc": "An earlier statement is explicitly corrected later in the document",
        "insertions": [
            (0.15, (
                "The project codename was initially set to FALCON."
            )),
            (0.50, (
                "After the board meeting, a correction was issued: "
                "the project codename FALCON is incorrect. "
                "The official codename was changed to PHOENIX."
            )),
            (0.80, (
                "A second correction notice clarified: the codename PHOENIX "
                "was a temporary placeholder. The final official codename is AURORA."
            )),
        ],
        "question": (
            "What is the final official project codename according to the document? "
            "Think step by step, end with 'Final answer: X'"
        ),
        "correct": "AURORA",
    },
]

# Fix distractor trap: CONDITION-1 should be >40 so only 49 works (35 is not >40)
PART1_CASES[1]["insertions"][0] = (
    0.10,
    "CONDITION-1: The special number is greater than 40."
)
# Now: 35>40? No. 49>40? Yes. 49 odd? Yes. 49=7×7? Yes → 49 is correct.


# ═══════════════════════════════════════════════════════════════════════════
# PART 2 — Function Calling
# ═══════════════════════════════════════════════════════════════════════════

PART2_CASES = [

    # ── F1. Single function, one param ─────────────────────────────────────
    {
        "name": "F1. Extract one param → call function",
        "desc": "Model reads a number buried in text, calls compute_square(n)",
        "insertions": [
            (0.30, (
                "The engineering team finalized the grid dimension: "
                "the base unit size is 17 meters on each side."
            )),
            (0.70, (
                "All subsequent area calculations must use the base unit size "
                "defined earlier in this document."
            )),
        ],
        "question": (
            "Using the base unit size defined in the document, "
            "call the appropriate function to compute its square area."
        ),
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "compute_square",
                    "description": "Computes the square of a number (n × n).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "n": {"type": "number", "description": "The number to square"}
                        },
                        "required": ["n"],
                    },
                },
            }
        ],
        "expected_fn":     "compute_square",
        "expected_args":   {"n": 17},
    },

    # ── F2. Single function, multiple params ────────────────────────────────
    {
        "name": "F2. Extract multiple params → call function",
        "desc": "Model extracts name + score buried in text, calls register_result()",
        "insertions": [
            (0.25, (
                "Participant registration confirmed: the contestant's name is Elena Vasquez."
            )),
            (0.65, (
                "Final evaluation complete. Elena Vasquez received a score of 94 points "
                "in the technical assessment."
            )),
        ],
        "question": (
            "Based on the participant information in the document, "
            "call the appropriate function to register the result."
        ),
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "register_result",
                    "description": "Registers a participant's final score.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "participant_name": {"type": "string", "description": "Full name of the participant"},
                            "score":            {"type": "number", "description": "Final score (0–100)"},
                        },
                        "required": ["participant_name", "score"],
                    },
                },
            }
        ],
        "expected_fn":   "register_result",
        "expected_args": {"participant_name": "Elena Vasquez", "score": 94},
    },

    # ── F3. Choose correct function among three decoys ──────────────────────
    {
        "name": "F3. Function selection — three tools, pick the right one",
        "desc": "Context hints at translation; model must choose translate(), not the decoys",
        "insertions": [
            (0.20, (
                "The document processing pipeline includes three available operations: "
                "summarization, translation, and sentiment analysis."
            )),
            (0.55, (
                "The incoming report is written in French and must be converted to English "
                "before distribution to the international team."
            )),
            (0.80, (
                "The target language for all converted documents in this batch is English."
            )),
        ],
        "question": (
            "Based on the document's instructions, call the correct function "
            "with the appropriate parameters."
        ),
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "summarize_text",
                    "description": "Generates a summary of a document.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"}
                        },
                        "required": ["text"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "translate_document",
                    "description": "Translates a document from one language to another.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_language": {"type": "string", "description": "Language of the input document"},
                            "target_language": {"type": "string", "description": "Language to translate into"},
                        },
                        "required": ["source_language", "target_language"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_sentiment",
                    "description": "Analyzes the sentiment of a text (positive/negative/neutral).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"}
                        },
                        "required": ["text"],
                    },
                },
            },
        ],
        "expected_fn":   "translate_document",
        "expected_args": {"source_language": "French", "target_language": "English"},
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# Runners
# ═══════════════════════════════════════════════════════════════════════════

def run_part1(filler: list[str]):
    print("\n" + "═" * 65)
    print("  PART 1 — Harder Problem Identification  (step-by-step)")
    print("═" * 65)
    results = []

    for i, tc in enumerate(PART1_CASES, 1):
        context    = build_context(filler, tc["insertions"])
        word_count = len(context.split())

        print(f"\n[1-{i}] {tc['name']}")
        print(f"  {tc['desc']}")
        print(f"  Context: ~{word_count} words  |  Expected: {tc['correct']}")
        print(f"  Asking ... ", end="", flush=True)

        choice = call([
            {
                "role": "system",
                "content": (
                    "You are a precise reading comprehension assistant. "
                    "Read the full text, follow every rule/condition carefully, "
                    "reason step by step, and end with 'Final answer: X'."
                ),
            },
            {
                "role": "user",
                "content": f"Text:\n\n{context}\n\n---\n\n{tc['question']}",
            },
        ])

        raw     = choice["message"]["content"].strip()
        answer  = extract_final(raw)
        correct = tc["correct"].lower() in answer.lower()
        status  = "PASS ✓" if correct else "FAIL ✗"
        print(status)

        short_reasoning = raw[:400].replace("\n", " ")
        print(f"  Reasoning : {short_reasoning}{'...' if len(raw) > 400 else ''}")
        print(f"  Answer    : {answer[:100]}")

        results.append({"name": tc["name"], "correct": correct, "answer": answer})

    return results


def run_part2(filler: list[str]):
    print("\n" + "═" * 65)
    print("  PART 2 — Function Calling")
    print("═" * 65)
    results = []

    for i, tc in enumerate(PART2_CASES, 1):
        context    = build_context(filler, tc["insertions"])
        word_count = len(context.split())

        print(f"\n[2-{i}] {tc['name']}")
        print(f"  {tc['desc']}")
        print(f"  Context: ~{word_count} words  |  Expected fn: {tc['expected_fn']}")
        print(f"  Expected args: {tc['expected_args']}")
        print(f"  Asking ... ", end="", flush=True)

        choice = call(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a function-calling assistant. "
                        "Read the provided text carefully and call the most appropriate "
                        "function with the correct parameters extracted from the text."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Text:\n\n{context}\n\n---\n\n{tc['question']}",
                },
            ],
            tools=tc["tools"],
        )

        finish_reason = choice.get("finish_reason", "")
        tool_calls    = choice["message"].get("tool_calls") or []

        if not tool_calls:
            # Model replied in text instead of calling a function
            text_reply = choice["message"].get("content", "")
            print("FAIL ✗  (no function call made)")
            print(f"  Model replied in text: {text_reply[:200]}")
            results.append({"name": tc["name"], "correct": False,
                            "fn": None, "args": {}})
            continue

        tc_call   = tool_calls[0]
        fn_name   = tc_call["function"]["name"]
        try:
            fn_args = json.loads(tc_call["function"]["arguments"])
        except json.JSONDecodeError:
            fn_args = {}

        fn_correct   = fn_name == tc["expected_fn"]
        args_correct = all(
            str(fn_args.get(k, "")).lower() == str(v).lower()
            for k, v in tc["expected_args"].items()
        )
        correct = fn_correct and args_correct
        status  = "PASS ✓" if correct else ("PASS (fn ok, args off) ~" if fn_correct else "FAIL ✗")
        print(status)
        print(f"  Called    : {fn_name}({fn_args})")
        if not fn_correct:
            print(f"  Expected  : {tc['expected_fn']}({tc['expected_args']})")
        elif not args_correct:
            print(f"  Expected args: {tc['expected_args']}")

        results.append({
            "name":    tc["name"],
            "correct": correct,
            "fn":      fn_name,
            "args":    fn_args,
        })

    return results


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  Advanced Long-Context Test — Qwen3.5 2B")
    print("=" * 65)
    print(f"  Model : {MODEL_NAME}  |  Filler: ~2000 words per test")

    filler  = make_filler(2000)
    r1      = run_part1(filler)
    r2      = run_part2(filler)

    all_results = r1 + r2
    passed  = sum(1 for r in all_results if r["correct"])
    total   = len(all_results)

    print("\n" + "=" * 65)
    print("  FINAL SUMMARY")
    print("=" * 65)
    print(f"  Total score: {passed}/{total}\n")
    print("  Part 1 — Problem Identification:")
    for r in r1:
        print(f"    {'✓' if r['correct'] else '✗'}  {r['name']}")
    print("  Part 2 — Function Calling:")
    for r in r2:
        print(f"    {'✓' if r['correct'] else '✗'}  {r['name']}")
    print("=" * 65)


if __name__ == "__main__":
    main()
