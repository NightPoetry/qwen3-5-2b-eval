"""知识节点：工程健壮性模式——流式空闲超时、前端防御性检查清单。

从开发方法论实践中提炼的防御性工程模式：
  - 空闲超时策略：流式请求用空闲超时替代固定超时，区分"处理中"和"真正断开"
  - 前端四维检查：溢出(overflow) + 裁剪(clipping) + 滚动条(scrollbar) + 切换(toggle)
  - 竞态条件防御：快速连续操作的防抖节流、异步操作返回顺序
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node
from llm import ask

ROBUSTNESS_PRINCIPLES = """你是工程健壮性设计顾问。基于以下经过验证的设计模式回答问题。

## 流式请求空闲超时策略
- 问题：思考类大模型先输出思考过程再输出答案，传统固定超时会误断
- 核心洞察：模型不是卡住，而是持续输出数据
- 方案：空闲超时检测——只有长时间没收到任何数据才判定为超时
- 实现：每次读取数据块时设置超时，收到数据重置计时器
- 效果：思考30秒后输出→正常完成；网络真断→空闲超时后判定
- 推广场景：大文件上传下载、数据库批量操作、视频转码等待

## 前端溢出检查(Overflow)
- 容器溢出：flex/grid容器因内容过长导致布局崩坏
- 文字溢出：长文本/动态内容撑开容器
- 测试方法：空数据、正常数据、极端长数据，多尺寸响应式
- 修复：overflow:hidden + text-overflow:ellipsis，或多行截断(-webkit-line-clamp)

## 前端裁剪检查(Clipping)
- overflow:hidden误用：导致下拉菜单/弹窗/Tooltip被裁剪
- z-index层级问题：高层级被低层级容器的overflow裁剪
- transform创建新层叠上下文：影响fixed/sticky定位
- 修复：position:fixed或Portal将弹层渲染到body

## 滚动条检查(Scrollbar)
- 意外滚动条：容器固定高度+overflow:auto
- 双滚动条：body和内部容器同时出现
- 布局抖动：滚动条出现/消失导致内容宽度变化

## 切换操作检查(Toggle)
- ID唯一性：切换相关ID是否唯一，避免重复
- 状态同步：本地状态vs全局状态正确同步
- 防抖节流：快速连续切换导致请求堆积
- 竞态条件：异步切换操作返回顺序问题"""

def execute(ctx: dict) -> dict:
    task = ctx.get("task", "")
    result = ask(
        ROBUSTNESS_PRINCIPLES,
        f"设计问题：{task}",
        max_tokens=300
    ).strip()
    ctx["_design_guidance"] = result
    return ctx

node = Node(id="975", name="工程健壮性模式",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["超时", "timeout", "流式", "stream", "溢出", "overflow",
                          "裁剪", "clipping", "滚动条", "scrollbar", "切换检查",
                          "防抖", "节流", "竞态", "前端检查", "健壮性"]},
    execute=execute, refs=["Y30"],
    metadata={"source": "design/engineering-robustness", "category": "design"})
