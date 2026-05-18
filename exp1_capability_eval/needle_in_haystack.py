"""
Needle in a Haystack Test for Qwen3.5 2B via LM Studio
Tests the model's ability to retrieve a hidden word from long contexts.
"""

import json
import os
import requests

# ── Config ──────────────────────────────────────────────────────────────────
API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"

NEEDLE     = "THE SECRET WORD IS: BLUEBERRY"
QUESTION   = "What is the secret word mentioned in the text? Answer with the secret word only."

# How many words of filler text to generate total
TOTAL_FILLER_WORDS = 2000

# Test at these positions (fraction of total context where needle is inserted)
POSITIONS = [0.1, 0.25, 0.5, 0.75, 0.9]
# ────────────────────────────────────────────────────────────────────────────


def make_filler(num_words: int) -> list[str]:
    """Generate a list of filler words (simple repeating sentences)."""
    sentence = (
        "The quick brown fox jumps over the lazy dog. "
        "Scientists have discovered that regular exercise improves cognitive function. "
        "The history of ancient civilizations reveals complex social structures. "
        "Modern technology continues to reshape how people communicate and work. "
    ).split()
    words = []
    while len(words) < num_words:
        words.extend(sentence)
    return words[:num_words]


def build_context(filler_words: list[str], needle: str, position: float) -> str:
    """Insert the needle at the given fractional position within filler text."""
    insert_at = int(len(filler_words) * position)
    before = " ".join(filler_words[:insert_at])
    after  = " ".join(filler_words[insert_at:])
    return f"{before} {needle} {after}".strip()


def ask_model(context: str, question: str) -> str:
    """Send a request to LM Studio and return the model's reply."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Read the provided text carefully and answer the question accurately.",
            },
            {
                "role": "user",
                "content": f"/no_think\n\nHere is a long text:\n\n{context}\n\n---\n\nQuestion: {question}",
            },
        ],
        "temperature": 0.0,
        "max_tokens": 50,
        "thinking": {"type": "disabled"},
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=600)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"[ERROR] {e}"


def check_answer(answer: str, needle: str) -> bool:
    """Return True if the model's answer contains the secret word."""
    secret = needle.split(":")[-1].strip().upper()
    return secret in answer.upper()


def run_test():
    print("=" * 60)
    print("  Needle in a Haystack Test — Qwen3.5 2B")
    print("=" * 60)
    print(f"  Model    : {MODEL_NAME}")
    print(f"  Needle   : {NEEDLE}")
    print(f"  Filler   : ~{TOTAL_FILLER_WORDS} words")
    print(f"  Positions: {[f'{int(p*100)}%' for p in POSITIONS]}")
    print("=" * 60)
    print()

    filler = make_filler(TOTAL_FILLER_WORDS)
    results = []

    for pos in POSITIONS:
        context = build_context(filler, NEEDLE, pos)
        word_count = len(context.split())
        label = f"{int(pos * 100)}%"

        print(f"[Testing position {label:>4}]  context ≈ {word_count} words ... ", end="", flush=True)

        answer  = ask_model(context, QUESTION)
        correct = check_answer(answer, NEEDLE)
        status  = "PASS ✓" if correct else "FAIL ✗"

        print(f"{status}")
        print(f"   Model answer : {answer[:120]}")
        print()

        results.append({"position": label, "correct": correct, "answer": answer})

    # ── Summary ──────────────────────────────────────────────────────────────
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r["correct"])
    total  = len(results)
    print(f"  Score: {passed}/{total}  ({int(passed/total*100)}%)")
    print()
    for r in results:
        icon = "✓" if r["correct"] else "✗"
        print(f"  [{icon}] Position {r['position']}")
    print("=" * 60)


if __name__ == "__main__":
    run_test()
