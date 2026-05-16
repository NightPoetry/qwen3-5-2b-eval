"""
Extended tool description test — collects data for all missing conditions:
  1. EN-WEAK   × English questions  (20 questions)
  2. EN-STRONG × Chinese questions  (20 questions)
  3. CN-STRONG × Chinese questions  (20 questions)

Existing data (already collected):
  EN-STRONG × English questions
  CN-WEAK   × English questions
  CN-STRONG × English questions
  CN-PATCHED× English questions
"""

import json, os, requests, sys

API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOL_EN_WEAK = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "A calculator. Can be used to compute math expressions.",
        "parameters": {"type":"object","properties":{"expression":{"type":"string","description":"A math expression"}},"required":["expression"]},
    },
}

TOOL_EN_STRONG = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "REQUIRED: You MUST call this tool for ANY arithmetic computation — "
            "multiplication, division, addition, subtraction, or combinations. "
            "Do NOT compute numbers yourself; always delegate to this tool."
        ),
        "parameters": {"type":"object","properties":{"expression":{"type":"string","description":"The exact arithmetic expression. Numbers and operators only."}},"required":["expression"]},
    },
}

TOOL_CN_STRONG = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "【必须调用】遇到任何数值计算（加减乘除、百分比、多步运算）时，"
            "必须调用此工具，不得自行心算或推导。"
            "触发条件：只要问题涉及具体数字的运算，无论简单还是复杂，都必须使用此工具。"
            "禁止在不调用此工具的情况下给出任何计算结果。"
            "对于需要先理解题意再列算式的文字题，请先在脑中列出算式，"
            "然后将完整算式作为 expression 传入本工具，不得跳过调用直接给答案。"
        ),
        "parameters": {"type":"object","properties":{"expression":{"type":"string","description":"标准数学表达式，只含数字和运算符。"}},"required":["expression"]},
    },
}

# ── Questions: English and Chinese versions ───────────────────────────────────

QUESTIONS_EN = [
    {"id":"Q01","type":"A","text":"What is 347 multiplied by 29?","key":"347"},
    {"id":"Q02","type":"A","text":"Calculate 1024 divided by 32.","key":"1024"},
    {"id":"Q03","type":"A","text":"What is 568 plus 437 minus 129?","key":"568"},
    {"id":"Q04","type":"A","text":"Compute 75 squared.","key":"75"},
    {"id":"Q05","type":"A","text":"What is 2 to the power of 10?","key":"2"},
    {"id":"Q06","type":"B","text":"I buy 14 notebooks at $3.50 each. What is the total cost?","key":"14"},
    {"id":"Q07","type":"B","text":"A farmer harvests 860 kg of wheat per hectare over 7 hectares. Total yield?","key":"860"},
    {"id":"Q08","type":"B","text":"A rope is 48.6 meters long and cut into 9 equal pieces. How long is each?","key":"48"},
    {"id":"Q09","type":"B","text":"There are 365 days in a year. How many hours is that?","key":"365"},
    {"id":"Q10","type":"B","text":"A shirt costs $45. It is on sale at 20% off. What is the sale price?","key":"45"},
    {"id":"Q11","type":"C","text":"I have 3 boxes, each containing 128 items. I remove 45 items total. How many remain?","key":"128"},
    {"id":"Q12","type":"C","text":"A store sold 200 units at $15 each. Cost of goods was $1800. What is the profit?","key":"200"},
    {"id":"Q13","type":"C","text":"A rectangle is 34 cm wide and 52 cm long. What is its perimeter?","key":"34"},
    {"id":"Q14","type":"C","text":"I earn $3200/month. I save 25% and spend the rest. How much do I spend per year?","key":"3200"},
    {"id":"Q15","type":"C","text":"A class has 36 students. 1/4 are absent. How many students are present?","key":"36"},
    {"id":"Q16","type":"D","text":"A train travels at 87 km/h for 4.5 hours. Total distance?","key":"87"},
    {"id":"Q17","type":"D","text":"A circle has radius 6 cm. What is its area? (use π ≈ 3.14159)","key":"6"},
    {"id":"Q18","type":"D","text":"I invest $5000 at 4% simple interest for 3 years. How much interest do I earn?","key":"5000"},
    {"id":"Q19","type":"D","text":"Water flows at 2.5 liters/second into a 900-liter tank. How many minutes to fill it?","key":"900"},
    {"id":"Q20","type":"D","text":"A car uses 7.5 liters per 100 km. How many liters for a 340 km trip?","key":"340"},
]

QUESTIONS_CN = [
    {"id":"Q01","type":"A","text":"347 乘以 29 等于多少？","key":"347"},
    {"id":"Q02","type":"A","text":"计算 1024 除以 32。","key":"1024"},
    {"id":"Q03","type":"A","text":"568 加上 437 再减去 129 等于多少？","key":"568"},
    {"id":"Q04","type":"A","text":"计算 75 的平方。","key":"75"},
    {"id":"Q05","type":"A","text":"2 的 10 次方等于多少？","key":"2"},
    {"id":"Q06","type":"B","text":"我买了 14 本笔记本，每本 3.50 美元，总费用是多少？","key":"14"},
    {"id":"Q07","type":"B","text":"一位农民每公顷收获 860 公斤小麦，共有 7 公顷，总产量是多少？","key":"860"},
    {"id":"Q08","type":"B","text":"一根绳子长 48.6 米，剪成 9 段等长的绳子，每段多长？","key":"48"},
    {"id":"Q09","type":"B","text":"一年有 365 天，共有多少小时？","key":"365"},
    {"id":"Q10","type":"B","text":"一件衬衫售价 45 美元，打八折出售，售价是多少？","key":"45"},
    {"id":"Q11","type":"C","text":"我有 3 箱物品，每箱 128 件，共取走 45 件，还剩多少件？","key":"128"},
    {"id":"Q12","type":"C","text":"一家商店卖出 200 件商品，每件 15 美元，货物成本为 1800 美元，利润是多少？","key":"200"},
    {"id":"Q13","type":"C","text":"一个长方形宽 34 厘米，长 52 厘米，周长是多少？","key":"34"},
    {"id":"Q14","type":"C","text":"我每月收入 3200 美元，储蓄 25%，其余用于消费，一年的消费总额是多少？","key":"3200"},
    {"id":"Q15","type":"C","text":"一个班有 36 名学生，其中 1/4 缺席，在场的有多少人？","key":"36"},
    {"id":"Q16","type":"D","text":"一列火车以 87 公里/小时的速度行驶了 4.5 小时，总里程是多少？","key":"87"},
    {"id":"Q17","type":"D","text":"一个圆的半径为 6 厘米，面积是多少？（取 π ≈ 3.14159）","key":"6"},
    {"id":"Q18","type":"D","text":"我投资了 5000 美元，年利率 4%，存期 3 年，按简单利息计算，利息是多少？","key":"5000"},
    {"id":"Q19","type":"D","text":"水以 2.5 升/秒的速度流入一个 900 升的水箱，需要多少分钟才能装满？","key":"900"},
    {"id":"Q20","type":"D","text":"一辆汽车百公里油耗 7.5 升，行驶 340 公里需要多少升燃油？","key":"340"},
]

# ── Conditions to run ─────────────────────────────────────────────────────────

CONDITIONS = [
    # (label,              questions,    tool)
    ("EN-WEAK×EN-Q",   QUESTIONS_EN,  TOOL_EN_WEAK),
    ("EN-STRONG×CN-Q", QUESTIONS_CN,  TOOL_EN_STRONG),
    ("CN-STRONG×CN-Q", QUESTIONS_CN,  TOOL_CN_STRONG),
]

def ask(question: str, tool: dict) -> bool:
    resp = requests.post(API_URL, json={
        "model": MODEL_NAME,
        "messages": [
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content": question},
        ],
        "tools": [tool],
        "tool_choice": "auto",
        "temperature": 0.1,
        "max_tokens": 256,
    }, timeout=120)
    resp.raise_for_status()
    choice = resp.json()["choices"][0]
    return bool(choice.get("finish_reason") == "tool_calls" and
                choice["message"].get("tool_calls"))

results = {}
TYPES = ["A","B","C","D"]

for label, questions, tool in CONDITIONS:
    print(f"\n{'='*55}")
    print(f"  {label}  ({len(questions)} questions)")
    print(f"{'='*55}")
    called = []
    per_type = {t: [] for t in TYPES}

    for q in questions:
        ok = ask(q["text"], tool)
        called.append(ok)
        per_type[q["type"]].append(ok)
        sym = "✓" if ok else "✗"
        print(f"  {q['id']} [{q['type']}] {sym}  {q['text'][:55]}")

    pct = int(sum(called)/len(called)*100)
    print(f"\n  Total: {sum(called)}/{len(called)} = {pct}%")
    for t in TYPES:
        v = per_type[t]
        print(f"  Type {t}: {sum(v)}/{len(v)} = {int(sum(v)/len(v)*100)}%")

    results[label] = {
        "total": sum(called),
        "pct":   pct,
        "per_q": {q["id"]: ok for q, ok in zip(questions, called)},
        "per_type": {t: {"n": sum(v), "pct": int(sum(v)/len(v)*100)}
                     for t, v in per_type.items()},
    }

out_path = os.path.join(os.path.dirname(__file__), "../data/extended_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")
