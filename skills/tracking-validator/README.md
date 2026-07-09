# tracking-validator

埋点点位上报入库验证工具

## 功能说明

验证埋点方案中指定序号点位的上报与入库状态，输出 HTML 验证报告。列宽规则：埋点事件 128px、上报参数详情 320px（×2.5）、案例/错误/警告列 510px 同宽。

## 输入

- 埋点方案 Excel（如 `副本-【odirouter】埋点方案与开发计划.xlsx`）
- 测试数据 CSV（如 `odirouter_test_data.csv`）
- 序号范围（如 `20-35` 或 `20,25,30,35`）

> **默认参考文件**：已在 `source/` 目录下提供 `副本-【odirouter】埋点方案与开发计划.xlsx` 和 `odirouter_test_data.csv` 作为标准输入参考。

## 输出

HTML 验证报告，包含：

| 列 | 说明 |
|----|------|
| 序号 / 埋点信息 | 基本信息（埋点信息列可换行） |
| 页面标识 / 埋点事件 / 上报参数详情 | Excel 方案对照（埋点事件、上报参数详情均可换行，后者宽 ×2.5） |
| 是否上报 / 是否入库 | 基于最新一条记录 |
| 入库案例 / 错误案例 | JSON，510px 宽，`.scroll-box` 横纵滚动 |
| 入库错误原因或警告 | 错误原因 / 警告分行，510px 宽（与案例列同宽） |

### CSS 列宽变量

| 变量 | 值 | 适用列 |
|------|-----|--------|
| `--col-event-width` | 128px | 埋点事件（可换行） |
| （计算） | 320px（×2.5） | 上报参数详情（可换行） |
| `--col-case-width` | 510px | 入库案例、错误案例、入库错误原因或警告（三列同宽） |

### 报告布局

- **整表横向滚动**：`.table-wrap` 包裹；表格 `width: max-content` + `<colgroup>` 固定列宽，避免列重叠
- **埋点信息换行**：`.col-name` 自动折行，避免单行过长
- **埋点事件**：128px 宽，可自动换行
- **上报参数详情**：宽 320px（埋点事件列 × 2.5），可自动换行，不设滚动区域
- **独立滚动区域**（固定高度，横纵双向滚动，仅用于较长内容）：

| 区域 | CSS 类 | 列宽 | 高度 |
|------|--------|------|------|
| 入库案例 / 错误案例 | `.col-case` + `.scroll-box.case-box` | 510px | 180px |
| 入库错误原因或警告 | `.col-error` + `.scroll-box.error-box` | 510px | 120px |

- **案例 JSON**：每个 `"参数": 值` 独占一行，行内不折行，由外层 `.scroll-box` 滚动查看

## 使用方法

```bash
python scripts/validate.py <excel_file> <csv_file> <序号范围> [output_file]
```

### 示例

```bash
# 验证序号 20-35
python scripts/validate.py "副本-【odirouter】埋点方案与开发计划.xlsx" "odirouter_test_data.csv" "20-35"

# 验证全量 1-175
python scripts/validate.py "副本-【odirouter】埋点方案与开发计划.xlsx" "odirouter_test_data.csv" "1-175"

# 指定输出文件
python scripts/validate.py "副本-【odirouter】埋点方案与开发计划.xlsx" "odirouter_test_data.csv" "107-110" "tracking_report_107_110.html"
```

## 文件结构

```
tracking-validator/
├── SKILL.md          # Skill 配置文件（AI 执行入口）
├── README.md         # 本文件
├── reference.md      # 验证规则参考
├── 使用说明.md       # 用户使用指南
├── source/           # 默认输入参考文件
│   ├── 副本-【odirouter】埋点方案与开发计划.xlsx
│   └── odirouter_test_data.csv
└── scripts/
    └── validate.py   # 核心验证脚本
```

## 验证规则摘要

1. **候选匹配**：事件名 + 页面标识（空则跳过）+ 固定值参数
2. **取最新一条**：按 `st_event_time` 降序，仅用最新记录判定
3. **是否上报**：存在匹配记录
4. **是否入库**：最新一条 `st_status=1`（多余参数仅警告，不阻断）
5. **错误原因**：`st_error_info` + 缺失必填参数
6. **警告**：方案未定义的多余参数

## 依赖

- pandas
- openpyxl
