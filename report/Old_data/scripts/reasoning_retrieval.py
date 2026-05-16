"""
Reasoning Retrieval Test for Qwen3.5 2B via LM Studio

Instead of an explicit label, the model must:
1. Find and understand a rule/criterion hidden in a long context
2. Reason about which word in the text satisfies that rule
3. Return the correct answer

Tests both "rule before answer" and "rule after answer" positions.
"""

import json
import os
import requests

# ── Config ──────────────────────────────────────────────────────────────────
API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"
# ────────────────────────────────────────────────────────────────────────────


# Each test case:
#   rule_snippet   — the sentence defining what to look for (inserted at rule_pos)
#   target_snippet — the sentence containing the answer word (inserted at target_pos)
#   correct_answer — the expected answer
#   question       — what we ask the model
#   rule_pos       — fractional position of the rule in the filler (0.0–1.0)
#   target_pos     — fractional position of the target sentence (0.0–1.0)

TEST_CASES = [
    {
        "name": "Prime number among a list",
        "rule_snippet": (
            "Note: among all numbers appearing in this document, "
            "exactly one of them is a prime number — that number is the special answer."
        ),
        "target_snippet": (
            "The annual audit recorded the following inventory counts: "
            "15 monitors, 23 keyboards, 40 chairs, and 18 desks."
        ),
        # 23 is prime; 15=3×5, 40=2³×5, 18=2×3² — not prime
        "correct_answer": "23",
        "question": (
            "Based on the rule stated in the document, what is the special answer? "
            "Reply with the number only."
        ),
        "rule_pos": 0.15,
        "target_pos": 0.75,
    },
    {
        "name": "Only South American country",
        "rule_snippet": (
            "Important: among all countries mentioned anywhere in this document, "
            "exactly one of them is located in South America — that country is the special answer."
        ),
        "target_snippet": (
            "The international summit was attended by representatives from "
            "Germany, Brazil, Japan, Canada, and Australia."
        ),
        # Brazil is the only South American country
        "correct_answer": "Brazil",
        "question": (
            "Based on the rule stated in the document, what is the special answer? "
            "Reply with the country name only."
        ),
        "rule_pos": 0.80,
        "target_pos": 0.20,
    },
    {
        "name": "Only mammal in a list of animals",
        "rule_snippet": (
            "Rule: this document mentions several animals. "
            "Exactly one of them is a mammal — that animal is the special answer."
        ),
        "target_snippet": (
            "The nature reserve is home to many species: "
            "the golden eagle, the Atlantic salmon, the European hedgehog, "
            "the green sea turtle, and the common frog."
        ),
        # Hedgehog is the only mammal; eagle=bird, salmon=fish, turtle=reptile, frog=amphibian
        "correct_answer": "hedgehog",
        "question": (
            "Based on the rule stated in the document, what is the special answer? "
            "Reply with the animal name only."
        ),
        "rule_pos": 0.40,
        "target_pos": 0.60,
    },
    {
        "name": "Only odd number",
        "rule_snippet": (
            "Pay attention: somewhere in this text a list of numbers appears. "
            "Exactly one number in that list is odd — that number is the special answer."
        ),
        "target_snippet": (
            "The shipping manifest listed quantities of: 84 units, 37 units, "
            "120 units, 56 units, and 200 units."
        ),
        # 37 is odd; 84, 120, 56, 200 are all even
        "correct_answer": "37",
        "question": (
            "Based on the rule stated in the document, what is the special answer? "
            "Reply with the number only."
        ),
        "rule_pos": 0.10,
        "target_pos": 0.90,
    },
    {
        "name": "Only planet in a list",
        "rule_snippet": (
            "Hidden in this document is a list of words. "
            "Exactly one of those words is the name of a planet in our solar system — "
            "that word is the special answer."
        ),
        "target_snippet": (
            "The scientist's notes referenced several proper nouns: "
            "Everest, Saturn, Sahara, Amazon, and Kilimanjaro."
        ),
        # Saturn is the only planet; others are mountains/deserts/rivers
        "correct_answer": "Saturn",
        "question": (
            "Based on the rule stated in the document, what is the special answer? "
            "Reply with the word only."
        ),
        "rule_pos": 0.50,
        "target_pos": 0.50,
    },
]


FILLER_SENTENCES = (
    "The global economy has faced unprecedented challenges over the past decade, "
    "driven by technological disruption and shifting geopolitical alliances. "
    "Researchers continue to explore the fundamental properties of matter and energy "
    "at scales both cosmic and subatomic. "
    "Urban planners are rethinking city infrastructure to accommodate growing populations "
    "while reducing environmental impact. "
    "The development of artificial intelligence has accelerated across industries, "
    "raising important questions about ethics, employment, and human creativity. "
    "Historical records indicate that trade routes connected distant civilizations "
    "long before the modern era of globalization. "
    "Marine biologists have documented thousands of previously unknown species "
    "in the deep ocean trenches of the Pacific. "
    "Advances in renewable energy technology are making solar and wind power "
    "increasingly competitive with fossil fuels. "
    "Linguists study how languages evolve, merge, and sometimes disappear "
    "as communities change over time. "
    "The human brain remains one of the most complex and least understood organs, "
    "despite decades of intensive neuroscience research. "
    "Agricultural innovations have transformed food production methods, "
    "though debates continue about sustainability and nutritional value. "
)


def make_filler(num_words: int) -> list[str]:
    words = []
    source = FILLER_SENTENCES.split()
    while len(words) < num_words:
        words.extend(source)
    return words[:num_words]


def build_context(filler_words: list[str], insertions: list[tuple[float, str]]) -> str:
    """Insert multiple snippets at their fractional positions."""
    # Sort by position so we insert in order
    insertions = sorted(insertions, key=lambda x: x[0])

    # Build list of (word_index, snippet) pairs
    n = len(filler_words)
    parts = []
    prev_idx = 0

    for pos, snippet in insertions:
        idx = int(n * pos)
        parts.append(" ".join(filler_words[prev_idx:idx]))
        parts.append(snippet)
        prev_idx = idx

    parts.append(" ".join(filler_words[prev_idx:]))
    return " ".join(p for p in parts if p).strip()


def ask_model(context: str, question: str) -> tuple[str, str]:
    """Returns (final_answer, full_reasoning_content)."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a careful reading comprehension assistant. "
                    "Read the entire provided text, find the stated rule, "
                    "then reason step by step to identify which word/number satisfies the rule. "
                    "At the very end, write exactly: 'Final answer: <your answer>'"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Read the following long text carefully:\n\n"
                    f"{context}\n\n"
                    f"---\n\n"
                    f"{question}\n\n"
                    f"Think step by step, then end with 'Final answer: <your answer>'"
                ),
            },
        ],
        "temperature": 0.0,
        "max_tokens": 2048,
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=600)
        resp.raise_for_status()
        msg      = resp.json()["choices"][0]["message"]
        full_out = msg.get("content", "").strip()

        # Extract "Final answer: X" from the last lines
        final_answer = full_out
        for line in reversed(full_out.splitlines()):
            line = line.strip()
            if line.lower().startswith("final answer"):
                final_answer = line.split(":", 1)[-1].strip()
                break

        return final_answer, full_out
    except requests.exceptions.RequestException as e:
        return f"[ERROR] {e}", ""


def check_answer(model_answer: str, correct: str) -> bool:
    return correct.lower() in model_answer.lower()


def run_test(filler_words_count: int = 2000):
    print("=" * 65)
    print("  Reasoning Retrieval Test — Qwen3.5 2B  [THINKING MODE ON]")
    print("=" * 65)
    print(f"  Model        : {MODEL_NAME}")
    print(f"  Filler words : ~{filler_words_count}")
    print(f"  Test cases   : {len(TEST_CASES)}")
    print(f"  Thinking     : enabled  (max_tokens=1024)")
    print("=" * 65)
    print()

    filler = make_filler(filler_words_count)
    results = []

    for i, tc in enumerate(TEST_CASES, 1):
        name        = tc["name"]
        rule_pos    = tc["rule_pos"]
        target_pos  = tc["target_pos"]
        correct     = tc["correct_answer"]
        question    = tc["question"]

        # Avoid inserting at the exact same position
        if abs(rule_pos - target_pos) < 0.01:
            target_pos += 0.01

        insertions = [
            (rule_pos,   tc["rule_snippet"]),
            (target_pos, tc["target_snippet"]),
        ]
        context    = build_context(filler, insertions)
        word_count = len(context.split())

        order = "rule→target" if rule_pos < target_pos else "target→rule"
        print(f"[{i}/{len(TEST_CASES)}] {name}")
        print(f"   Rule at {int(rule_pos*100):>3}%  |  Target at {int(target_pos*100):>3}%  |  Order: {order}  |  ~{word_count} words")
        print(f"   Expected : {correct}")
        print(f"   Asking model ... ", end="", flush=True)

        answer, reasoning = ask_model(context, question)
        correct_flag = check_answer(answer, correct)
        status  = "PASS ✓" if correct_flag else "FAIL ✗"

        print(status)
        if reasoning:
            short = reasoning[:350].replace("\n", " ")
            print(f"   Reasoning    : {short}{'...' if len(reasoning) > 350 else ''}")
            print(f"   Chain length : {len(reasoning)} chars")
        print(f"   Final answer : {answer[:120]}")
        print()

        results.append({
            "name":      name,
            "correct":   correct_flag,
            "answer":    answer,
            "reasoning": reasoning,
            "order":     order,
        })

    # ── Summary ──────────────────────────────────────────────────────────────
    print("=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    passed = sum(1 for r in results if r["correct"])
    total  = len(results)
    print(f"  Score: {passed}/{total}  ({int(passed/total*100)}%)\n")

    for r in results:
        icon = "✓" if r["correct"] else "✗"
        think_len = len(r.get("reasoning", ""))
        think_note = f"  thinking={think_len} chars" if think_len else "  no thinking"
        print(f"  [{icon}] {r['name']}  ({r['order']}){think_note}")
        if not r["correct"]:
            print(f"       Got: {r['answer'][:80]}")

    print("=" * 65)


if __name__ == "__main__":
    run_test(filler_words_count=2000)
