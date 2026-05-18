"""域抽象：工程域 — LLM 路由，判断走哪条子路径。

不再全部展开 52 个 refs，而是用一次 LLM 调用分类意图，
只激活对应的 2-3 个子节点。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

KEYWORDS = [
    "应用", "app", "网页", "页面", "工具", "系统", "待办", "编辑器", "计算器", "看板",
    "tauri", "桌面", "ESP32", "嵌入式", "Arduino", "IoT", "websocket", "socket",
    "代理", "proxy", "API", "gateway", "LLM", "LM Studio", "agent",
    "bug", "fix", "debug", "修复", "调试",
    "css", "html", "js", "flex", "grid", "布局", "样式", "溢出", "代码",
    "函数", "组件", "博客", "网站", "迁移", "开发", "develop", "实现",
    "删除", "擦除", "格式化", "git", "测试", "部署",
    "特效", "光照", "动画", "导出", "渲染",
    "BLE", "蓝牙", "流式", "stream",
]

ROUTES = {
    "QA":    ["135"],
    "BUILD": ["010"],
    "FIX":   ["600", "420", "140"],
    "EMBED": ["360", "540", "640", "663"],
    "NET":   ["370", "390", "395", "530"],
    "GAME":  ["665", "976", "977", "E10", "E11"],
    "NLE":   ["180", "E20", "E21", "E22"],
    "TAURI": ["170"],
    "TOOL":  ["E00", "E01", "E02", "E03", "E04"],
    "AI":    ["520", "E05", "E06", "971"],
    "META":  ["600", "610", "630", "661", "662"],
}

def execute(ctx: dict) -> dict:
    ctx["_domain_routed"] = True
    task = ctx.get("task", "")

    route = ask(
        "将用户的技术请求分类到一个类别。只回答类别代号：\n"
        "QA = 纯技术问答（问原理/区别/方法，不需要写代码）\n"
        "BUILD = 创建应用/网站/工具（需要生成代码）\n"
        "FIX = 修复bug/调试问题\n"
        "EMBED = 嵌入式/ESP32/Arduino/IoT\n"
        "NET = 网络/WebSocket/API代理\n"
        "GAME = 游戏引擎/特效/渲染/光照\n"
        "NLE = 视频编辑/时间轴\n"
        "TAURI = Tauri桌面应用\n"
        "TOOL = 开发工具/Git/CI/CD\n"
        "AI = LLM/AI相关\n"
        "META = 方法论/模式/架构",
        task,
        max_tokens=5
    ).strip().upper()

    matched = None
    for key in ROUTES:
        if key in route:
            matched = key
            break
    if not matched:
        matched = "QA"

    ctx["_eng_route"] = matched
    ctx["_eng_refs"] = ROUTES[matched]
    return ctx

node = Node(
    id="B00", name="工程域",
    trigger={"type": "keyword", "target": "task",
             "keywords": KEYWORDS,
             "unless": "_domain_routed"},
    execute=execute,
    refs=list({r for refs in ROUTES.values() for r in refs}),
    metadata={"category": "domain", "layer": "abstraction"})
