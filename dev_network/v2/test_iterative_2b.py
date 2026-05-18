"""
测试2B模型能否通过多轮对话修正自己的作品。

流程：
  1. 给模型看它之前生成的页面（的CSS部分）
  2. 要求它修改（比如换色、改布局）
  3. 看它能不能正确修改
"""

import requests
from pathlib import Path

API_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-2b"


def chat(messages, max_tokens=2048):
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }, timeout=300)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    # 读取裸2B之前生成的页面
    raw_html = (Path(__file__).parent / "output_raw_2b" / "index.html").read_text()

    print("=== 2B多轮修正测试 ===\n")

    # 测试1：改背景色
    print("--- 测试1：要求改为暗色主题 ---")
    messages = [
        {"role": "user", "content": f"这是一个网页的HTML代码：\n\n{raw_html}"},
        {"role": "assistant", "content": "好的，我看到了这个网页代码。请问你需要做什么修改？"},
        {"role": "user", "content": "把背景改成深色主题，背景色用#0d1117，文字用浅色。只输出修改后的完整<style>标签内容，不要其他东西。"},
    ]
    result1 = chat(messages)
    print(f"  输出长度: {len(result1)} chars")
    print(f"  包含#0d1117: {'#0d1117' in result1}")
    print(f"  包含浅色文字: {'#f0f6fc' in result1 or '#e0e0e0' in result1 or '#ffffff' in result1 or 'white' in result1 or '#ccc' in result1 or '#c9d1d9' in result1}")
    print(f"  前100字: {result1[:100]}")
    print()

    # 测试2：改布局
    print("--- 测试2：要求卡片改为两列网格 ---")
    messages2 = [
        {"role": "user", "content": f"这是网页CSS：\n\n{result1[:1500]}"},
        {"role": "assistant", "content": "我看到了CSS。需要做什么修改？"},
        {"role": "user", "content": "把博文卡片从横排改为两列网格布局。只输出.blog-posts和.card的CSS，不要其他。"},
    ]
    result2 = chat(messages2, max_tokens=512)
    print(f"  输出长度: {len(result2)} chars")
    print(f"  包含grid: {'grid' in result2}")
    print(f"  包含2列: {'repeat(2' in result2 or '1fr 1fr' in result2 or 'grid-template-columns' in result2}")
    print(f"  内容:\n{result2[:300]}")
    print()

    # 测试3：加渐变标题（之前没做到的）
    print("--- 测试3：要求标题加渐变色 ---")
    messages3 = [
        {"role": "user", "content": "给.logo选择器加上从#2563eb到#7c3aed的渐变色文字效果。只输出这一个选择器的CSS。"},
    ]
    result3 = chat(messages3, max_tokens=256)
    print(f"  输出长度: {len(result3)} chars")
    print(f"  包含gradient: {'gradient' in result3}")
    print(f"  包含background-clip: {'background-clip' in result3 or 'text-fill-color' in result3}")
    print(f"  内容:\n{result3}")


if __name__ == "__main__":
    main()
