"""
认知递归展开测试。

check_line 工具内部将"是否顶级函数"拆解为微型子问题，
每个子问题用独立的 mini-conversation 问模型（上下文隔离）。
模型仍然在做所有判断，工具只负责拆解和编排。
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

import requests
from tools import ToolState, execute_tool, make_tool_schemas
from data_generator import generate_python_file
from evaluate import evaluate

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"
TIMEOUT = 120
MAX_ROUNDS = 80


# ── 微型对话：每次只问一个极简问题 ──────────────────────────────────────

def mini_chat(question: str) -> str:
    """隔离的微型对话，只问一个简单问题。"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "只回答问题，不要解释。尽量用一个词回答。"},
            {"role": "user", "content": question},
        ],
        "temperature": 0.0,
        "max_tokens": 32,
    }
    resp = requests.post(API_URL, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── 认知展开器：将"是否顶级函数"拆解为微型子问题 ────────────────────────

def expand_check_top_level(line_content: str) -> dict:
    """
    将"这行是不是顶级函数？"展开为 2-3 个微型子问题。
    每个子问题在隔离上下文中由模型回答。
    """
    # 子步骤 1：第一个字符是什么？
    q1 = f"这行代码的第一个字符是什么？只回答那个字符。\n行：`{line_content}`"
    a1 = mini_chat(q1)

    # 子步骤 2：是否为空格？
    is_space = a1.strip() in ("空格", " ", "' '", "space", "空白", "（空格）",
                               "' '", '" "', "a space", "whitespace")
    # 也直接问模型确认
    q2 = f"字符 `{a1}` 是不是空格或空白字符？只回答 YES 或 NO。"
    a2 = mini_chat(q2)
    has_space = "yes" in a2.lower() or "是" in a2

    if has_space:
        return {
            "is_target": False,
            "reason": f"行首字符是 '{a1}'（空白），不是顶级定义",
            "子步骤": [
                {"问": q1, "答": a1},
                {"问": q2, "答": a2, "结论": "行首有空格 → 不是顶级"},
            ],
        }

    # 子步骤 3：是否以 'def ' 开头？
    q3 = f"这行代码是否以 'def ' 这四个字符开头？只回答 YES 或 NO。\n行：`{line_content}`"
    a3 = mini_chat(q3)
    is_def = "yes" in a3.lower() or "是" in a3

    if not is_def:
        return {
            "is_target": False,
            "reason": f"不是 def 定义",
            "子步骤": [
                {"问": q1, "答": a1},
                {"问": q2, "答": a2},
                {"问": q3, "答": a3, "结论": "不以 def 开头 → 不是函数"},
            ],
        }

    # 子步骤 4：提取函数名
    q4 = f"'{line_content}' 是函数定义。函数名紧跟 'def ' 出现，在 '(' 之前。函数名是？"
    a4 = mini_chat(q4)
    name = a4.strip().strip("'\"` ").split("(")[0].split(" ")[0]

    return {
        "is_target": True,
        "item": name,
        "category": "function",
        "reason": f"行首无空格 + 以 def 开头 → 顶级函数 '{name}'",
        "子步骤": [
            {"问": q1, "答": a1},
            {"问": q2, "答": a2},
            {"问": q3, "答": a3},
            {"问": q4, "答": a4, "结论": f"顶级函数: {name}"},
        ],
    }


# ── 先单独测试展开器的准确率 ──────────────────────────────────────────

def test_expander_accuracy():
    """对标准测试行逐个展开，验证准确率。"""
    test_cases = [
        ("def authenticate(user, pw):", True, "authenticate"),
        ("    def _hash(s):", False, None),
        ("class Server:", False, None),
        ("    def handle(self, req):", False, None),
        ("def process_batch(items):", True, "process_batch"),
        ("        def inner():", False, None),
        ("import os", False, None),
        ("def log_event(msg):", True, "log_event"),
    ]

    print("=" * 60)
    print("展开器准确率测试")
    print("每行代码通过 2-4 个微型子问题判断")
    print("=" * 60)

    correct = 0
    for line, expected_target, expected_name in test_cases:
        result = expand_check_top_level(line)
        got_target = result["is_target"]
        got_name = result.get("item")

        ok_target = got_target == expected_target
        ok_name = (not expected_target) or (got_name == expected_name)
        ok = ok_target and ok_name
        correct += ok

        mark = "✓" if ok else "✗"
        print(f"\n  {mark} `{line}`")
        print(f"    期望: target={expected_target} name={expected_name}")
        print(f"    得到: target={got_target} name={got_name}")
        for step in result["子步骤"]:
            print(f"    → 问: {step['问'][:50]}...")
            print(f"      答: {step['答']}")

    print(f"\n展开器准确率: {correct}/{len(test_cases)}")
    return correct == len(test_cases)


# ── 集成到主循环的完整测试 ──────────────────────────────────────────────

def chat(messages, tools=None, retries=3):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 1024,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    for attempt in range(retries):
        try:
            resp = requests.post(API_URL, json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json()["choices"][0]
        except requests.HTTPError as e:
            if attempt < retries - 1 and "400" in str(e):
                import time
                time.sleep(2)
                continue
            raise


def run_full_test(seed=42):
    """
    完整流程：模型只负责循环导航（read→advance）。
    Runner 在 read_next 返回后，自动对每行执行认知展开检查，
    将发现注入到 tool result 中告知模型。
    模型看到 "发现目标" 后只需调用 record()。
    """
    text, gt = generate_python_file(
        n_top_level=5, n_classes=2, n_methods_per_class=3, seed=seed)

    state = ToolState(text)
    tools = make_tool_schemas(include_stack=False, include_record=True)

    system = """\
你是文本扫描器。用工具逐段处理文档。

每轮：
1. read_next() 读取一批内容
2. 如果返回结果中有"发现目标"，按指示调用 record()
3. advance_past(to_line=<advance_target>)
4. done=true → get_records()；done=false → 回到第1步

严禁输出文字，只调用工具。\
"""
    user = "开始扫描。调用 read_next()。"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    rounds = 0
    tool_seq = []
    expand_calls = 0
    expand_hits = 0

    print(f"\n{'='*60}")
    print(f"完整流程测试 seed={seed}")
    print(f"GT: {gt}")
    print(f"{'='*60}")

    while rounds < MAX_ROUNDS:
        rounds += 1
        try:
            choice = chat(messages, tools=tools)
        except Exception as e:
            print(f"  API error at round {rounds}: {e}")
            break

        finish = choice["finish_reason"]
        msg = choice["message"]

        if finish == "tool_calls":
            tcs = msg.get("tool_calls", [])
            messages.append({
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": tcs,
            })
            for tc in tcs:
                fn = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                result_str = execute_tool(state, fn, args)

                # Runner 层拦截：read_next 返回后，对每行执行认知展开
                if fn == "read_next":
                    result_dict = json.loads(result_str)
                    if result_dict.get("content_type") == "lines":
                        findings = []
                        for line_entry in result_dict.get("lines", []):
                            content = line_entry.get("content", "")
                            if "def " in content:
                                expand_calls += 1
                                check = expand_check_top_level(content)
                                if check["is_target"]:
                                    expand_hits += 1
                                    findings.append({
                                        "行": line_entry["line"],
                                        "函数名": check["item"],
                                        "类别": check["category"],
                                    })
                                    print(f"  R{rounds}: 展开检查 L{line_entry['line']} "
                                          f"'{content[:40]}' → ✓ {check['item']}")
                        if findings:
                            result_dict["发现目标"] = findings
                            result_dict["操作指示"] = (
                                "发现以下目标，必须对每个调用 "
                                "record(item=函数名, category='function')："
                                + "、".join(f["函数名"] for f in findings)
                            )
                        result_str = json.dumps(result_dict, ensure_ascii=False)

                tool_seq.append(fn)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_str,
                })
            called = [tc["function"]["name"] for tc in tcs]
            if "get_records" in called:
                break
            if state.cursor >= len(text):
                break
        elif finish in ("stop", "length"):
            tool_seq.append("STOP")
            if state.cursor < len(text):
                messages.append({
                    "role": "user",
                    "content": "继续。read_next → record(如有目标) → advance_past。",
                })
            else:
                break
        else:
            break

    found = [r["item"] for r in state.records]
    coverage = round(state.cursor / max(len(text), 1) * 100, 1)
    metrics = evaluate("python_functions", gt, found)
    counts = Counter(tool_seq)

    print(f"\n结果:")
    print(f"  F1={metrics['f1']:.2f}  R={metrics['recall']:.2f}  P={metrics['precision']:.2f}")
    print(f"  Coverage: {coverage}%  Rounds: {rounds}")
    print(f"  Tools: {dict(counts)}")
    print(f"  展开调用: {expand_calls} 次, 命中: {expand_hits} 次")
    print(f"  Found: {found}")
    return metrics["f1"]


def main():
    # 第一步：单独测试展开器准确率
    expander_ok = test_expander_accuracy()

    if not expander_ok:
        print("\n展开器准确率不到 100%，先修复再跑完整测试。")
        return

    # 第二步：跑一个完整的单例测试
    f1 = run_full_test(seed=42)
    print(f"\n最终 F1: {f1:.2f}")


if __name__ == "__main__":
    main()
