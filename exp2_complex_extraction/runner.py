"""
Experiment runner: executes one condition (A, B, or C) for one test case.

run_condition_a  — full context, single API call, parse JSON from response text
run_condition_b  — full tool suite (read_next + advance_past + stack + record)
run_condition_c  — navigation tools only (read_next + advance_past), no stack/record
"""

import json
import os
import re
import time

import requests

from tools import ToolState, execute_tool, make_tool_schemas

API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"

MAX_ROUNDS = 80   # safety cap on tool-calling loop
REQUEST_TIMEOUT = 300


# ── Low-level API call ────────────────────────────────────────────────────────

def _chat(messages: list[dict], tools: list[dict] | None = None) -> dict:
    payload: dict = {
        "model":       MODEL_NAME,
        "messages":    messages,
        "temperature": 0.0,
        "max_tokens":  1024,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    resp = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]


# ── JSON extraction helper ────────────────────────────────────────────────────

def _extract_json_list(text: str) -> list:
    """Pull the last JSON array from a text string."""
    # Try the whole text first
    for match in reversed(list(re.finditer(r'\[.*?\]', text, re.DOTALL))):
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            continue
    return []


def _extract_heading_list(text: str) -> list[dict]:
    """Extract list of {"level": int, "text": str} from model output."""
    raw = _extract_json_list(text)
    result = []
    for item in raw:
        if isinstance(item, dict) and "level" in item and "text" in item:
            try:
                result.append({"level": int(item["level"]), "text": str(item["text"]).strip()})
            except (ValueError, TypeError):
                pass
        elif isinstance(item, str):
            result.append({"level": 0, "text": item.strip()})
    return result


# ── Condition A ───────────────────────────────────────────────────────────────

def run_condition_a(
    system_prompt: str,
    user_prompt: str,
    task_type: str,
) -> dict:
    t0 = time.time()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    choice = _chat(messages)
    text = choice["message"].get("content", "")
    elapsed = time.time() - t0

    if task_type == "html_headings":
        found = _extract_heading_list(text)
    else:
        found = _extract_json_list(text)
        found = [str(x).strip() for x in found]

    return {
        "condition": "A",
        "found": found,
        "rounds": 1,
        "tool_calls": 0,
        "elapsed_s": round(elapsed, 2),
        "raw_response": text,
    }


# ── Condition B ───────────────────────────────────────────────────────────────

def run_condition_b(
    system_prompt: str,
    user_prompt: str,
    text: str,
    task_type: str,
    history_window: int = 0,   # 0 = 保留全部；N > 0 = 只保留最近 N 轮（system+user 始终保留）
) -> dict:
    state = ToolState(text)
    tools = make_tool_schemas(include_stack=True, include_record=True)

    fixed_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]
    messages = list(fixed_messages)

    t0 = time.time()
    rounds = 0
    finished = False

    while rounds < MAX_ROUNDS:
        rounds += 1
        choice = _chat(messages, tools=tools)
        finish_reason = choice["finish_reason"]
        message = choice["message"]

        if finish_reason == "tool_calls":
            tool_calls = message.get("tool_calls", [])
            messages.append({
                "role":       "assistant",
                "content":    message.get("content") or "",
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                result  = execute_tool(state, fn_name, fn_args)

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc["id"],
                    "content":      result,
                })

            # 主动终止：模型调用了 get_records（表示完成）
            called_names = [tc["function"]["name"] for tc in tool_calls]
            if "get_records" in called_names:
                finished = True
                break
            # 兜底：游标到达文末
            if state.cursor >= len(text):
                finished = True
                break

            # 滑动窗口：裁剪过长的对话历史，只保留最近 N 轮
            if history_window > 0:
                tail = messages[len(fixed_messages):]
                if len(tail) > history_window * 2:  # 每轮约 2 条消息
                    tail = tail[-(history_window * 2):]
                messages = list(fixed_messages) + tail

        elif finish_reason in ("stop", "length"):
            # 模型提前输出文字——若文档未读完则强制继续
            if state.cursor < len(text) and rounds < MAX_ROUNDS - 1:
                pct = round(state.cursor / len(text) * 100)
                messages.append({
                    "role": "user",
                    "content": (
                        f"文档尚未读完（当前进度 {pct}%），严禁停止。"
                        "请立即调用 read_next() 继续读取剩余内容，不得输出任何文字。"
                    ),
                })
                # 保留 message（如有文字内容）以维持上下文
                if message.get("content"):
                    messages.insert(-1, {"role": "assistant", "content": message["content"]})
            else:
                finished = True
                break
        else:
            break

    elapsed = time.time() - t0

    # 发现来自 state.records（由 record() 工具写入）
    if task_type == "html_headings":
        found = [
            {"level": int(r["category"].lstrip("h") or 0), "text": r["item"]}
            for r in state.records
            if r["category"].startswith("h")
        ]
    else:
        found = [r["item"] for r in state.records]

    return {
        "condition": "B",
        "found": found,
        "rounds": rounds,
        "tool_calls": len(state.call_log),
        "cursor_final": state.cursor,
        "text_length": len(text),
        "coverage_pct": round(state.cursor / max(len(text), 1) * 100, 1),
        "elapsed_s": round(elapsed, 2),
        "finished": finished,
        "tool_call_log": state.call_log,
    }


# ── Condition C ───────────────────────────────────────────────────────────────

def run_condition_c(
    system_prompt: str,
    user_prompt: str,
    text: str,
    task_type: str,
) -> dict:
    state = ToolState(text)
    # Navigation tools only — no stack, no record
    tools = make_tool_schemas(include_stack=False, include_record=False)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]

    t0 = time.time()
    rounds = 0
    last_text = ""
    finished = False

    while rounds < MAX_ROUNDS:
        rounds += 1
        choice = _chat(messages, tools=tools)
        finish_reason = choice["finish_reason"]
        message = choice["message"]

        if finish_reason == "tool_calls":
            tool_calls = message.get("tool_calls", [])
            messages.append({
                "role":       "assistant",
                "content":    message.get("content") or "",
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                result  = execute_tool(state, fn_name, fn_args)

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc["id"],
                    "content":      result,
                })

            if state.cursor >= len(text):
                finished = True
                # 给模型最后一次机会输出 JSON
                messages.append({"role": "user", "content": "文档已读完，请在回复最后一行输出你记录的所有发现的 JSON 列表。"})
                choice2 = _chat(messages, tools=tools)
                last_text = choice2["message"].get("content", "")
                break

        elif finish_reason in ("stop", "length"):
            last_text = message.get("content", "")
            finished = True
            break
        else:
            break

    elapsed = time.time() - t0

    # Findings must be parsed from the model's final text output
    if task_type == "html_headings":
        found = _extract_heading_list(last_text)
    else:
        found = _extract_json_list(last_text)
        found = [str(x).strip() for x in found]

    return {
        "condition": "C",
        "found": found,
        "rounds": rounds,
        "tool_calls": len(state.call_log),
        "cursor_final": state.cursor,
        "text_length": len(text),
        "coverage_pct": round(state.cursor / max(len(text), 1) * 100, 1),
        "elapsed_s": round(elapsed, 2),
        "finished": finished,
        "raw_response": last_text,
    }
