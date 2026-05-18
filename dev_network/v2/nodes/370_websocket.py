"""知识节点：WebSocket长连接模式——token生命周期/重连策略/session恢复。

适用于涉及WebSocket、长连接、实时通信的任务。
融合：websocket-long-connection
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

WS_KNOWLEDGE = """你是WebSocket长连接专家。根据以下知识评估任务中的连接管理风险。

## Token生命周期
- 带token鉴权的WebSocket，token过期是最常见断线原因——连接本身没问题，服务器因鉴权失败主动断开
- token刷新应在过期前提前执行（预留margin），非等断开后再刷新
- 必须记录token获取时间和有效期，仅靠"能否成功请求"判断过期不可靠（网络错误和鉴权错误混淆）

## 重连策略
- 库内置自动重连通常只处理TCP层，不处理应用层token刷新、session恢复
- 重连前按依赖顺序：刷新token → 获取新endpoint → 建立连接 → 发送鉴权/恢复
- 指数退避（5s→10s→20s→60s cap），成功后立即重置延迟
- 重连触发不能依赖"指针为null"或"对象未初始化"——静态分配对象永远不为null，应直接检查连接状态枚举

## Session Resume vs Full Reconnect
- 很多协议支持session resume：断线后用session_id+最后seq恢复，跳过初始化握手
- resume失败时必须回退到完整连接流程，不能无限重试resume
- session有有效期，长时间断线后session可能已被服务器清除

## 嵌入式设备特殊考虑
- millis()溢出（约49.7天）导致基于时间差的心跳计算错误，用无符号减法天然处理单次溢出
- 低内存设备SSL占约20KB/连接，HTTP token刷新和WebSocket不能同时持有两个SSL上下文
"""

WS_TEMPLATE = """
// WebSocket 连接管理模板（含token刷新和指数退避）
class WS {
  constructor(url, getToken) {
    this.url = url;
    this.getToken = getToken;
    this.retryDelay = 1000;
    this.maxRetry = 60000;
    this.queue = [];
    this.sessionId = null;
    this.lastSeq = 0;
    this.connect();
  }
  async connect() {
    const token = await this.getToken();
    this.ws = new WebSocket(this.url + '?token=' + token);
    this.ws.onopen = () => {
      this.retryDelay = 1000;
      if (this.sessionId) this.send({type:'resume', sid: this.sessionId, seq: this.lastSeq});
      this.flush();
    };
    this.ws.onclose = (e) => {
      if (e.code === 4001) this.sessionId = null; // invalid session, full reconnect
      setTimeout(() => this.connect(), this.retryDelay = Math.min(this.retryDelay * 2, this.maxRetry));
    };
    this.ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.seq) this.lastSeq = msg.seq;
      if (msg.sid) this.sessionId = msg.sid;
      this.onMessage(msg);
    };
  }
  send(data) {
    if (this.ws?.readyState === 1) this.ws.send(JSON.stringify(data));
    else this.queue.push(data);
  }
  flush() { while (this.queue.length) this.send(this.queue.shift()); }
  onMessage(data) { /* override */ }
}
"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        WS_KNOWLEDGE +
        "\n分析以下任务涉及的WebSocket风险点，给出具体建议（每条一行，不超过5条）。"
        "如果不涉及长连接风险，回答'无长连接风险'。",
        f"任务：{task[:600]}",
        max_tokens=250
    ).strip()

    if "无长连接风险" not in result:
        ctx.setdefault("_domain_rules", []).append(result)
    ctx.setdefault("_inject_js", []).append(WS_TEMPLATE)
    return ctx

node = Node(id="370", name="WebSocket模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["websocket", "ws", "长连接", "实时", "推送", "socket",
                          "token刷新", "重连", "reconnect", "session"]},
    execute=execute, refs=["Y20"],
    metadata={"source": "knowledge/websocket-long-connection", "category": "domain_network"})
