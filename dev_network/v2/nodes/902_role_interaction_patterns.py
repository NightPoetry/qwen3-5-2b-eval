"""知识节点：交互设计模式库——具体交互模式与反模式参考。
"""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node

INTERACTION_PATTERNS = [
    "创建即选中：新创建的对象自动成为选中项，属性面板立即可编辑",
    "对话框是浓缩操作台：把此刻有意义的配置项放在对话框中，留空用默认值",
    "工具自动切回：单次操作工具完成后自动切回选择模式，连续操作工具保持",
    "Escape层级退出：正在绘制→取消绘制，有选中→取消选中，面板打开→关闭面板",
    "空状态引导：画布空白时显示第一步操作提示文字，加载内容后自动隐藏",
    "音效语义化：频率上行=增加/确认，下行=减少/删除，咔嗒=吸附对齐，15-200ms极短极轻",
    "吸附音效去重：只在首次进入吸附区域时触发，持续停留不重复发声",
    "富文本tooltip：350ms延迟，标题+快捷键标签+操作指引描述，mousedown立即隐藏",
    "导出零代价默认：保存对话框默认路径自动推算，文件名自动填充，路径偏好跨会话记忆",
    "导出通知链：状态栏+进度条+Toast+自动打开文件夹+音效，多管齐下防错过",
    "脏标三件套：可视化指示器+智能保存+关闭/重载/加载拦截，三处缺一不可",
    "时间空间映射：当用户感受不对时先画图标记三种时间空间，找所有跨空间裸赋值",
    "弹性区域三管齐下：固定最大尺寸+内部滚动、可拖拽分割条、双向最小高度保底",
    "类型视觉区分：不同类型元素用颜色+图标+内容三维度区分，扫一眼颜色知类型",
    "Logo即入口：Logo同时是品牌标识和设置入口，设置面板从Logo下方弹出",
]

def execute(ctx: dict) -> dict:
    ctx.setdefault("_domain_rules", []).extend(INTERACTION_PATTERNS)
    return ctx

node = Node(id="902", name="交互模式库",
    trigger={"type": "keyword", "target": "task",
             "keywords": ["交互模式", "设计模式", "交互规范", "音效设计",
                          "吸附", "导出流程", "脏标", "空状态",
                          "tooltip设计", "通知设计"]},
    execute=execute, refs=["901"],
    metadata={"source": "role/交互设计师/experience", "category": "role"})
