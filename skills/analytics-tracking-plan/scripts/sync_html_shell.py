#!/usr/bin/env python3
"""为已有埋点 HTML 同步 template 外壳（复制按钮、样式等）。"""

from __future__ import annotations

import re
from pathlib import Path


def main() -> int:
    skill_dir = Path(__file__).resolve().parents[1]
    workspace = skill_dir.parents[2]
    template = (skill_dir / "template.html").read_text(encoding="utf-8")

    style = re.search(r"<style>.*?</style>", template, re.S)
    script = re.search(r"<script>.*?</script>", template, re.S)
    if not style or not script:
        raise SystemExit("template 缺少 style 或 script")

    header = """  <div class="page-header">
    <h2>埋点清单</h2>
    <div class="toolbar">
      <button type="button" class="copy-btn" id="copy-table-btn">一键复制数据行</button>
      <span class="copy-status" id="copy-status"></span>
    </div>
  </div>"""

    files = list(workspace.glob("*_埋点开发计划.html"))
    files.append(skill_dir / "examples" / "discover_page_埋点开发计划.html")

    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        title_m = re.search(r"<title>.*?</title>", text, re.S)
        tbody_m = re.search(r"<tbody>.*?</tbody>", text, re.S)
        if not title_m or not tbody_m:
            print(f"skip {path}")
            continue

        new_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {title_m.group(0)}
  {style.group(0)}
</head>
<body>
{header}
  <div class="table-wrap">
    <table id="tracking-table">
      <thead>
        <tr>
          <th>埋点信息</th>
          <th>页面截图</th>
          <th>页面标识</th>
          <th>埋点事件</th>
          <th>上报时机</th>
          <th>上报参数详情</th>
          <th>前后端埋点</th>
        </tr>
      </thead>
{tbody_m.group(0)}
    </table>
  </div>
  {script.group(0)}
</body>
</html>
"""
        path.write_text(new_html, encoding="utf-8")
        print(f"updated {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
