"""
Web chat interface for v2 knowledge network.
Lets you chat with the 2B model through the node graph engine.
"""

import sys
import json
import time
import uuid
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_from_directory, Response
from engine import Engine

app = Flask(__name__)

NODES_DIR = Path(__file__).parent.parent / "nodes"
CHAT_LOG_DIR = Path(__file__).parent.parent / "chat_logs"
CHAT_LOG_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS = {}


def get_engine():
    engine = Engine()
    engine.load_from_dir(NODES_DIR)
    return engine


def build_result_text(result: dict, trace: list[dict]) -> str:
    if result.get("_chat_response"):
        return result["_chat_response"]

    parts = []

    if result.get("_creative_output"):
        parts.append(result["_creative_output"])

    if result.get("_reasoning"):
        r = result["_reasoning"]
        parts.append(f"重述：{r.get('restated', '')}")
        if r.get("classification"):
            parts.append(f"分类：{r['classification']}")

    if result.get("_word_method"):
        parts.append(f"词义原则：{result['_word_method']['principle']}")

    if result.get("_disambiguated"):
        for t, m in result["_disambiguated"].items():
            parts.append(f"{t} → {m}")

    if result.get("_fix_steps"):
        parts.append(f"修复方案（{len(result['_fix_steps'])}步）：")
        for s in result["_fix_steps"][:5]:
            parts.append(f"  {s['id']}: {s['name']}")
    if result.get("_debug"):
        parts.append(f"症状：{result['_debug'].get('symptom', '')}")

    contract = result.get("contract", {})
    patterns = contract.get("interaction_patterns", [])
    if patterns:
        parts.append(f"交互模式（{len(patterns)}条）：")
        for p in patterns[:5]:
            parts.append(f"  - {p}")

    if result.get("_domain_rules"):
        parts.append(f"领域规则（{len(result['_domain_rules'])}条）：")
        for r in result["_domain_rules"][:5]:
            parts.append(f"  - {r}")

    if result.get("_changes"):
        parts.append(f"变更：{result['_changes']}")

    if result.get("_warnings"):
        for w in result["_warnings"]:
            parts.append(f"⚠ {w}")

    if result.get("output_path"):
        out = Path(result["output_path"])
        if out.exists():
            files = [f for f in out.iterdir() if f.is_file()]
            if files:
                parts.append(f"输出目录：{out}")
                for f in sorted(files):
                    parts.append(f"  {f.name}: {f.stat().st_size}b")

    if result.get("raw_html"):
        parts.append("[已生成 HTML 代码]")
    if result.get("raw_css"):
        parts.append("[已生成 CSS 代码]")
    if result.get("raw_js"):
        parts.append("[已生成 JS 代码]")

    if not parts and len(trace) <= 1:
        parts.append("没有节点被触发。试试更具体的指令，比如：\n"
                      "  · 写一首关于月亮的诗\n"
                      "  · 分析为什么天空是蓝色的\n"
                      "  · 创建一个待办事项应用\n"
                      "  · 修复这个 bug...")

    return "\n".join(parts) if parts else "（节点执行完成，无文本输出）"


@app.route("/")
def index():
    return send_from_directory(Path(__file__).parent, "index.html")


@app.route("/graph")
def graph():
    return send_from_directory(Path(__file__).parent, "graph.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").strip()
    session_id = data.get("session_id", str(uuid.uuid4()))
    force_new = data.get("force_new", False)

    if not message:
        return jsonify({"error": "空消息"}), 400

    session = {} if force_new else SESSIONS.get(session_id, {})

    ctx = {
        "task": message,
        "output_dir": str(Path(__file__).parent.parent / "output"),
        "_turns": session.get("_turns", []),
    }
    ctx["_turns"].append(message)

    # 聊天记录不进 context — 回忆节点按需检索
    ctx["_chat_log_path"] = str(CHAT_LOG_DIR / f"{session_id}.json")
    if session.get("_cursor"):
        ctx["_cursor"] = session["_cursor"]
    if session.get("_active_domain"):
        ctx["_active_domain"] = session["_active_domain"]
    for key in ("html", "css", "js", "contract", "blog", "theme", "interactions",
                "_reasoning", "_design_guidance", "_role_response",
                "_disambiguated", "_calibration", "_risk_levels"):
        if session.get(key):
            ctx[key] = session[key]
    if ctx.get("html"):
        ctx["existing_html"] = ctx["html"]

    engine = get_engine()
    t0 = time.time()

    try:
        result = engine.run("000", ctx)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
        }), 500

    elapsed = time.time() - t0

    trace = []
    for t in engine.trace:
        trace.append({
            "node": t["node"],
            "name": t["name"],
            "depth": t["depth"],
            "reason": t["reason"],
            "error": t.get("error"),
        })

    response_text = build_result_text(result, trace)
    cursor = result.get("_cursor", [])

    # 聊天记录存文件（供回忆节点检索），不进 context
    chat_log_path = ctx["_chat_log_path"]
    chat_log = []
    if Path(chat_log_path).exists():
        try:
            chat_log = json.loads(Path(chat_log_path).read_text())
        except (json.JSONDecodeError, IOError):
            chat_log = []
    # 本次对话追加
    user_msg = message
    assistant_msg = response_text
    chat_log.append({"role": "user", "content": user_msg})
    if assistant_msg:
        chat_log.append({"role": "assistant", "content": assistant_msg})
    # 保留最近 100 条
    Path(chat_log_path).write_text(json.dumps(chat_log[-100:], ensure_ascii=False))

    save = {
        "_cursor": cursor,
        "_turns": result.get("_turns", []),
        "_active_domain": result.get("_active_domain"),
    }
    for key in ("html", "css", "js", "contract", "blog", "theme", "interactions",
                "_reasoning", "_design_guidance", "_role_response",
                "_disambiguated", "_calibration", "_risk_levels"):
        if result.get(key):
            try:
                json.dumps(result[key])
                save[key] = result[key]
            except (TypeError, ValueError):
                pass
    SESSIONS[session_id] = save

    return jsonify({
        "session_id": session_id,
        "response": response_text,
        "trace": trace,
        "cursor": cursor,
        "turn": len(save["_turns"]),
        "elapsed": round(elapsed, 2),
        "node_count": len(engine.nodes),
    })


@app.route("/api/nodes", methods=["GET"])
def list_nodes():
    engine = get_engine()
    nodes = []
    for nid, n in sorted(engine.nodes.items()):
        nodes.append({
            "id": n.id,
            "name": n.name,
            "trigger": n.trigger,
            "refs": n.refs,
            "category": n.metadata.get("category", ""),
        })
    return jsonify({"nodes": nodes, "count": len(nodes)})


@app.route("/api/reset", methods=["POST"])
def reset_session():
    data = request.json or {}
    session_id = data.get("session_id", "")
    if session_id in SESSIONS:
        del SESSIONS[session_id]
    return jsonify({"ok": True})


if __name__ == "__main__":
    print(f"Loaded {len(get_engine().nodes)} nodes from {NODES_DIR}")
    print("http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
