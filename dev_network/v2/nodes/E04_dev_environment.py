"""知识节点：开发环境与IDE模式——单文件架构/双版本同构/键位映射。

融合：自研IDE开发指南(架构总览) + Ctrl与win键交换 + CodingPlan接入
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

DEV_ENV_RULES = [
    "单文件零框架架构：全部前端代码集中在一个index.html——浏览器双击即用",
    "双版本同构：浏览器版和桌面版(Tauri)共用同一份源码——差异用补丁处理",
    "零网络依赖：所有资源内联或本地化——离线可用",
    "混淆构建：terser+html-minifier-terser 3-pass压缩——frontend/是产物绝不手动改",
    "所有修改在frontend-src/index.html——frontend/由构建脚本生成",
    "图标全部SVG内联——不使用emoji(跨系统渲染不一致)",
    "macOS键位交换：hidutil property --set修改Ctrl与Command映射——临时生效重启恢复",
    "键位交换必须双向——只做单向映射会导致功能键错乱",
    "聚合API网关需特定请求头(User-Agent/版本头)才能调用——缺少返回405",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(DEV_ENV_RULES)
    return ctx

node = Node(id="E04", name="开发环境模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["IDE", "开发环境", "单文件", "混淆", "obfuscate",
                          "键位", "键盘", "Ctrl", "Command", "hidutil",
                          "同构", "构建", "build script"]},
    execute=execute, refs=["170"],
    metadata={"source": "Guild/开发工具与工作流/自研IDE+键位交换", "category": "domain_dev_tools"})
