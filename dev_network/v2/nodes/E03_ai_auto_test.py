"""知识节点：AI造物自动测试——测试接口/Debug模式分离/自验证闭环。

融合：AI造物自动测试原则 + macOS应用UI自动化闭环调试
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

AUTO_TEST_RULES = [
    "AI生成程序必须留测试接口让AI自动读取结果——不依赖用户做中间人",
    "测试结果输出JSON格式含name/status/error字段——AI可直接解析定位问题",
    "Debug模式和线上模式必须分离——测试路由线上返回404不暴露存在",
    "启动时安全检查：线上模式发现test/debug路由注册则拒绝启动",
    "macOS应用自截图闭环：NSView.cacheDisplay→PNG→AI读取验证UI——零权限",
    "沙盒应用截图写自己容器目录——不涉及其他应用无需系统权限",
    "进阶：内置127.0.0.1调试HTTP服务随时curl截图——端口用5位数避免冲突",
    "调试服务必须绑定回环地址(127.0.0.1)——不能用0.0.0.0",
    "发行版默认关闭调试服务——用#if DEBUG或环境变量控制",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(AUTO_TEST_RULES)
    return ctx

node = Node(id="E03", name="AI自动测试",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["测试", "test", "debug", "调试", "自动化",
                          "截图", "screenshot", "验证", "CI",
                          "闭环", "自检", "fixture"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/AI与LLM应用/AI造物测试+macOS闭环调试", "category": "domain_dev_tools"})
