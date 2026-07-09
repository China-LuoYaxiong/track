# analytics-tracking-plan

从**页面截图**自动生成 odirouter 规范 **HTML 埋点清单** 的 Cursor Agent Skill。

**本文件夹为完整可移植包**，复制到任意电脑即可使用。

## 目录结构

```
analytics-tracking-plan/
├── SKILL.md                         # Agent 主流程（Cursor 自动读取）
├── reference.md                     # 事件、字段、页面模板摘要
├── reference_data.json              # Excel 全量数据 + 合并后的扩展属性
├── extended_attrs.json              # Skill 扩展事件属性（非 Excel 原规范）
├── template.html                    # HTML 输出模板（7 列 + 一键复制数据行）
├── examples.md                      # 示例说明
├── README.md                        # 本文件
├── 使用说明.md                       # 快速上手
├── source/
│   └── 副本-5【odirouter】埋点方案与开发计划.xlsx
├── examples/
│   ├── discover_page_埋点开发计划.html
│   └── work_detail_page_埋点开发计划.html
└── scripts/
    ├── update_reference.py          # Excel → reference_data.json
    └── sync_html_shell.py           # template 外壳同步到已有 HTML
```

## 输出格式要点

| 特性 | 说明 |
|------|------|
| 7 列表格 | 在 Excel 6 列基础上插入「页面截图」（默认 `-`） |
| 扩展参数 | 可扩展，命名贴合产品语义；**不在 Excel 中的参数** HTML 输出红色加粗，登记于 `extended_attrs.json` |
| 一键复制数据行 | 仅复制数据行（无表头），粘贴到 Excel「开发计划」 |
| 参数合法性 | 只能用事件已定义属性 + 扩展属性，禁止自造字段 |

## 安装

**项目级（推荐）：** 复制到 `<项目>/.cursor/skills/analytics-tracking-plan/`

**全局：** `~/.cursor/skills/analytics-tracking-plan/`（Windows：`C:\Users\<用户名>\.cursor\skills\`）

## 使用

```
@analytics-tracking-plan 帮我出埋点
```

附上页面截图，可选补充 `page_id`、是否排除游戏区域、是否全事件带 `work_id` 等。

产出：`{page_id}_埋点开发计划.html`

## 粘贴到 Excel

1. 浏览器打开 HTML
2. 点击 **「一键复制数据行」**
3. 在 Excel「开发计划」Sheet 中 **Ctrl+V**（表头已存在时直接贴数据行）

## 维护

```bash
# Excel 规范更新后
python scripts/update_reference.py

# template 复制按钮/样式变更后，同步已有 HTML
python scripts/sync_html_shell.py
```

## 文件说明

| 文件 | 作用 |
|------|------|
| SKILL.md | Agent 主流程 |
| reference.md | 人类可读规范摘要 |
| reference_data.json | 机器可读全量数据 |
| extended_attrs.json | 扩展事件属性定义 |
| template.html | HTML 模板（含复制脚本） |
| examples/*.html | 标准输出示例 |
| scripts/update_reference.py | 从 xlsx 提取并合并扩展属性 |
| scripts/sync_html_shell.py | 批量更新 HTML 外壳 |
