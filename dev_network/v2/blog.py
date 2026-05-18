"""
博客管线 — 全碎片节点驱动 + 自举预设系统。

用法：
  python blog.py                            # 新建亮色博客
  python blog.py --dark                     # 新建暗色博客
  python blog.py "改成暗色主题"               # 修改主题
  python blog.py "文章改成两列布局"            # 修改布局
  python blog.py "把标题改成AI实验室"          # 修改标题
  python blog.py "保存这个布局叫暗色双列"       # 保存为预设
  python blog.py "用暗色双列"                 # 复用预设新建
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import Engine

OUTPUT_DIR = Path(__file__).parent / "output_blog_final"


def main():
    engine = Engine()
    engine.load_from_dir(Path(__file__).parent / "nodes_blog")

    args = sys.argv[1:]
    task = " ".join(a for a in args if not a.startswith("--"))
    theme = "dark" if "--dark" in args else "light"

    existing_path = OUTPUT_DIR / "index.html"
    existing_html = None
    if existing_path.exists() and task and not any(
        kw in task for kw in ["新建", "创建", "新"]
    ):
        existing_html = existing_path.read_text()

    context = {
        "task": task or f"创建个人技术博客 {theme}",
        "theme": theme,
        "output_dir": str(OUTPUT_DIR),
    }
    if existing_html:
        context["existing_html"] = existing_html

    mode = "修改" if existing_html else "新建"
    print(f"=== 博客管线 ({mode}) ===")
    print(f"节点: {len(engine.nodes)} 个")
    print(f"任务: {context['task']}")

    # 检查预设
    preset_dir = Path(__file__).parent / "nodes_blog" / "saved_presets"
    if preset_dir.exists():
        presets = [f.stem for f in preset_dir.glob("*.json")]
        if presets:
            print(f"已有预设: {presets}")
    print()

    result = engine.run("000", context)

    print("\n执行轨迹:")
    engine.print_trace()

    if result.get("_changes"):
        print(f"\n变更: {result['_changes']}")
    if result.get("_saved_presets"):
        print(f"所有预设: {result['_saved_presets']}")
    if result.get("output_path"):
        print(f"\n输出: {result['output_path']}")


if __name__ == "__main__":
    main()
