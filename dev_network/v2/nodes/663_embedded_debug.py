"""知识节点：嵌入式调试模式——从ESP32系列fix记录提炼的资源受限调试方法。

来源：GLM-5 fix 005-009（ESP32相关）+ Opus4.6 fix 001-007（嵌入式Web服务）

嵌入式核心约束：
  - RAM极度紧张（ESP32C3约150KB可用）
  - 无动态分析工具（无valgrind/sanitizer）
  - 重启成本高（重新建立WiFi+WebSocket连接）
  - 日志只能串口输出（带宽有限）

资源受限调试策略：
  - 静态分配消碎片——所有网络对象改static成员，unload只disconnect不delete
  - 栈溢出防护——static char缓冲区替代栈上分配
  - Flash存储替代RAM——对话历史等大数据写Flash流式读取
  - 重连逻辑必须独立于对象生命期——不依赖对象是否为null
  - Token刷新必须主动——解析expires_in+记录获取时间+定时刷新

内存计算模板：
  总RAM约150KB - 网络静态对象约96KB = 剩余约54KB
  String历史最大约50KB ≈ 12K-20K tokens（中文）
  远小于API支持的200K tokens → 必须用Flash扩展
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")

    verdict = ask(
        system="你是嵌入式系统判断助手。",
        user=f"任务：{task}\n\n这个任务是否涉及嵌入式或资源受限环境？"
             "（ESP32/Arduino/STM32/IoT/内存限制/Flash存储）回答是或否。",
        max_tokens=30
    )

    if "是" in verdict:
        ctx.setdefault("_design_principles", []).extend([
            "静态分配消碎片——一次分配运行时永不释放",
            "unload只断连不delete——保持对象存活避免碎片",
            "栈上大缓冲区改static——防嵌套栈溢出",
            "大数据用Flash流式读写——RAM存不下就用外存",
            "重连逻辑独立于对象——不依赖指针是否null",
            "Token必须主动刷新——解析expires_in+定时更新",
            "ESP.getMaxAllocHeap()诊断碎片——最大连续块<16KB=SSL握手失败",
        ])

    return ctx


node = Node(id="663", name="嵌入式调试模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["ESP32", "嵌入式", "embedded", "Arduino", "内存",
                          "Flash", "RAM", "碎片", "IoT"]},
    execute=execute, refs=["600", "660"],
    metadata={"source": "Agent/GLM-5 fix005-009+Opus4.6 fix001-007(ESP32系列)", "category": "methodology"})
