"""知识节点：AI自反馈回环 — 可自视/可远操/可感知/可全知/可封印。

五条原则让AI构建的应用能自己测试每个交互：

1. 可自视：应用能捕获自身视觉输出（窗口缓冲区导出，不触发权限弹窗）
2. 可远操：所有用户交互可程序等价触发（直接调用业务函数，不模拟鼠标事件）
3. 可感知：每个操作结果可查询为结构化数据（不截图看文字）
4. 可全知：一条命令获取完整应用状态快照（不翻DevTools/日志）
5. 可封印：以上能力正式发布时完全关闭（编译期排除+运行期开关+网络层隔离）

判断标准：AI改一行代码后能否10秒内自己验证改对了？
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

FEEDBACK_SYSTEM = """You are a self-testing capability advisor. Apply the 5 self-feedback principles:

1. SELF-VISUAL: App captures its own visual output from window buffer. No screen recording permission needed. Implementation: NSView.cacheDisplay (macOS/Tauri), html2canvas (Web), HTTP GET /capture endpoint.

2. REMOTE-OPERABLE: All user interactions triggerable programmatically. DO NOT simulate DOM events (unreliable in WebView overlay regions). Instead: maintain ID->function mapping table, call business functions directly. HTTP POST /click body: buttonId -> evaluate JS function.

3. PERCEIVABLE: Every operation result queryable as structured data. HTTP GET /state returns: connection status, message count, sending flag, current config. In-memory ring buffer for structured logs (ts, level, tag, message). Operation completion: poll sending status variable.

4. OMNISCIENT: One call returns complete application state snapshot. Endpoints: /ping (health+metrics), /state (app snapshot), /debug/logs?tag=X&level=Y&limit=N. All bound to 127.0.0.1 only.

5. SEALABLE: All debug capabilities fully disabled in production. Three layers: compile-time exclusion (cfg debug_assertions), runtime env var gate, network 127.0.0.1 hard-bind.

TEST: Can AI verify a code change in 10 seconds without human compilation/clicking/describing?
If needs human -> not qualified. If AI compiles/operates/reads/sees -> qualified.

Given the application, assess which self-feedback capabilities exist and which are missing."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    review = ask(
        FEEDBACK_SYSTEM,
        f"Application/testing scenario: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_self_feedback_review"] = review
    return ctx

node = Node(id="E30", name="自反馈回环",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["测试", "自测", "调试端点", "截图", "自动化测试",
                          "test", "debug", "endpoint", "capture", "autotest"]},
    execute=execute, refs=["140"],
    metadata={"source": "Guild/AI自反馈回环测试+实现手册", "category": "quality"})
