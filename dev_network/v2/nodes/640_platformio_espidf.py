"""知识节点：PlatformIO+ESP-IDF开发——构建/上传/分区/框架迁移/串口。

适用于使用PlatformIO构建ESP-IDF项目、分区配置、固件上传的任务。
来源：platformio-espidf
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

PIO_KNOWLEDGE = """你是PlatformIO+ESP-IDF构建专家。根据以下知识诊断构建问题。

## 构建与上传
- pio run编译，pio run --target upload刷固件，pio run --target uploadfs上传文件系统镜像
- --target upload只刷固件分区，不影响文件系统分区（LittleFS/SPIFFS数据保留）
- --target uploadfs会用data/目录重建并覆盖整个文件系统分区，运行时写入的数据丢失
- 运行时更新单个文件应通过HTTP API上传，不需要重刷文件系统

## 分区表
- board_build.partitions指定自定义分区表CSV
- no_ota方案把OTA空间全给APP和数据分区，代价是不能空中升级
- Flash大小警告"Expected 4MB, found 2MB"通常是sdkconfig默认值与实际芯片不匹配

## 框架迁移（Arduino到ESP-IDF）
- Arduino的WebServer类内部自动URL解码，迁移到ESP-IDF后必须手动处理
- Arduino的SPIFFS.begin()/LittleFS.begin()等价于ESP-IDF的esp_vfs_littlefs_register()，但API完全不同
- ESP-IDF使用标准C文件操作（fopen/fread/opendir），Arduino使用File类和fs::FS抽象
- 迁移时原框架自动做的事（URL解码、Content-Type推断、路径规范化）在新框架中需手动实现

## 版本对应
- PlatformIO espressif32@6.9.0对应ESP-IDF 5.3.1

## 串口监控
- USB CDC模式下端口名/dev/cu.usbmodem*，每次重启可能变化
- 用pyserial读串口比cat /dev/cu.usbmodem*更可靠，后者在设备重启时会挂起
"""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        PIO_KNOWLEDGE +
        "\n分析以下任务涉及的PlatformIO/ESP-IDF问题，给出具体建议（每条一行，不超过5条）。"
        "如果不涉及PlatformIO构建问题，回答\"无PIO构建问题\"。",
        f"任务：{task[:600]}",
        max_tokens=300
    ).strip()

    if "无PIO构建问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx


node = Node(id="640", name="PlatformIO构建",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["platformio", "pio", "esp-idf", "分区表", "partition",
                          "uploadfs", "sdkconfig", "espressif32", "Arduino迁移",
                          "串口", "serial", "usbmodem"]},
    execute=execute, refs=["360"],
    metadata={"source": "knowledge/platformio-espidf", "category": "domain_embedded"})
