"""知识节点：三层设计分离——逻辑/交互/视觉 + 前端设计经验保存。

架构级节点。确保生成的代码遵循三层分离：
  - 逻辑层（数据结构、状态、规则）→ JS数据层
  - 交互层（操作流程、事件响应）→ JS事件层
  - 视觉层（配色、字体、间距）→ CSS

融合：前端设计经验保存指南（三层保存：逻辑设计/交互设计/视觉设计）
+ 前后端接口对接规范（接口文档先行）
+ 本地资源替代远程资源（优先本地，失败才简化）。
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

def execute(ctx: dict) -> dict:
    js = ctx.get("js", "")
    css = ctx.get("css", "")
    html = ctx.get("html", "")
    issues = []

    # JS中不应有CSS（inline style）
    if js:
        inline_styles = re.findall(r'\.style\.\w+\s*=', js)
        if len(inline_styles) > 3:
            issues.append(f"JS中{len(inline_styles)}处inline style——视觉层应在CSS中")

    # HTML中不应有JS逻辑（允许onclick单行）
    if html:
        script_blocks = re.findall(r'<script[^>]*>(.+?)</script>', html, re.DOTALL)
        long_scripts = [s for s in script_blocks if len(s.strip()) > 200]
        if long_scripts:
            issues.append("HTML中嵌入了大段JS——逻辑层应分离到.js文件")

    # 检查远程资源依赖（本地资源替代远程资源原则）
    if html:
        remote_fonts = re.findall(r'https?://fonts\.googleapis\.com', html)
        remote_cdn = re.findall(r'https?://cdn\.\w+', html)
        remote_api = re.findall(r'https?://api\.\w+\.com', html)
        total_remote = len(remote_fonts) + len(remote_cdn) + len(remote_api)
        if total_remote > 0:
            issues.append(
                f"发现{total_remote}处远程资源引用——本地应用应优先下载到本地"
            )

    # 检查前后端接口一致性：fetch URL格式
    if js:
        fetch_calls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', js)
        if fetch_calls:
            for url in fetch_calls:
                if not url.startswith("/") and not url.startswith("http"):
                    issues.append(f"fetch URL '{url}' 格式异常——应以/或http开头")

    if issues:
        ctx.setdefault("_architecture_review", []).extend(issues)
    return ctx

node = Node(id="250", name="三层分离检查",
    trigger={"type": "key_exists", "key": "js"},
    execute=execute, refs=["Y20"],
    metadata={"source": "Guild/三层分离+前端经验+接口规范+本地资源", "category": "architecture"})
