"""知识节点：即时通讯机器人集成——WebSocket协议/Token认证/嵌入式内存约束。

融合：QQ机器人接入指南（去敏化：移除项目名/AppID/具体URL）
适用于任何IM Bot WebSocket+HTTP API集成场景。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

IM_BOT_RULES = [
    "IM Bot标准协议流程：获取Token→获取Gateway URL→WebSocket连接→Hello(op=10)→Identify(op=2)→Ready→心跳循环",
    "Token有效期约2小时需定期刷新——提前300秒刷新避免请求中过期",
    "Intents用位掩码(1<<N)计算，不是数字相加——用位运算|组合",
    "私聊消息事件类型是C2C_MESSAGE_CREATE不是MESSAGE_CREATE——常见错误",
    "用户标识字段：私聊用author.user_openid，群聊用author.openid——字段名不同",
    "消息ID在d对象顶层不在author内——提取时注意层级",
    "消息请求必须包含msg_seq字段(0~65535)——时间戳低位^随机数",
    "ESP32同时维护WebSocket+HTTPS SSL内存不足——发送前断开WebSocket释放45KB再发",
    "断线重连用Resume(op=6)携带session_id和最后seq——比重新Identify快且不丢消息",
    "主动消息每月每用户4条限制——被动回复60分钟内无限制",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(IM_BOT_RULES)
    return ctx

node = Node(id="E06", name="IM Bot集成",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["机器人", "bot", "WebSocket", "IM", "消息",
                          "message", "Token", "Gateway", "heartbeat",
                          "心跳", "私聊", "群聊", "Identify",
                          "Resume", "session"]},
    execute=execute, refs=["370", "360"],
    metadata={"source": "Guild/AI与LLM应用/QQ机器人(desensitized)", "category": "domain_ai"})
