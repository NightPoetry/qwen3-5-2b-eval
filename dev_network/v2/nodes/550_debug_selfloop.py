"""知识节点：交互调试五原则——可自视/可远操/可感知/可全知/可封印。

AI改一行代码后10秒内自己验证——不需要人编译、人点击、人描述。
三个核心动作循环：操作(/click,/eval)→感知(/state,/logs,/capture)→判断→修改→操作...
闭环标志：循环中没有任何一步需要人类介入。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

FIVE_PRINCIPLES = [
    "可自视：应用能捕获自身视觉输出（窗口缓冲区，不用系统截屏，零权限）",
    "可远操：所有UI操作可通过程序等价触发（直接调函数，不模拟DOM事件）",
    "可感知：每个操作结果能查询结构化数据（不是截图看文字）",
    "可全知：一条命令获取应用完整状态快照（连接/消息/错误/性能）",
    "可封印：以上能力在发布时完全关闭（编译期排除+运行期开关+只绑127.0.0.1）",
]

DEBUG_ENDPOINTS = [
    "/ping — 健康检查+基础指标",
    "/click — 远程触发按钮（传按钮ID→函数映射）",
    "/eval — 执行表达式（白名单或受限）",
    "/capture — 按需截图（返回PNG路径）",
    "/state — 应用完整状态快照",
    "/debug/logs — 结构化日志查询（按tag/level过滤）",
]

SELF_TEST_PATTERNS = [
    "lavfi生成fixture：ffmpeg内置color/sine源合成测试输入，无需准备素材",
    "invoke直调绕过dialog：file picker用hardcoded路径绕开",
    "注入虚拟state而非真实IO：构造合法对象push进state，跳过IO",
    "外部工具验证输出：ffprobe等给客观结构数据",
    "测试负责清理：结束后state恢复原状",
]

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    # 让模型判断当前任务是否涉及GUI/交互验证
    is_gui = ask(
        "这个任务是否涉及GUI、Web页面、桌面应用的交互或验证？只回答'是'或'否'。",
        f"任务：{task}",
        max_tokens=5
    ).strip()

    if "是" in is_gui:
        ctx.setdefault("_design_principles", []).extend(FIVE_PRINCIPLES)
        ctx.setdefault("_domain_rules", []).extend(DEBUG_ENDPOINTS)
        ctx.setdefault("_domain_rules", []).extend(SELF_TEST_PATTERNS)
    else:
        ctx.setdefault("_design_principles", []).extend(FIVE_PRINCIPLES)
        ctx.setdefault("_domain_rules", []).extend(DEBUG_ENDPOINTS)

    return ctx

node = Node(id="550", name="交互调试五原则",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["调试", "测试", "验证", "debug", "自测", "截图"]},
    execute=execute, refs=["480"],
    metadata={"source": "Skills/交互调试", "category": "quality"})
