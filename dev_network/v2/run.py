"""
v2 运行入口 — 完全动态化的节点图执行。

引擎加载 nodes/ 目录中的所有节点，
从入口节点开始栈展开执行。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from engine import Engine


def main():
    engine = Engine()

    # 动态加载所有节点
    nodes_dir = Path(__file__).parent / "nodes"
    engine.load_from_dir(nodes_dir)

    print(f"=== v2 节点图执行引擎 ===")
    print(f"已加载 {len(engine.nodes)} 个节点:")
    for nid, n in sorted(engine.nodes.items()):
        refs = " → " + ",".join(n.refs) if n.refs else " (终端)"
        print(f"  [{nid}] {n.name}{refs}")

    # 初始上下文
    output_dir = str(Path(__file__).parent / "output")
    context = {
        "task": "待办事项 Web 应用（添加、删除、标记完成，localStorage 存储）",
        "output_dir": output_dir,
    }

    print(f"\n任务: {context['task']}")
    print(f"输出: {output_dir}")
    print(f"\n--- 开始执行 ---\n")

    # 执行
    result = engine.run("010", context)

    # 打印轨迹
    print("\n--- 执行轨迹 ---\n")
    engine.print_trace()

    # 结果摘要
    print("\n--- 结果 ---\n")
    if result.get("_errors"):
        print("错误:")
        for e in result["_errors"]:
            print(f"  [{e['node']}] {e['error']}")

    if result.get("html_issues"):
        print(f"HTML修复: {result['html_issues']}")
    if result.get("css_issues"):
        print(f"CSS修复: {result['css_issues']}")
    if result.get("js_issues"):
        print(f"JS修复: {result['js_issues']}")
    if result.get("id_issues"):
        print(f"ID修复: {result['id_issues']}")

    if result.get("output_path"):
        print(f"\n输出保存到: {result['output_path']}")
        for f in result.get("output_files", []):
            fpath = Path(result["output_path"]) / f
            if fpath.exists():
                print(f"  {f}: {fpath.stat().st_size} bytes")


if __name__ == "__main__":
    main()
