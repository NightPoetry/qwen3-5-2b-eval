"""
多场景测试 — 验证知识网络的选择性激活。

不同任务应激活不同的知识节点子集：
- 待办应用 → 创建流+反馈+暗色+间距+溢出
- 桌面应用 → Tauri诊断+资源路径
- 视频编辑器 → NLE时间映射+绑定操作+音效+拟物
- 博客 → 事实校准
- 拖拽看板 → 拟物交互
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from engine import Engine, Node


def load_engine():
    engine = Engine()
    engine.load_from_dir(Path(__file__).parent / "nodes")
    return engine


def test_scenario(engine, task, expected_active, expected_inactive):
    """测试单个场景的节点激活情况。"""
    context = {"task": task, "output_dir": "/tmp/test_scenario"}

    # 模拟执行（不实际调用API，只检查触发逻辑）
    # 用dry-run模式：只检查从入口出发哪些节点会被触发
    entry = engine.nodes.get("010")
    if not entry:
        return False, "入口节点不存在"

    # 简单模拟：检查哪些节点的trigger对给定task满足
    activated = set()
    for nid, node in engine.nodes.items():
        if engine.check_trigger(node, {"task": task, "interactions": task,
                                        "_input": task, "html": "", "css": "",
                                        "js": "", "contract": {}}):
            activated.add(nid)

    # 验证
    missing_expected = [n for n in expected_active if n not in activated]
    unwanted_active = [n for n in expected_inactive if n in activated]

    success = not missing_expected and not unwanted_active
    return success, activated, missing_expected, unwanted_active


def main():
    engine = load_engine()
    print(f"=== 多场景知识网络测试 ({len(engine.nodes)} 节点) ===\n")

    scenarios = [
        {
            "name": "待办应用",
            "task": "待办事项 Web 应用（添加、删除、标记完成，localStorage 存储）",
            "expect_active": ["110"],  # 创建流（有"添加"关键词）
            "expect_inactive": ["170", "180", "220"],  # Tauri/NLE/音效不该触发
        },
        {
            "name": "Tauri桌面应用",
            "task": "Tauri桌面笔记应用（native菜单、文件系统访问）",
            "expect_active": ["170"],  # Tauri诊断
            "expect_inactive": ["180", "220"],  # NLE/音效不该触发
        },
        {
            "name": "视频编辑器",
            "task": "视频时间轴编辑器（多轨、剪辑、拖拽片段、播放）",
            "expect_active": ["180", "150", "220"],  # NLE+拟物+音效
            "expect_inactive": ["170"],  # Tauri不该触发
        },
        {
            "name": "博客生成",
            "task": "技术博客页面（文章列表、标签分类、关于页）blog",
            "expect_active": ["160"],  # 事实校准
            "expect_inactive": ["170", "180", "150"],  # Tauri/NLE/拟物不该触发
        },
        {
            "name": "拖拽看板",
            "task": "看板应用（添加卡片、拖拽在列之间移动、排序）",
            "expect_active": ["150", "110"],  # 拟物+创建流
            "expect_inactive": ["170", "180"],  # Tauri/NLE不该触发
        },
    ]

    passed = 0
    total = len(scenarios)

    for s in scenarios:
        success, activated, missing, unwanted = test_scenario(
            engine, s["task"], s["expect_active"], s["expect_inactive"]
        )

        status = "PASS" if success else "FAIL"
        if success:
            passed += 1

        print(f"  [{status}] {s['name']}")
        print(f"       任务: {s['task'][:40]}...")
        print(f"       激活: {sorted(activated)}")
        if missing:
            print(f"       缺失: {missing}")
        if unwanted:
            print(f"       误触: {unwanted}")
        print()

    print(f"--- 结果: {passed}/{total} 通过 ---")

    if passed == total:
        print("\n知识网络选择性激活验证通过：")
        print("  - 待办应用不触发NLE/Tauri/音效")
        print("  - Tauri应用不触发NLE/音效")
        print("  - 视频编辑器触发NLE+拟物+音效")
        print("  - 博客触发校准")
        print("  - 拖拽看板触发拟物")


if __name__ == "__main__":
    main()
