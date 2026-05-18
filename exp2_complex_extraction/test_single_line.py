"""
测试 2B 对单行代码的判断能力。
每次只给一行，问是否为顶级函数。
"""

import requests

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"

LINES = [
    ("def authenticate(user, pw):", True),
    ("    def _hash(s):", False),
    ("class Server:", False),
    ("    def handle(self, req):", False),
    ("def process_batch(items):", True),
    ("        def inner():", False),
    ("import os", False),
    ("def log_event(msg):", True),
    ("    return result", False),
    ("def     spaced(x):", True),  # 行首是 def 但 def 后面空格多——仍是顶级
]


def chat(system, user):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": 64,
    }
    resp = requests.post(API_URL, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def main():
    system = "你是代码分析助手。只回答 YES 或 NO，不要解释。"

    correct = 0
    total = len(LINES)

    print("逐行判断测试：行首是否以 'def ' 开头（无前导空格）？\n")

    for line, expected in LINES:
        user = (
            f"这行代码：`{line}`\n"
            "问题：这行的【第一个字符】是不是 'd'，且前4个字符是 'def '？\n"
            "只回答 YES 或 NO。"
        )
        answer = chat(system, user)
        got_yes = "yes" in answer.lower()
        ok = got_yes == expected
        correct += ok
        mark = "✓" if ok else "✗"
        print(f"  {mark} `{line:40s}` expect={expected}  got={answer[:20]}")

    print(f"\n单行判断正确率: {correct}/{total} ({correct/total*100:.0f}%)")

    # 测试2: 3行一批（模拟 read_next 场景）
    print("\n" + "="*50)
    print("3行一批判断测试\n")

    batches = [
        LINES[0:3],
        LINES[3:6],
        LINES[6:9],
    ]

    correct2 = 0
    total2 = 0

    for batch in batches:
        lines_text = "\n".join(f"  行{i+1}: `{line}`" for i, (line, _) in enumerate(batch))
        user = (
            f"以下是3行代码：\n{lines_text}\n\n"
            "哪些行的第一个字符是 'd' 且前4个字符是 'def '？\n"
            "只输出这些行的行号（如 '行1' '行3'），如果没有就说 '无'。"
        )
        answer = chat(system, user)
        expected_nums = [i+1 for i, (_, is_top) in enumerate(batch) if is_top]
        print(f"  批次: {[l for l, _ in batch]}")
        print(f"  期望: 行{expected_nums}  回答: {answer[:60]}")
        total2 += 1

    # 测试3: 模拟 read_next 返回格式
    print("\n" + "="*50)
    print("模拟 read_next JSON 返回格式\n")

    fake_batch = {
        "lines": [
            {"line": 15, "content": "    def handle(self, req):"},
            {"line": 16, "content": "        pass"},
            {"line": 17, "content": ""},
            {"line": 18, "content": "def process_batch(items):"},
            {"line": 19, "content": '    """Process a batch."""'},
        ],
        "advance_target": 19,
    }

    import json
    user = (
        f"read_next 返回结果：\n{json.dumps(fake_batch, ensure_ascii=False, indent=2)}\n\n"
        "哪些行的 content 字段以 'def ' 开头（content 的第一个字符是 'd'）？\n"
        "只输出行号和函数名。如果没有就说 '无'。"
    )
    answer = chat("你是文本扫描助手。简短回答。", user)
    print(f"  期望: 第18行 process_batch")
    print(f"  回答: {answer[:100]}")


if __name__ == "__main__":
    main()
