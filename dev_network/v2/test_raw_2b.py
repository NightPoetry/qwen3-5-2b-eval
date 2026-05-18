"""
裸2B测试 — 不编排、不拆解、不验证，一次性让模型生成完整网页。
用于和v2管线对比。
"""

import requests
from pathlib import Path

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"


def raw_generate(prompt, max_tokens=4096):
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }, timeout=360)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    print("=== 裸2B直接生成测试 ===\n")

    prompt = """生成一个个人技术博客的完整HTML页面。CSS和JS写在HTML里面。
亮色主题，白色背景，有导航栏、3篇博文卡片、关于页。中文内容。
直接输出HTML代码："""

    print("发送请求到2B模型...")
    result = raw_generate(prompt)
    print(f"模型输出: {len(result)} chars\n")

    # 保存原始输出
    output_dir = Path(__file__).parent / "output_raw_2b"
    output_dir.mkdir(exist_ok=True)

    # 尝试提取HTML
    if "```html" in result:
        import re
        blocks = re.findall(r'```html\n(.*?)```', result, re.DOTALL)
        if blocks:
            html = blocks[0]
        else:
            html = result
    elif "<html" in result.lower():
        start = result.lower().find("<!doctype") if "<!doctype" in result.lower() else result.lower().find("<html")
        if start >= 0:
            html = result[start:]
        else:
            html = result
    else:
        html = result

    (output_dir / "index.html").write_text(html)
    print(f"保存到: {output_dir}/index.html")
    print(f"HTML大小: {len(html)} chars")

    # 简单分析
    print(f"\n--- 输出分析 ---")
    print(f"包含<html>: {'<html' in html.lower()}")
    print(f"包含<style>: {'<style' in html.lower()}")
    print(f"包含<script>: {'<script' in html.lower()}")
    print(f"包含<body>: {'<body' in html.lower()}")
    print(f"包含中文: {any(ord(c) > 0x4e00 for c in html)}")
    print(f"CSS行数: {html.lower().count(chr(10), html.lower().find('<style'), html.lower().find('</style')) if '<style' in html.lower() else 0}")

    # 看前200字符
    print(f"\n--- 前300字符 ---")
    print(html[:300])
    print("...")
    print(f"\n--- 后200字符 ---")
    print(html[-200:])


if __name__ == "__main__":
    main()
