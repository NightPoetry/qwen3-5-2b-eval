"""
统一入口 — 用户只说一句话，网络自己决定。
上下文 = 图中的位置。停在哪就从哪继续。

用法：
  python do.py "创建一个待办事项应用"   ← 从000入口进，停在代码区域
  python do.py "改个颜色"              ← 从代码区域的邻接续入
  python do.py "写首诗"                ← 邻接不匹配，回退到000，路由到创作区域
  python do.py --new "全新任务"         ← 强制从000开始
  python do.py --history               ← 查看轨迹
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import Engine

SESSION_FILE = Path(__file__).parent / ".session.json"


def load_session() -> dict:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_session(ctx: dict):
    """只存光标 + 对话历史 + 累积的产出物。位置就是上下文。"""
    session = {
        "_cursor": ctx.get("_cursor", []),
        "_turns": ctx.get("_turns", []),
    }
    # 保留累积的产出物（代码/内容/契约）——这些是"你在图中走过留下的痕迹"
    for key in ("html", "css", "js", "contract", "blog", "theme", "interactions"):
        if ctx.get(key):
            try:
                json.dumps(ctx[key])
                session[key] = ctx[key]
            except (TypeError, ValueError):
                pass
    SESSION_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2))


def main():
    args = sys.argv[1:]

    if "--history" in args:
        s = load_session()
        turns = s.get("_turns", [])
        cursor = s.get("_cursor", [])
        print(f"=== 会话 ({len(turns)}轮) ===")
        for i, t in enumerate(turns):
            print(f"  [{i+1}] {t}")
        if cursor:
            print(f"\n光标停在: {cursor}")
        return

    force_new = "--new" in args
    args = [a for a in args if not a.startswith("--")]
    task = " ".join(args) if args else input("说点什么: ")

    # 加载session——核心是光标位置
    session = {} if force_new else load_session()

    ctx = {
        "task": task,
        "output_dir": str(Path(__file__).parent / "output"),
        "_turns": session.get("_turns", []),
    }
    ctx["_turns"].append(task)

    # 恢复光标和累积产出
    if session.get("_cursor"):
        ctx["_cursor"] = session["_cursor"]
    for key in ("html", "css", "js", "contract", "blog", "theme", "interactions"):
        if session.get(key):
            ctx[key] = session[key]

    # 如果已有产出，标记给修改类节点用
    if ctx.get("html"):
        ctx["existing_html"] = ctx["html"]

    engine = Engine()
    engine.load_from_dir(Path(__file__).parent / "nodes")

    turn_num = len(ctx["_turns"])
    cursor = ctx.get("_cursor", [])
    if cursor and turn_num > 1:
        print(f"[续·第{turn_num}轮] {task}")
        print(f"光标在: {cursor}")
    else:
        print(f"[新·第{turn_num}轮] {task}")
    print(f"节点: {len(engine.nodes)} 个\n")

    result = engine.run("000", ctx)

    # 显示结果
    print("\n--- 轨迹 ---")
    engine.print_trace()

    new_cursor = result.get("_cursor", [])
    if new_cursor:
        print(f"\n停机位置: {new_cursor}")

    # 输出
    print("\n--- 结果 ---")

    if result.get("_creative_output"):
        print(f"\n{result['_creative_output']}")

    if result.get("_reasoning"):
        r = result["_reasoning"]
        print(f"\n[推理] {r.get('restated', '')}")
        if r.get("classification"):
            print(f"  → {r['classification']}")

    if result.get("_word_method"):
        print(f"\n[词义] {result['_word_method']['principle']}")

    if result.get("_disambiguated"):
        for t, m in result["_disambiguated"].items():
            print(f"  {t} → {m}")

    if result.get("_fix_steps"):
        print(f"\n[Fix] {len(result['_fix_steps'])}步展开")
        for s in result["_fix_steps"][:3]:
            print(f"  {s['id']}: {s['name']}")
    if result.get("_debug"):
        print(f"  症状: {result['_debug'].get('symptom', '')}")

    contract = result.get("contract", {})
    patterns = contract.get("interaction_patterns", [])
    if patterns:
        print(f"\n[交互] {len(patterns)}条模式")
        for p in patterns[:3]:
            print(f"  - {p}")

    if result.get("output_path"):
        out = Path(result["output_path"])
        if out.exists():
            files = [f for f in out.iterdir() if f.is_file()]
            if files:
                print(f"\n[输出] {out}")
                for f in sorted(files):
                    print(f"  {f.name}: {f.stat().st_size}b")

    if result.get("_domain_rules"):
        print(f"\n[领域] {len(result['_domain_rules'])}条")
        for r in result["_domain_rules"][:3]:
            print(f"  - {r}")

    if result.get("_changes"):
        print(f"\n[变更] {result['_changes']}")

    if result.get("_warnings"):
        for w in result["_warnings"]:
            print(f"  ! {w}")

    if len(engine.trace) <= 1:
        print("\n  (无节点被触发)")

    # 保存——光标就是上下文
    save_session(result)
    print(f"\n[第{turn_num}轮结束]")


if __name__ == "__main__":
    main()
