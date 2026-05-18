"""
LLM 调用工具 — 节点中需要模型能力时使用。

隔离对话：每次调用都是独立的，不共享上下文。
2B原则：一次只问一个简单问题。

配置：通过环境变量或直接修改下方默认值。
  LLM_API_URL: OpenAI 兼容 API 地址（默认 localhost:1234）
  LLM_MODEL:   模型名称（默认 qwen3.5-2b）
"""

import os
import requests

API_URL = os.environ.get("LLM_API_URL", "http://localhost:1234/v1/chat/completions")
MODEL = os.environ.get("LLM_MODEL", "qwen3.5-2b")
TIMEOUT = 120


def ask(system: str, user: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
    """隔离对话：独立上下文问一个问题。"""
    resp = requests.post(API_URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
