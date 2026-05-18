"""
确定性验证器 — 程序能做的事不让模型做。

HTML/CSS/JS 的结构验证是确定性的：
  - HTML 标签嵌套是否正确
  - CSS 是否混入了 HTML
  - JS 是否混入了 HTML
  - 文件间引用是否存在
  - 基本格式是否完整

这些 100% 用代码解决，不问模型。
"""

import re
from dataclasses import dataclass


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    message: str
    fix: str = ""  # 程序能自动修复的就直接修


def validate_html(content: str, expected_css: list[str] = None,
                  expected_js: list[str] = None) -> tuple[str, list[Issue]]:
    """验证并自动修复 HTML。返回 (修复后内容, 问题列表)。"""
    issues = []
    fixed = content

    # 1. body 嵌套在 head 里 → 自动修复
    head_start = fixed.find("<head")
    head_end = fixed.find("</head>")
    body_start = fixed.find("<body")

    if head_start >= 0 and body_start >= 0 and head_end >= 0:
        if head_start < body_start < head_end:
            # body 在 head 内 — 把 </head> 移到 body 之前
            fixed = fixed[:body_start] + "</head>\n" + fixed[body_start:]
            # 移除原来的 </head>
            old_head_end_pos = fixed.find("</head>", body_start + 10)
            if old_head_end_pos > 0:
                fixed = fixed[:old_head_end_pos] + fixed[old_head_end_pos + 7:]
            issues.append(Issue("error", "body嵌套在head内", "已自动修复"))

    # 2. 缺少 DOCTYPE
    if "<!DOCTYPE" not in fixed.upper() and "<!doctype" not in fixed:
        fixed = "<!DOCTYPE html>\n" + fixed
        issues.append(Issue("warning", "缺少DOCTYPE", "已添加"))

    # 3. 缺少 viewport meta
    if "viewport" not in fixed:
        insert_pos = fixed.find("<head")
        if insert_pos >= 0:
            head_close = fixed.find(">", insert_pos)
            if head_close >= 0:
                meta = '\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                fixed = fixed[:head_close+1] + meta + fixed[head_close+1:]
                issues.append(Issue("warning", "缺少viewport", "已添加"))

    # 4. 缺少 charset
    if "charset" not in fixed.lower():
        insert_pos = fixed.find("<head")
        if insert_pos >= 0:
            head_close = fixed.find(">", insert_pos)
            if head_close >= 0:
                meta = '\n    <meta charset="UTF-8">'
                fixed = fixed[:head_close+1] + meta + fixed[head_close+1:]
                issues.append(Issue("warning", "缺少charset", "已添加"))

    # 5. script 在 head 里而不是 body 末尾
    if expected_js:
        for js in expected_js:
            script_tag = f"<script src='{js}'></script>"
            alt_tag = f'<script src="{js}"></script>'
            if script_tag in fixed or alt_tag in fixed:
                # 检查是否在 head 中
                tag = script_tag if script_tag in fixed else alt_tag
                tag_pos = fixed.find(tag)
                body_pos = fixed.find("<body")
                if body_pos > 0 and tag_pos < body_pos:
                    # 从 head 移到 body 末尾
                    fixed = fixed.replace(tag, "")
                    close_body = fixed.find("</body>")
                    if close_body > 0:
                        fixed = fixed[:close_body] + f"    {tag}\n" + fixed[close_body:]
                    else:
                        close_html = fixed.find("</html>")
                        if close_html > 0:
                            fixed = fixed[:close_html] + f"    {tag}\n</body>\n" + fixed[close_html:]
                    issues.append(Issue("error", f"script在head中", "已移到body末尾"))

    # 6. 确保有 CSS 引用
    if expected_css:
        for css in expected_css:
            if css not in fixed:
                insert_pos = fixed.find("</head>")
                if insert_pos > 0:
                    link = f'    <link rel="stylesheet" href="{css}">\n'
                    fixed = fixed[:insert_pos] + link + fixed[insert_pos:]
                    issues.append(Issue("error", f"缺少CSS引用{css}", "已添加"))

    # 7. 重复ID检测修复：同一ID出现多次时保留标签匹配的那个
    id_occurrences = re.findall(r'<(\w+)[^>]*\bid=[\'"](\w+)[\'"]', fixed)
    id_counts = {}
    for tag, eid in id_occurrences:
        id_counts.setdefault(eid, []).append(tag)

    for eid, tags in id_counts.items():
        if len(tags) > 1:
            # 多个元素使用同一ID — 移除包裹元素（div/section/article）上的ID
            wrapper_tags = {"div", "section", "article", "main", "header", "footer", "nav"}
            for wtag in wrapper_tags:
                if wtag in tags:
                    pattern = rf'(<{wtag})\s+id=[\'\"]{eid}[\'\"]([\s>])'
                    fixed = re.sub(pattern, rf'\1\2', fixed, count=1)
                    issues.append(Issue("error", f"重复ID#{eid}在<{wtag}>上", "已移除包裹层ID"))
                    break

    # 8. 清理空行过多
    fixed = re.sub(r'\n{3,}', '\n\n', fixed)

    return fixed, issues


def validate_css(content: str) -> tuple[str, list[Issue]]:
    """验证 CSS。"""
    issues = []
    fixed = content

    # 去掉开头的文件名（模型有时会输出 "style.css\n..."）
    lines = fixed.split("\n")
    if lines and lines[0].strip().endswith(".css"):
        fixed = "\n".join(lines[1:])
        issues.append(Issue("warning", "CSS开头有文件名", "已移除"))

    # 去掉 markdown 代码块标记
    if fixed.startswith("```"):
        fixed = re.sub(r'^```\w*\n', '', fixed)
        fixed = re.sub(r'\n```\s*$', '', fixed)
        issues.append(Issue("warning", "CSS包含markdown标记", "已移除"))

    # 检查是否混入了 HTML
    if "<html" in fixed or "<body" in fixed or "<div" in fixed:
        issues.append(Issue("error", "CSS中混入HTML标签", "无法自动修复"))

    # [知识卡001] flex子元素防溢出：flex:1 必须伴随 min-width:0
    blocks = re.findall(r'([^{}]+)\{([^}]*)\}', fixed)
    for selector, body in blocks:
        if re.search(r'flex:\s*1', body) and 'min-width' not in body:
            inject = "  min-width: 0;\n  overflow: hidden;\n"
            old_block = f"{selector}{{{body}}}"
            new_body = body.rstrip() + "\n" + inject
            new_block = f"{selector}{{{new_body}}}"
            fixed = fixed.replace(old_block, new_block, 1)
            issues.append(Issue("warning", f"flex:1缺min-width({selector.strip()})", "已添加防溢出"))

    return fixed, issues


def validate_js(content: str) -> tuple[str, list[Issue]]:
    """验证 JS。"""
    issues = []
    fixed = content

    # 去掉 markdown 代码块标记
    if fixed.startswith("```"):
        fixed = re.sub(r'^```\w*\n', '', fixed)
        fixed = re.sub(r'\n```\s*$', '', fixed)
        issues.append(Issue("warning", "JS包含markdown标记", "已移除"))

    # 如果模型输出了完整 HTML 页面而不是纯 JS → 提取 <script> 内容
    if "<script" in fixed and "<html" in fixed.lower():
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', fixed, re.DOTALL)
        if scripts:
            # 取最长的 script 块（通常是主逻辑）
            fixed = max(scripts, key=len).strip()
            issues.append(Issue("error", "模型输出了HTML而非JS", "已提取script内容"))
        else:
            issues.append(Issue("error", "JS中混入HTML但无script块", "无法修复"))
    elif "<script" in fixed:
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', fixed, re.DOTALL)
        if scripts:
            fixed = max(scripts, key=len).strip()
            issues.append(Issue("warning", "JS包含script标签", "已提取纯JS"))

    # 检查是否有 DOMContentLoaded
    if "DOMContentLoaded" not in fixed and "document.ready" not in fixed:
        fixed = f"document.addEventListener('DOMContentLoaded', () => {{\n{fixed}\n}});\n"
        issues.append(Issue("warning", "缺少DOMContentLoaded", "已包裹"))

    # [知识卡009] 可逆操作不弹确认框：列表项删除/状态切换是可逆的
    confirm_pattern = r'if\s*\(\s*confirm\s*\([^)]*\)\s*\)\s*\{'
    if re.search(confirm_pattern, fixed):
        fixed = re.sub(
            r'if\s*\(\s*confirm\s*\([^)]*\)\s*\)\s*\{',
            '{',  # 移除confirm判断，直接执行块内代码
            fixed
        )
        issues.append(Issue("warning", "移除可逆操作的confirm()", "直接执行+支持撤销"))

    return fixed, issues


def validate_id_consistency(contract: dict, html: str, js: str) -> tuple[str, str, list[Issue]]:
    """
    ID一致性验证：契约中的所有静态元素ID必须出现在HTML和JS中。
    缺失则自动补齐。
    """
    issues = []
    fixed_html = html
    fixed_js = js

    elements = contract.get("elements", [])

    # JS 中需要 getElementById 的ID列表
    js_id_refs = set(re.findall(r'getElementById\([\'"](\w+)[\'"]\)', js))

    for elem in elements:
        eid = elem["id"]
        tag = elem["tag"]
        purpose = elem.get("purpose", "")

        # --- HTML 检查 ---
        html_pattern = rf'id=[\'\"]{eid}[\'\"' + r']'
        if not re.search(html_pattern, fixed_html):
            # 在 </body> 前插入元素
            insert_pos = fixed_html.find("</body>")
            if insert_pos < 0:
                insert_pos = len(fixed_html)

            if tag == "input":
                new_elem = f'    <input type="text" id="{eid}" placeholder="{purpose}">\n'
            elif tag == "button":
                new_elem = f'    <button id="{eid}">{purpose}</button>\n'
            elif tag == "ul":
                new_elem = f'    <ul id="{eid}"></ul>\n'
            elif tag == "select":
                new_elem = f'    <select id="{eid}"></select>\n'
            else:
                new_elem = f'    <{tag} id="{eid}"></{tag}>\n'

            fixed_html = fixed_html[:insert_pos] + new_elem + fixed_html[insert_pos:]
            issues.append(Issue("error", f"HTML缺少#{eid}", f"已添加<{tag}>"))

        # --- JS 检查 ---
        if eid not in js_id_refs:
            # 在文件顶部（DOMContentLoaded内部或文件开头）插入获取语句
            get_line = f"const {eid} = document.getElementById('{eid}');\n"
            # 找 DOMContentLoaded 回调的开头
            dom_match = re.search(
                r"(addEventListener\(['\"]DOMContentLoaded['\"].*?(?:=>|function)\s*\{?\s*\n)",
                fixed_js
            )
            if dom_match:
                insert_at = dom_match.end()
            else:
                insert_at = 0

            fixed_js = fixed_js[:insert_at] + get_line + fixed_js[insert_at:]
            js_id_refs.add(eid)
            issues.append(Issue("error", f"JS缺少#{eid}引用", f"已添加getElementById"))

    return fixed_html, fixed_js, issues


def validate_file(filename: str, content: str,
                  all_files: dict[str, str] = None) -> tuple[str, list[Issue]]:
    """根据文件类型选择验证器。"""
    ext = filename.split(".")[-1].lower()
    all_files = all_files or {}

    css_files = [f for f in all_files if f.endswith(".css")]
    js_files = [f for f in all_files if f.endswith(".js")]

    if ext == "html":
        return validate_html(content, expected_css=css_files, expected_js=js_files)
    elif ext == "css":
        return validate_css(content)
    elif ext == "js":
        return validate_js(content)
    return content, []
