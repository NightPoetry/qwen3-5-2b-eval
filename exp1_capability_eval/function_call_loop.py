"""
Complete Function Calling Loop Demo — Qwen3.5 2B

Scenario: User asks about travel to Tokyo.
The model will call multiple tools across multiple rounds:
  Round 1 → model calls get_weather("Tokyo")
  Round 2 → seeing rain, model calls get_forecast("Tokyo", days=3)
  Round 3 → model calls get_exchange_rate("USD", "JPY")
  Final   → model synthesizes all results into a travel advice answer

Our code plays the role of the "tool executor" — returning fake but realistic data.
"""

import json
import os
import requests

API_URL    = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
MODEL_NAME = "qwen3.5-2b"

# ── Tool definitions ─────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Get a multi-day weather forecast for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Number of days (1–7)"},
                },
                "required": ["city", "days"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get the current exchange rate between two currencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "Source currency code, e.g. USD"},
                    "to_currency":   {"type": "string", "description": "Target currency code, e.g. JPY"},
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    },
]

# ── Fake tool executor ────────────────────────────────────────────────────────

def execute_tool(name: str, args: dict) -> str:
    """Simulate real tool execution — returns fake but realistic data."""
    if name == "get_weather":
        city = args.get("city", "Unknown")
        return json.dumps({
            "city":        city,
            "temperature": "16°C",
            "condition":   "rainy",
            "humidity":    "88%",
            "wind":        "12 km/h",
            "note":        "Heavy rain expected throughout the day.",
        })

    elif name == "get_forecast":
        city = args.get("city", "Unknown")
        days = args.get("days", 3)
        forecast = [
            {"day": "Tomorrow",       "condition": "heavy rain",    "high": "15°C", "low": "11°C"},
            {"day": "Day after",      "condition": "cloudy",        "high": "18°C", "low": "13°C"},
            {"day": "In 3 days",      "condition": "partly sunny",  "high": "21°C", "low": "14°C"},
        ]
        return json.dumps({"city": city, "forecast": forecast[:days]})

    elif name == "get_exchange_rate":
        from_c = args.get("from_currency", "USD")
        to_c   = args.get("to_currency",   "JPY")
        rates  = {
            ("USD", "JPY"): 152.3,
            ("EUR", "JPY"): 164.7,
            ("GBP", "JPY"): 191.2,
        }
        rate = rates.get((from_c.upper(), to_c.upper()), 1.0)
        return json.dumps({
            "from":        from_c.upper(),
            "to":          to_c.upper(),
            "rate":        rate,
            "note":        f"1 {from_c.upper()} = {rate} {to_c.upper()}",
        })

    return json.dumps({"error": f"Unknown tool: {name}"})


# ── API call ─────────────────────────────────────────────────────────────────

def chat(messages: list[dict]) -> dict:
    resp = requests.post(API_URL, json={
        "model":       MODEL_NAME,
        "messages":    messages,
        "tools":       TOOLS,
        "tool_choice": "auto",
        "temperature": 0.0,
        "max_tokens":  1024,
    }, timeout=300)
    resp.raise_for_status()
    return resp.json()["choices"][0]


# ── Main loop ─────────────────────────────────────────────────────────────────

def run():
    SEP = "─" * 60

    print("=" * 60)
    print("  Function Calling Loop Demo — Qwen3.5 2B")
    print("=" * 60)

    user_question = (
        "I'm flying to Tokyo from the US tomorrow. "
        "What's the weather like? Should I pack an umbrella? "
        "Also, how much yen will I get if I exchange 500 USD?"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful travel assistant. "
                "Use the available tools to gather real-time information "
                "before answering. Call multiple tools if needed."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    print(f"\n[USER]\n{user_question}\n")

    round_num = 0

    while True:
        round_num += 1
        print(SEP)
        print(f"  Round {round_num} — calling model ...")
        print(SEP)

        choice        = chat(messages)
        finish_reason = choice["finish_reason"]
        message       = choice["message"]

        # ── Model wants to call tool(s) ──────────────────────────────────────
        if finish_reason == "tool_calls":
            tool_calls = message.get("tool_calls", [])

            # Add assistant's tool-call message to history
            messages.append({
                "role":       "assistant",
                "content":    message.get("content") or "",
                "tool_calls": tool_calls,
            })

            print(f"  Model requested {len(tool_calls)} tool call(s):\n")

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                call_id = tc["id"]

                print(f"  ▶ CALL  : {fn_name}({fn_args})")

                # Execute the tool
                result = execute_tool(fn_name, fn_args)
                result_pretty = json.dumps(json.loads(result), indent=2)

                print(f"  ◀ RESULT: {result_pretty}\n")

                # Append tool result to message history
                messages.append({
                    "role":         "tool",
                    "tool_call_id": call_id,
                    "content":      result,
                })

            print("  Sending tool results back to model ...")

        # ── Model is done — final answer ──────────────────────────────────────
        elif finish_reason in ("stop", "length"):
            final = message.get("content", "").strip()
            print(f"\n[ASSISTANT — Final Answer]\n{final}\n")
            print("=" * 60)
            print(f"  Done in {round_num} round(s).")
            print("=" * 60)
            break

        else:
            print(f"  Unexpected finish_reason: {finish_reason}")
            break


if __name__ == "__main__":
    run()
