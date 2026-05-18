"""知识节点：注意力看门狗——检测模型输出失控重复。

核心原理（结构性，非工程性）：
- 模型有能力注意到重复时就不会重复；开始重复说明注意力已涣散
- 让模型自己检测注意力在不在原理上不可能——自指闭锁
- 看门狗价值是永久的结构性的，不是算力不够的临时方案

三层探针联动：
  1. 数字层：计数Tag序号是否单调
  2. 结构层：Tag闭合符/字段完整性（实测主要信号是结构层塌陷，非数字层）
  3. 行为层：滚动4-gram重复率（最近600词，阈值0.30）

三档失败梯度：
  微弱（损坏出现且间隔大）→ 仅记录
  加速（间隔持续缩短EMA下降）→ 注入提示不截断
  严重（数字乱/重复>50%）→ 截断+reset（新请求，不复用旧KV cache）

介入判断：仅"行为层+至少一个其他层"才介入（纯文本重复但Tag正常=可控重复）
同会话reset硬上限3次，超过则终止任务。

融合：watchdog-empirical
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def _ngram_repeat_rate(text, n=4, window=600):
    """滚动n-gram重复率。窗口太大冲淡早期信号，太小噪声大。"""
    words = text.split()[-window:]
    if len(words) < n:
        return 0.0
    ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    unique = len(set(ngrams))
    return 1.0 - (unique / len(ngrams)) if ngrams else 0.0


def _check_structure_collapse(content):
    """结构层探针：检测Tag闭合符丢失或字段名消失。
    实测：失控时Tag数字层可能始终单调，真信号是结构层塌陷。
    """
    # 检测well-formed vs malformed计数Tag（如<wd:N>正常 vs <wd:N后非>非数字）
    well_formed = len(re.findall(r'<wd:\d+>', content))
    malformed = len(re.findall(r'<wd:\d+(?![\d>])', content))
    return malformed, well_formed


def execute(ctx: dict) -> dict:
    """检查模型输出是否有失控重复信号。三层联动判断。"""
    for key in ("raw_html", "raw_css", "raw_js"):
        content = ctx.get(key, "")
        if not content or len(content) < 200:
            continue

        alerts = []
        behavior_alert = False
        structure_alert = False

        # 行为层：n-gram重复率
        repeat_rate = _ngram_repeat_rate(content)
        if repeat_rate > 0.5:
            alerts.append(f"严重：{key} n-gram重复率{repeat_rate:.0%}，模型输出可能失控")
            behavior_alert = True
        elif repeat_rate > 0.3:
            alerts.append(f"警告：{key} n-gram重复率{repeat_rate:.0%}，注意力可能涣散")
            behavior_alert = True

        # 结构层：Tag闭合和标签平衡
        malformed, well_formed = _check_structure_collapse(content)
        if malformed > 0 and well_formed > 0:
            alerts.append(f"结构层：{key} 检测到{malformed}个畸形Tag（共{well_formed}个正常Tag）")
            structure_alert = True

        if key == "raw_html":
            opens = len(re.findall(r'<[a-z][\w-]*[^/]>', content))
            closes = len(re.findall(r'</[a-z][\w-]*>', content))
            if opens > 0 and abs(opens - closes) > opens * 0.3:
                alerts.append(f"结构层：{key} 标签开闭不平衡(开{opens}/闭{closes})")
                structure_alert = True

        # 联动判断：仅"行为层+至少一个其他层"才真正介入
        # 纯行为层（Tag正常）= 可能是用户要求的可控重复
        if behavior_alert and structure_alert:
            ctx.setdefault("_watchdog_alerts", []).extend(alerts)
            ctx.setdefault("_watchdog_action", []).append(
                f"{key}: 行为层+结构层联动触发，建议截断+注入新信息重分布注意力"
            )
        elif behavior_alert and repeat_rate > 0.5:
            # 极高重复率即使无结构异常也应警告
            ctx.setdefault("_watchdog_alerts", []).extend(alerts)
        elif structure_alert:
            # 纯结构异常记录但不截断
            ctx.setdefault("_watchdog_alerts", []).extend(alerts)

    return ctx


node = Node(id="460", name="注意力看门狗",
    trigger={"type": "key_exists", "key": "raw_js"},
    execute=execute, refs=["350"],
    metadata={"source": "knowledge/watchdog-empirical", "category": "safety"})
