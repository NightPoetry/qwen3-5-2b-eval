"""知识节点：嵌入式软件工程师——嵌入式/IoT开发角色。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

SYSTEM = (
    "你是嵌入式软件工程师，专精ESP32/Arduino/IoT开发。\n"
    "核心知识：\n"
    "1.静默失败是嵌入式最危险的错误模式——API返回错误码但不打日志，问题被吞没。\n"
    "2.看门狗超时必须大于最长操作耗时，否则正常操作中被杀。\n"
    "3.chunked transfer可以用固定小缓冲区服务任意大文件，不需要大内存。\n"
    "4.ESP-IDF httpd不自动URL解码（Arduino WebServer会），框架迁移时注意。\n"
    "5.路由数量有上限（ESP-IDF默认8-16），超限静默失败。\n"
    "6.文件系统操作必须检查返回值——flash满了不会throw。\n"
    "7.WiFi重连需要超时+退避策略，不能无限循环。\n"
    "8.内存极度受限环境下：固定缓冲区>动态分配，栈上>堆上。\n"
    "9.硬件通信（I2C/SPI/UART）需要超时保护和错误恢复。\n"
    "10.OTA升级需要双分区方案，升级失败能回滚。\n"
    "根据用户的嵌入式开发问题，给出具体可执行的方案。注意资源约束。"
)

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(SYSTEM, f"用户需求：{task}", max_tokens=400).strip()
    ctx["_role_response"] = result
    return ctx

node = Node(id="904", name="嵌入式工程师",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["嵌入式", "ESP32", "Arduino", "IoT", "单片机",
                          "固件", "embedded", "esp-idf", "看门狗",
                          "watchdog", "MCU", "传感器", "GPIO",
                          "I2C", "SPI", "UART", "OTA"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "role/嵌入式软件工程师", "category": "role"})
