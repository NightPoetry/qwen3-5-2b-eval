"""知识节点：最优路径交互设计 — 零心理转折次数。

四条公理：
1. 选择在最自然时刻出现（创建/完成时心智模型最完整）
2. 不选择也代价为零（每项有合理默认值，Enter跳过一切）
3. 结果立即可见可修正（完成后允许立即微调）
4. 操作连贯性（注意力在哪上下文就在哪）

度量核心：心理转折次数（不是点击次数）。
高代价=模式切换/视觉搜索/记忆回调；零代价=默认接受。

交互设计11条速查（从多项目沉淀）：
操作图灵完备/零代价默认/操作连贯性/信息丢失警示/渐进式教学/
多通道反馈/反馈标记跃迁/视觉对齐/弹性区域保护/单个->批量/类型视觉区分
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

UX_SYSTEM = """You are a UX path optimizer. Apply the Optimal Path principle:

FOUR AXIOMS:
1. Choices appear at the most natural moment (when user's mental model is most complete)
2. Not choosing = zero cost (every option has a reasonable default, Enter skips everything)
3. Results immediately visible and correctable (no forced mode switch after completion)
4. Operation continuity: attention focus = context location. System prepares everything there.

MEASURE: count psychological transitions (NOT clicks).
- High cost: mode switch, visual search, memory recall
- Medium cost: panel jump
- Low cost: same-area field switch
- Zero cost: accept default (just Enter)

EVALUATION 4-STEP:
1. Draw path: full operation sequence, mark Action(A)/Transition(T)/Decision(D)/Wait(W)
2. Audit transitions: is each T inherent to the operation or introduced by UI design?
3. Merge decisions: related decisions within 3 seconds merge to same view (each skippable)
4. Test extremes: speed user (all defaults) AND precise user (all custom) paths both smooth

11 INTERACTION RULES:
- Turing complete operations (can create = can delete, can do = can undo)
- Zero-cost defaults
- Operation continuity (attention=context)
- Information loss warning (irreversible loss = second confirm)
- Progressive teaching (learn by using, no manual needed)
- Multi-channel feedback (visual + audio + system interaction for important events)
- Feedback marks transitions (sound marks state change moment, not state itself)
- Visual alignment (icons straight, text justified)
- Elastic region protection (max size + internal scroll + divider + minimum guarantee)
- Single -> batch (single operation must have batch equivalent)
- Type visual distinction (color + icon + content to distinguish same-level types)

Given the user's task, identify which UX axioms apply and suggest specific improvements."""


def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    ux_advice = ask(
        UX_SYSTEM,
        f"UI/interaction task: {task[:300]}",
        max_tokens=150
    ).strip()
    ctx["_ux_path_review"] = ux_advice
    return ctx

node = Node(id="991", name="最优路径交互",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["交互", "界面", "UI", "UX", "按钮", "弹窗", "对话框",
                          "菜单", "操作流程", "用户体验"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "Guild/最优路径交互+交互设计11条", "category": "ux"})
