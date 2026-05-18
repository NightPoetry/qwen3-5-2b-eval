"""知识节点：防御性布局 — 任何显示条件下保持结构完整。

核心：布局首要职责是在任何显示条件下保持结构完整，不是仅在理想条件下好看。
"不坏"是比"好看"更基础的要求。

布局意义上的"坏"=功能性失效：
- 关键元素被遮住（字数统计被footer压住）
- 操作按钮被挤出视口（无法点击）
- 内容溢出容器边界（破坏整体结构）
- 文字截断但没有提示（用户以为信息完整）

设计判断标准：不是"在我屏幕上好不好看"，而是"可用空间减半会发生什么"。

快速排查：
1. 找最近flex-col祖先，确认有高度约束
2. flex-1子项是否同时有minHeight->去掉或改min-h-0
3. "被遮住"元素是否在可收缩区域底部->移到flex-shrink-0的footer
4. 固定宽度是否用px硬编码->改min(Npx,100vw)
5. 横向按钮组右侧是否有flex-shrink-0
"""
import re
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


def execute(ctx: dict) -> dict:
    """检查CSS/HTML中的防御性布局问题。"""
    css = ctx.get("css", "")
    html = ctx.get("html", "")
    issues = []

    if css:
        # 检查flex-1和minHeight同时使用
        if "flex: 1" in css or "flex-1" in css:
            if "min-height:" in css and "min-height: 0" not in css:
                if "min-h-0" not in css:
                    issues.append(
                        "flex-1与min-height同时使用——空间不足时容器会溢出。"
                        "去掉min-height或改为min-height:0"
                    )

        # 检查固定宽度硬编码
        fixed_widths = re.findall(r'width:\s*(\d{3,})px', css)
        for w in fixed_widths:
            if int(w) > 300:
                issues.append(
                    f"固定宽度{w}px可能在小屏/高缩放下超出视口——"
                    f"建议改为min({w}px, 100vw)"
                )

    if html:
        # 检查type=number（原生spinner泄漏）
        if 'type="number"' in html or "type='number'" in html:
            issues.append(
                'type="number"会显示浏览器原生spinner——'
                '改用type="text" inputMode="numeric"或CSS隐藏spinner'
            )

    if issues:
        ctx.setdefault("_architecture_review", []).extend(issues)

    return ctx

node = Node(id="E31", name="防御性布局检查",
    trigger={"type": "key_exists", "key": "css"},
    execute=execute, refs=["993"],
    metadata={"source": "Guild/防御性布局+Flex防溢出+原生样式隔离", "category": "code_quality"})
