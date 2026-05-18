"""域抽象：工程域 — 纯路由，不调 LLM。

覆盖代码生成、调试修复、领域知识（Tauri/嵌入式/WebSocket/NLE/API）、方法论。
关键词取自所有工程类节点的 keyword trigger 并集。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

KEYWORDS = [
    "应用", "app", "网页", "页面", "工具", "系统", "待办", "编辑器", "计算器", "看板",
    "tauri", "桌面", "desktop", "native",
    "时间轴", "视频编辑", "播放", "timeline", "NLE", "剪辑",
    "ESP32", "嵌入式", "Arduino", "IoT", "单片机", "固件", "embedded", "watchdog", "看门狗",
    "websocket", "ws", "socket", "长连接", "实时", "推送",
    "代理", "proxy", "API", "gateway", "负载均衡", "转发", "代理网关", "中转",
    "LLM", "LM Studio", "temperature", "max_tokens", "chat/completions",
    "thinking", "enable_thinking", "qwen", "tool_call",
    "agent", "自动化", "autonomous",
    "bug", "fix", "debug", "regression", "修复", "调试", "回归",
    "css", "html", "js", "flex", "grid", "布局", "样式", "溢出", "overflow", "对齐",
    "代码", "函数", "组件", "模块", "接口", "博客", "网站",
    "迁移", "migration", "备份", "同步",
    "拖拽", "拖动", "排序", "drag", "音效",
    "开发", "develop", "新功能", "实现", "部署",
    "删除", "擦除", "清除", "格式化", "重置", "drop", "rm", "erase", "wipe", "destroy",
    "参数", "阈值", "magic number", "配置", "常量", "硬编码",
    "自举", "bootstrap", "迭代",
    "多池", "降级", "供应商", "路由",
    "heap", "NVS", "flash", "缓冲区", "内存",
    "模型调用", "API调用",
    "代码", "函数", "组件", "模块", "框架",
    "撤销", "undo",
    "设计",
    # E-series additions
    "git", "push", "仓库", "CI", "CD", "workflow", "打包",
    "上下文", "context", "会话", "session",
    "测试", "test", "fixture", "自检", "截图",
    "IDE", "混淆", "构建", "键位",
    "机器人", "bot", "Token", "心跳",
    "特效", "effect", "关键帧", "动画", "animation",
    "光照", "light", "阴影", "shadow", "光场",
    "导出", "export", "ffmpeg", "渲染", "render",
    "SFX", "工具栏", "toolbar", "资源库", "素材",
    "陪伴", "companion", "主动消息", "表达欲",
    "SSE", "delta", "stream", "流式",
    "BLE", "蓝牙", "WiFi配网", "分区方案",
]

def execute(ctx: dict) -> dict:
    ctx["_domain_routed"] = True
    return ctx

node = Node(
    id="B00", name="工程域",
    trigger={"type": "keyword", "target": "task",
             "keywords": KEYWORDS,
             "unless": "_domain_routed"},
    execute=execute,
    refs=["135", "010", "600", "610", "620",
          "170", "180", "360", "370", "390", "395", "400",
          "420", "480", "490", "500", "520", "530", "540",
          "550", "560", "580", "220", "440", "510",
          "E00", "E01", "E02", "E03", "E04", "E05", "E06",
          "E10", "E11", "E20", "E21", "E22",
          "640", "650", "661", "662", "663", "664", "665",
          "710", "740", "750", "900", "902", "904", "905",
          "950", "972", "975", "976", "977",
          "E30", "E31", "E32", "E33"],
    metadata={"category": "domain", "layer": "abstraction"})
