"""
单独测试 2B 模型的判断能力。
尝试不同的 prompt 表述方式，找到 2B 能理解的版本。
"""

import json
import re
import requests

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 300

CODE_LINES = [
    "def authenticate(user, pw):",
    "    def _hash(s):",
    "class Server:",
    "    def handle(self, req):",
    "def process_batch(items):",
    "        def inner():",
    "import os",
    "def log_event(msg):",
]
EXPECTED = ["authenticate", "process_batch", "log_event"]


def chat(system, user):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": 512,
    }
    resp = requests.post(API_URL, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def parse_json_list(text):
    for m in re.finditer(r'\[.*?\]', text, re.DOTALL):
        try:
            raw = json.loads(m.group())
            return [str(x).strip() for x in raw]
        except json.JSONDecodeError:
            continue
    names = re.findall(r'\b(authenticate|process_batch|log_event|_hash|handle|inner|Server)\b', text)
    return list(dict.fromkeys(names))


def make_code_block():
    return "\n".join(f"  {i+1}. {line}" for i, line in enumerate(CODE_LINES))


def test_variant(name, system, user):
    text = chat(system, user)
    found = parse_json_list(text)
    ok = set(found) == set(EXPECTED)
    extra = set(found) - set(EXPECTED)
    missing = set(EXPECTED) - set(found)
    print(f"\n  [{name}]")
    print(f"  Found:   {found}")
    print(f"  OK: {'✓' if ok else '✗'}", end="")
    if extra:
        print(f"  多余: {extra}", end="")
    if missing:
        print(f"  遗漏: {missing}", end="")
    print(f"\n  Raw: {text[:150]}...")
    return ok


def main():
    code = make_code_block()

    results = {}

    # V1: 当前版本（已知失败）
    results["v1_当前"] = test_variant(
        "v1: 当前版本",
        "你是精确的代码分析助手，只输出 JSON。",
        f"以下是 Python 代码的若干行（每行前标注了编号）：\n\n{code}\n\n"
        "规则：顶级函数 = 行首无任何空格且以 'def ' 开头的行。\n"
        '请只输出顶级函数名，用 JSON 列表格式：["name1", "name2", ...]'
    )

    # V2: 逐行判断——明确问每一行是/否
    results["v2_逐行"] = test_variant(
        "v2: 逐行是/否判断",
        "你是代码分析助手。对每一行，先判断是否符合条件，最后汇总。只输出 JSON。",
        f"以下是 Python 代码：\n\n{code}\n\n"
        "对每一行判断：这一行的【第一个字符】是不是字母 'd'？\n"
        "- 第 1 行 'def authenticate...' → 第一个字符是 'd' → 是\n"
        "- 第 2 行 '    def _hash...' → 第一个字符是空格 ' ' → 否\n\n"
        "只输出第一个字符是 'd' 且紧接着是 'ef ' 的行中，'def ' 后面 '(' 前面的名字。\n"
        '格式：["name1", "name2", ...]'
    )

    # V3: 超简——只看第一个字符
    results["v3_首字符"] = test_variant(
        "v3: 只看第一个字符是否为 d",
        "你是代码分析助手。只输出 JSON 列表。",
        f"以下是 Python 代码：\n\n{code}\n\n"
        "哪些行的第一个字符是字母 'd'？\n"
        "对于这些行，提取 'def ' 后面到 '(' 之间的单词。\n"
        '输出 JSON 列表：["word1", "word2", ...]'
    )

    # V4: 排除法——先列出所有 def 行，再去掉有空格的
    results["v4_排除法"] = test_variant(
        "v4: 排除法",
        "你是代码分析助手。一步一步思考，最后输出 JSON。",
        f"以下是 Python 代码：\n\n{code}\n\n"
        "第一步：找出所有包含 'def ' 的行。\n"
        "第二步：在这些行中，去掉【'def ' 前面有空格】的行。\n"
        "第三步：剩下的就是顶级函数。提取函数名（'def ' 和 '(' 之间的词）。\n"
        '输出 JSON 列表：["name1", ...]'
    )

    # V5: 给出完整示例答案推理过程
    results["v5_示例推理"] = test_variant(
        "v5: 示例推理",
        "你是代码分析助手。模仿示例的推理方式，只输出最终 JSON。",
        "任务：找出顶级函数（行首直接是 def 的行）。\n\n"
        "示例：\n"
        "  代码：\n"
        "    1. def foo():\n"
        "    2.     def bar():\n"
        "    3. def baz():\n"
        "  分析：第1行首字符是'd' → 顶级。第2行首字符是' ' → 不是。第3行首字符是'd' → 顶级。\n"
        '  答案：["foo", "baz"]\n\n'
        f"现在分析这段代码：\n\n{code}\n\n"
        '只输出最终答案，格式：["name1", ...]'
    )

    # V6: 用 tool_call 模式——模拟工具场景下的单行判断
    results["v6_单行工具"] = test_variant(
        "v6: 单行判断（模拟工具场景）",
        "你是文本扫描助手。只输出 JSON。",
        "我会给你若干行代码。对每行，判断该行是否以 'def ' 开头（行的前4个字符是 'd','e','f',' '）。\n"
        "如果是，提取函数名。如果不是，写 null。\n\n"
        + "\n".join(f"第{i+1}行：`{line}`" for i, line in enumerate(CODE_LINES))
        + "\n\n"
        '只输出以 def 开头的行的函数名列表：["name1", ...]（去掉 null）'
    )

    print(f"\n{'='*50}")
    print("总结")
    print(f"{'='*50}")
    for name, ok in results.items():
        print(f"  {name:20s} {'✓' if ok else '✗'}")

    passed = sum(1 for v in results.values() if v)
    print(f"\n通过率: {passed}/{len(results)}")


if __name__ == "__main__":
    main()
