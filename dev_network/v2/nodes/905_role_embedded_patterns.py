"""知识节点：嵌入式开发模式库——硬件交互与资源约束下的工程模式。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

EMBEDDED_PATTERNS = [
    "静默失败防御：所有API调用必须检查返回值并打日志，esp_err_t不为ESP_OK就记录",
    "看门狗设置：超时=最长操作耗时*2+安全余量，长操作前喂狗或临时延长超时",
    "内存管理：优先栈上固定缓冲区，避免频繁malloc/free导致碎片化",
    "chunked HTTP服务：固定小缓冲区(1-4KB)分块发送，服务任意大文件",
    "ESP-IDF路由上限：默认8-16个，超限静默失败，需在menuconfig中调大或动态注册",
    "WiFi重连策略：指数退避(1s→2s→4s→8s→max30s)+最大重试次数+状态LED指示",
    "文件系统安全：SPIFFS/LittleFS写入前检查剩余空间，写入后验证，flash满不会throw",
    "I2C通信保护：设置超时，失败后reset总线(SDA/SCL toggle)，重试最多3次",
    "SPI设备共享：使用mutex保护总线，每次通信前设置正确的CS和时钟参数",
    "UART收发：用DMA或中断+环形缓冲区，避免忙等浪费CPU",
    "OTA双分区：A/B分区方案，升级写入备用分区，验证通过后切换启动分区",
    "电源管理：深睡眠模式+RTC唤醒，传感器采集完立即休眠",
    "时间同步：NTP校时+RTC保底，网络不可用时RTC维持时间",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(EMBEDDED_PATTERNS)
    return ctx

node = Node(id="905", name="嵌入式模式库",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["嵌入式模式", "硬件模式", "ESP32模式",
                          "chunked", "看门狗配置", "OTA升级",
                          "深睡眠", "WiFi重连", "SPIFFS"]},
    execute=execute, refs=["904"],
    metadata={"source": "role/嵌入式软件工程师/knowledge", "category": "role"})
