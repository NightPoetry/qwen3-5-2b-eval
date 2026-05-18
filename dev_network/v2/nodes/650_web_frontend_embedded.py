"""知识节点：嵌入式Web前端——API请求/静态资源/Markdown渲染/localStorage。

适用于在资源受限设备上运行Web前端（嵌入式网关、IoT管理界面）的任务。
来源：web-frontend-embedded
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

WEB_EMBEDDED_KNOWLEDGE = """你是嵌入式Web前端专家。根据以下知识诊断前端问题。

## API请求模式
- 统一封装的请求函数如果内部固定.json()解析，就不能用于获取非JSON响应，否则报SyntaxError
- 获取原始文件内容用fetch()+.text()，结构化数据才用封装函数+.json()
- fetch()的.ok属性在非2xx时为false但不throw，必须主动检查
- encodeURIComponent()编码/为%2F、空格为%20、中文为%E4%BD%A0，后端必须能解码
- 纯ASCII字母数字经encodeURIComponent后不变，token等参数无需后端解码

## 请求封装陷阱
- 统一封装方便复用但硬编码响应解析方式会成为异构端点的绊脚石
- 要么支持多种响应类型，要么明确标注仅适用于JSON端点
- 返回非JSON的端点应绕过封装直接使用fetch

## 前端防重入
- 用Set跟踪正在请求的资源可防止并发重复请求
- 必须在finally块中清除标记，否则请求失败后资源永远无法重新加载

## Markdown渲染
- marked.js(~40KB min)是轻量级单文件MD渲染库，适合带宽和存储受限环境
- 手写正则解析器在嵌套列表、代码块内特殊字符等场景容易出错

## 静态资源加载
- script src加载失败时脚本内所有函数不可用，后续依赖代码报xxx is not defined
- Content-Type必须正确，.js文件返回text/html会被浏览器拒绝执行
- 嵌入式HTTP服务器上分块传输可用固定小缓冲区服务任意大文件

## localStorage
- 存储的token在服务端重启后失效（token重新生成），前端应验证失败时自动清除并跳转登录
- localStorage按域名含端口隔离，不同设备IP各自独立

## 编辑/预览模式
- 同一面板用两个互斥元素（textarea+div）比切换innerHTML更可靠
- 按文件类型自动选初始模式（.md默认预览、.json默认编辑）
"""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    js = ctx.get("js", "")

    result = ask(
        WEB_EMBEDDED_KNOWLEDGE +
        "\n分析以下任务涉及的嵌入式Web前端问题，给出具体建议（每条一行，不超过5条）。"
        "如果不涉及嵌入式Web前端问题，回答\"无嵌入式前端问题\"。",
        f"任务：{task[:400]}\nJS片段：{js[:300]}",
        max_tokens=300
    ).strip()

    if "无嵌入式前端问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx


node = Node(id="650", name="嵌入式Web前端",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["嵌入式前端", "网关页面", "IoT界面", "ESP32前端",
                          "localStorage", "fetch", "marked", "Content-Type",
                          "文件管理", "chunked", "管理界面", "控制面板"]},
    execute=execute, refs=["360", "240"],
    metadata={"source": "knowledge/web-frontend-embedded", "category": "domain_frontend"})
