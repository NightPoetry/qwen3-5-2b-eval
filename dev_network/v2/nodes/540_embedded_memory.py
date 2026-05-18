"""知识节点：嵌入式内存管理——静态分配/Flash替代RAM/TLS连接策略。

融合：esp32-embedded-patterns + ESP32C3静态分配方法论 + TLS连接复用评估
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

MEMORY_KNOWLEDGE = """你是嵌入式内存管理专家。根据以下知识诊断内存相关问题。

## 三种分配方式对比
- 堆(new/delete)：动态随时分配，碎片风险高——应避免
- 栈(局部变量)：函数调用时分配，无碎片但空间有限(4-8KB)——仅小缓冲<1KB
- 静态(static)：启动时分配永不释放，零碎片——网络对象和缓冲区首选
- Flash(文件)：文件系统存储，无碎片——大数据首选

## 网络对象必须静态化
- WiFiClientSecure每次new/delete产生16KB碎片→第二次分配失败→HTTP -1
- 正确做法：static WiFiClientSecure _client，启动时分配永久占用
- SSL握手需约16KB连续内存+4KB RX+4KB TX=约24KB
- client.stop()清理连接状态但不释放内存——复用已分配的对象

## Flash替代RAM
- 对话历史存Flash而非RAM：Flash可存几MB支持200K+tokens，RAM只能50KB约12K tokens
- HTTP请求体分段写Flash，发送时从Flash流式读取→内存占用从50KB+降到512字节
- 绕过HTTPClient用WiFiClientSecure直接流式写：分块发送body，512字节缓冲无限大小
- 临时String用完立即清空("")释放——不要持有到函数返回

## TLS Keep-Alive评估（弊大于利）
- TLS连接保持占约20KB常驻内存（从83KB降到63KB）
- 中间层(穿透/反代)有自己的超时，连接大概率被对端关闭
- Stale检测不可靠：TCP层写入成功但数据可能丢失(RST延迟)
- 结论：RAM<100KB设备上TLS keep-alive弊大于利，恢复Connection:close

## 消息合并替代连接复用
- 用户高频发多条消息时：等AI处理完第一条后poll WebSocket收积压消息
- 一次LLM调用处理多条消息(B+C在sliding_chat中)→给出整合回复
- 省下多次TLS握手开销，且回复质量更高（看到完整意图）

## 设计原则
- 网络对象必须静态——启动时分配永不释放
- 缓冲区必须静态——避免栈溢出和碎片
- 大数据必须Flash——对话历史、请求体存文件
- NVS键名最长15字节值最大~4000字节——不适合存文件内容
- NVS频繁写入缩短flash寿命——秒级写入是反模式
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        MEMORY_KNOWLEDGE +
        "\n分析以下任务涉及的嵌入式内存问题，给出具体建议（每条一行，不超过4条）。"
        "如果不涉及内存问题，回答'无内存问题'。",
        f"任务：{task[:500]}",
        max_tokens=250
    ).strip()
    if "无内存问题" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    return ctx

node = Node(id="540", name="嵌入式内存管理",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["ESP32", "heap", "内存", "NVS", "flash", "缓冲区",
                          "嵌入式", "碎片", "静态分配", "static", "TLS",
                          "SSL", "WiFiClientSecure", "内存不足", "OOM"]},
    execute=execute, refs=["360"],
    metadata={"source": "Guild/嵌入式与硬件开发/静态分配+TLS评估+内存优化", "category": "domain_embedded"})
