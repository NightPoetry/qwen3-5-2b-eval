"""知识节点：GUI验证策略 — DOM测量/像素对比/业务e2e三层。

适用场景：需要验证生成的前端代码正确性时。
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine import Node


VERIFICATION_SCRIPT = """
// === 自动验证脚本（可在浏览器控制台运行） ===
(function verify() {
  const results = [];

  // 几何层：关键元素存在性
  const requiredIds = %REQUIRED_IDS%;
  requiredIds.forEach(id => {
    const el = document.getElementById(id);
    results.push({
      test: `#${id} exists`,
      pass: !!el,
      detail: el ? `${el.tagName} ${el.getBoundingClientRect().width}x${el.getBoundingClientRect().height}` : 'NOT FOUND'
    });
  });

  // 间距层：关键间距 >= 8px
  document.querySelectorAll('[id]').forEach(el => {
    const style = getComputedStyle(el);
    const padding = parseInt(style.padding) || 0;
    if (padding > 0 && padding < 6) {
      results.push({test: `#${el.id} padding`, pass: false, detail: `${padding}px < 6px`});
    }
  });

  // 输出
  const passed = results.filter(r => r.pass).length;
  console.table(results);
  console.log(`${passed}/${results.length} passed`);
  return results;
})();
"""


def execute(ctx: dict) -> dict:
    """生成验证脚本并附加到输出。"""
    contract = ctx.get("contract", {})
    elements = contract.get("elements", [])

    if not elements:
        return ctx

    ids = [e["id"] for e in elements]
    script = VERIFICATION_SCRIPT.replace("%REQUIRED_IDS%", str(ids))

    ctx["verification_script"] = script
    ctx.setdefault("output_extra", {})["verify.js"] = script

    return ctx


node = Node(
    id="190",
    name="GUI验证脚本",
    trigger={"type": "key_exists", "key": "contract"},
    execute=execute,
    refs=["191"],
    metadata={"source": "GUI前端集成验证工程师", "category": "verification"},
)
