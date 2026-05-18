"""
知识路由器 — 网状组织，邻接可见。

核心模型：
  你站在一个节点上，只看得到邻接节点。
  系统判断邻接节点的触发条件是否被当前内容满足。
  满足 → 走过去，应用该卡，然后从新位置看邻接。
  不满足 → 不走，那个方向对当前内容不可见。

为什么不需要深度限制：
  触发条件本身是自然停止条件。
  环不会无限循环——visited集合记录已到过的节点。
  走过的不再走，不是"深度限制"而是"已经用过了"。

为什么是网不是树：
  知识之间有循环引用和交叉引用。
  003(最少决定) ↔ 009(可逆不弹确认) — confirm就是一种决定
  001(flex防溢出) ↔ 010(文本溢出) — 都是边界可控
  循环 = 迭代精化能力（图灵完备的组成部分）
"""

import json
import re
from pathlib import Path

CARDS_DIR = Path(__file__).parent / "knowledge_cards"

# Phase → 入口节点的标签（从哪些节点开始看）
PHASE_ENTRY = {
    "phase0": ["phase0_post"],
    "phase1": [],
    "phase2": ["architecture"],
    "phase3_html": ["html_css_validation"],
    "phase3_css": ["css_validation", "css_generation", "html_css_validation"],
    "phase3_js": ["js_generation", "js_validation"],
    "phase4": ["html_css_validation", "css_validation", "js_validation"],
}


def load_all_cards() -> dict[str, dict]:
    """加载所有知识卡，以ID为key。"""
    cards = {}
    for f in sorted(CARDS_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            card = json.load(fh)
            cards[card["id"]] = card
    return cards


def _triggered(card: dict, content: str) -> bool:
    """判断一张卡的触发条件是否被当前内容满足。"""
    trigger = card.get("trigger", {})
    t = trigger.get("type", "")

    if t == "always":
        return True
    elif t == "regex":
        pattern = trigger.get("pattern", "")
        return bool(pattern and re.search(pattern, content))
    elif t == "keyword":
        return any(kw in content for kw in trigger.get("keywords", []))
    elif t in ("count", "pattern", "element_analysis"):
        return True
    return False


def walk(phase: str, content: str) -> list[dict]:
    """
    从Phase入口出发，沿触发的边行走。

    行走规则：
      1. Phase过滤确定入口节点集合
      2. 入口节点中，触发条件满足的 → 激活
      3. 被激活节点的邻接(refs) → 检查触发条件
      4. 满足 → 走过去（激活），继续看它的邻接
      5. 不满足 → 不走（不可见）
      6. 已走过的 → 不再走（visited）

    返回: 所有被激活的卡（按激活顺序）
    """
    entry_tags = PHASE_ENTRY.get(phase, [])
    if not entry_tags:
        return []

    all_cards = load_all_cards()

    # 入口：Phase标签匹配 + 触发满足
    frontier = []
    for card in all_cards.values():
        if card.get("phase") in entry_tags and _triggered(card, content):
            frontier.append(card["id"])

    # 行走
    visited = set()
    activated = []

    while frontier:
        card_id = frontier.pop(0)

        if card_id in visited:
            continue
        visited.add(card_id)

        card = all_cards.get(card_id)
        if not card:
            continue

        activated.append(card)

        # 看邻接：refs中触发条件满足的才走
        for ref_id in card.get("refs", []):
            if ref_id not in visited:
                ref_card = all_cards.get(ref_id)
                if ref_card and _triggered(ref_card, content):
                    frontier.append(ref_id)

    return activated


def get_active_rules(phase: str, content: str) -> list[dict]:
    """供验证器消费：返回被激活的确定性规则。"""
    return [
        {"id": c["id"], "name": c["name"], "steps": c.get("steps", [])}
        for c in walk(phase, content)
        if c.get("deterministic", False)
    ]


def visualize_graph() -> str:
    """可视化知识图拓扑 + 环检测。"""
    all_cards = load_all_cards()
    lines = ["=== 知识网络拓扑 ===\n"]

    for card_id, card in sorted(all_cards.items()):
        refs = card.get("refs", [])
        refs_display = ", ".join(refs) if refs else "(无邻接)"
        lines.append(f"  [{card_id}] {card['name']} → {refs_display}")

    lines.append("\n=== 双向环（互相引用） ===")
    found_cycle = False
    for card_id, card in all_cards.items():
        for ref_id in card.get("refs", []):
            ref_card = all_cards.get(ref_id)
            if ref_card and card_id in ref_card.get("refs", []):
                if card_id < ref_id:  # 避免重复打印
                    lines.append(
                        f"  [{card_id}]{card['name']} ↔ [{ref_id}]{ref_card['name']}"
                    )
                    found_cycle = True
    if not found_cycle:
        lines.append("  (无双向环)")

    return "\n".join(lines)


if __name__ == "__main__":
    print(visualize_graph())

    print("\n\n=== 行走测试 ===\n")

    # CSS阶段：flex:1 触发001，001邻接010（文本溢出），010是否触发取决于content
    test_css = ".sidebar { flex: 1; }\n.item span { width: 200px; }"
    print(f"Phase: phase3_css")
    print(f"Content: flex:1 + 固定宽度span\n")
    cards = walk("phase3_css", test_css)
    for c in cards:
        print(f"  [{c['id']}] {c['name']} (邻接: {c.get('refs', [])})")
    print(f"\n  激活 {len(cards)} 张卡")

    # JS阶段：confirm() 触发009，009邻接003和006
    # 003的trigger是count类型（phase0_post阶段），但当前是JS阶段
    # 所以003不在入口集 → 但它被009的ref拉过来 → 检查触发 → count类型返回True → 激活
    print(f"\n\nPhase: phase3_js")
    print(f"Content: confirm('删除?')\n")
    test_js = "if(confirm('确定删除?')) { items.splice(i,1); }"
    cards = walk("phase3_js", test_js)
    for c in cards:
        print(f"  [{c['id']}] {c['name']} (邻接: {c.get('refs', [])})")
    print(f"\n  激活 {len(cards)} 张卡")
    print(f"  注意：003(最少决定)通过009的ref被拉入——跨Phase的邻接也是可见的")
