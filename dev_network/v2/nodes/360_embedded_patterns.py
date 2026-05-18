"""知识节点：嵌入式开发模式——内存管理/HTTP服务/文件系统/静默失败。

适用于涉及MCU、嵌入式、IoT的任务。
融合：esp32-embedded-patterns / esp-idf-filesystem / esp-idf-http-server
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

EMBEDDED_KNOWLEDGE = """你是嵌入式系统专家。根据以下知识判断任务涉及哪些嵌入式风险点，给出具体建议。

## 内存管理
- MCU可用heap通常不到100KB，单次分配超4KB应审视必要性
- 长生命周期对象应启动时静态分配一次、永不释放，避免heap碎片化
- TLS连接占约20KB heap，低内存设备用Connection:close策略
- 多个顺序执行模块可共享同一块工作缓冲区（不并发访问时安全）
- 流式处理（边读边写，固定小缓冲区）是低内存设备处理大数据的唯一正确方式
- 不同用途缓冲区应分离（工作缓冲区和上传缓冲区），避免长操作独占

## HTTP服务
- max_uri_handlers是硬上限，超出后注册静默失败返回错误码（不崩溃不打日志），表现为404
- 新增路由后出404，优先检查handler上限是否够用
- 通配符路由必须注册在具体路由之后，否则吞掉精确匹配
- httpd_query_key_value()不做URL解码，前端encodeURIComponent的参数后端必须手动解码
- 所有handler在同一线程顺序执行，共享全局buffer不需加锁，但慢handler阻塞全部请求
- chunked传输可用固定小缓冲区服务任意大文件

## 文件系统
- LittleFS支持真目录结构，SPIFFS不支持（平坦路径模拟）
- opendir返回NULL可能是路径不存在、不是目录、或URL编码未解码导致路径含%2F
- fopen要求父目录已存在，需先递归创建
- 大文件写入必须边接收边写（streaming），不整体读入内存
- 分区标签可叫spiffs但实际用LittleFS格式化，只是注册函数不同

## URL编码
- 就地URL解码安全（解码后长度<=原始长度）
- 必须处理%XX和+两种编码
- 中文经UTF-8后每字3字节，再URL编码变9字节

## 静默失败模式
- 嵌入式框架很多配置项是硬上限，超出后静默失败而非崩溃
- 每次新增消耗配额的资源（路由、连接、定时器），应检查上限配置是否充足
- 静默失败的API调用应主动检查返回值并打日志

## 框架迁移
- 从高层框架迁移到低层框架时，最易遗漏原框架隐式自动做的事：URL解码、Content-Type推断、路径规范化
- 迁移后应逐一测试含特殊字符的输入（/、空格、中文、+、%）

## BLE配网与卸载
- BLE仅用于首次WiFi配置，配置完成后立即卸载释放约55KB内存
- BLE通知机制：Characteristic必须添加BLE2902 descriptor才支持通知
- 断开后必须重新启动广播(pAdvertising->start())，否则新客户端无法发现
- 新连接必须重置认证状态，所有敏感操作先认证
- WiFi配置保存到NVS，重启后自动连接
- WiFi连接必须设超时(15秒)，避免无限等待
- BLE配置成功需客户端确认收到IP后再卸载BLE（IP_CONFIRMED协议）

## 分区方案选择
- ESP32C3 no_ota方案：2MB程序+2MB文件系统，适合无OTA的嵌入式项目
- huge_app方案：3MB程序+1MB文件系统，最大程序空间
- 程序空间不足(>100%)选no_ota(2MB)或huge_app(3MB)
- 分区标签可叫spiffs但实际可用LittleFS格式化
- 自定义分区用CSV文件，PartitionScheme=custom

## 流式网络处理
- HTTP流无法暂停：停止读取30秒可能触发超时断连
- 正确顺序：接收AI流→关闭AI SSL(释放20KB)→打开发送SSL→发送
- 不能同时开两个SSL连接：内存从92KB→34KB→HTTP -1
- 接收用固定1KB缓冲区，凑够完整句子+回车就发送，超1KB强制发送
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        EMBEDDED_KNOWLEDGE +
        "\n任务描述如下，列出涉及的风险点和具体建议（每条一行，不超过5条）。"
        "如果任务不涉及嵌入式风险，回答'无嵌入式风险'。",
        f"任务：{task[:600]}",
        max_tokens=300
    ).strip()

    if "无嵌入式风险" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="360", name="嵌入式模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["ESP32", "嵌入式", "Arduino", "IoT", "单片机", "固件",
                          "embedded", "esp-idf", "看门狗", "watchdog", "MCU",
                          "LittleFS", "SPIFFS", "httpd", "分区", "flash",
                          "BLE", "蓝牙", "WiFi配网", "NVS", "分区方案",
                          "SSL", "TLS", "流式", "streaming"]},
    execute=execute, refs=["540"],
    metadata={"source": "knowledge/esp32+Guild/嵌入式与硬件开发", "category": "domain_embedded"})
