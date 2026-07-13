# 埋点验证参考文档

## 输入文件规则（强制）

| 规则 | 说明 |
|------|------|
| 必须使用 | 用户 @ 提供的埋点方案 **xlsx** 和测试数据 **csv** |
| 禁止使用 | `tracking-validator/source/` 下任何内置示例文件 |
| 路径缺失 | 先向用户确认，不得 fallback 到 skill 内置文件 |
| 执行前 | 打印两个输入文件的绝对路径 |
| 报告页脚 | 写入埋点方案与测试数据路径 |
| 脚本拦截 | `validate.py` 检测到 `source/` 路径会报错退出 |

`source/` 目录文件仅用于 Skill 开发时了解 Excel/CSV 列结构，**不能替代用户真实数据**。

## 测试数据 CSV 格式（用户提供时仅需 5 列）

| 列名 | 说明 |
|------|------|
| `st_event_name` | 事件名称 |
| `st_raw_message` | 完整上报 JSON（含 `properties` 及业务参数） |
| `st_status` | 入库状态（`1`=成功） |
| `st_error_info` | 入库失败原因（JSON；成功时可 `{}`） |
| `st_available_message` | 辅助 JSON（可为空；优先取其中 `st_event_datetime`） |

表头须完全一致。`validate.py` 启动时校验这 5 列；含额外列时仅提示，不影响验证。

## 验证规则

### 1. 上报验证

**判断条件：**
- 在CSV中找到满足**候选匹配**的记录（不要求参数完全合规）
- 候选匹配条件：
  - `st_event_name` = 埋点事件名称
  - `properties.current_page_name` = 页面标识（**页面标识为空时跳过**，适用于后端 `_server` 埋点）
  - 「上报参数详情」中定义的非动态固定值参数（如有）

**结果：**
- ✅ 是：找到至少一条候选匹配记录（判定以最新一条为准）
- ❌ 否：未找到匹配记录（未上报或未触发）

### 2. 入库验证

**判断条件：**
- 取该点位**最新一条**候选匹配记录（按 `st_event_time` 降序）
- 最新一条 `st_status` = 1 即算入库成功
- **多余参数不阻断入库判定**（仅生成警告，**不影响合规判定**）

**结果：**
- ✅ 是：最新一条 `st_status=1`
- ❌ 否：无匹配记录，或最新一条 `st_status≠1`

### 3. 合规验证

**判断条件（基于 `case_record`，与入库案例同源）：**
- 已入库时：`case_record` = 最新 `st_status=1` 记录
- 未入库时：`case_record` = `latest`
- 顶层参数：无缺失**必填**参数（白名单来自「上报参数详情」，注释标注可选的不算缺失）
- 嵌套结构：JSON 字符串字段（如 `element_content`）内对象键名须与方案示例一致
- **多余参数仅警告，不影响合规**
- 通过 `get_compliance_from_record(case_record, point)` **实时**计算，不使用缓存字段

**嵌套结构校验逻辑：**
1. 从「上报参数详情」示例块提取嵌套键名（如 `{model_id: "gpt-4o", pos: 0}` → `model_id`、`pos`）
2. 解析实际上报的 JSON 字符串，检查数组内每个对象的键名
3. 方案要求 `model_id`，实际上报 `model_name` → **不合规**

**典型场景（序号46）：**
- 方案：`element_content` 示例为 `[{model_id: "deepseek-v4-flash"}, ...]`
- 实际上报：`[{"model_name":"claude-haiku-4-5"}, ...]`
- `st_status=1` → 入库 ✅；键名错误 → 合规 ❌

**结果：**
- ✅ 是：无缺失必填参数、无嵌套键名错误
- ❌ 否：缺失必填参数或存在嵌套键名错误
- 多余参数仅产生警告，不计入不合规

### 4. 参数校验（用于错误原因 / 不合规 / 警告）

**每个点位的白名单 = 「上报参数详情」解析出的参数名列表（含必填与可选）。**

**可选参数识别：** 满足任一即视为可选，缺失不算不合规：
- 行内 `#` 注释含「有就报，没有就算了」「没有就算了」「非必填」
- 行内 `#` 注释为**独立标注**「可选」「选填」（如 `# 可选`），**不会**误匹配「可选场景」「可选择」等描述性文字
- 值侧为花括号占位且语义为可选，如 `model_id = {可选参数}`、`work_id={可选}`、`tag={选填参数}`、`element_content={可选补充}`

**对比内容：**
- 实际上报参数 vs 该点位白名单

**分类：**
- 预置属性和公共属性：必有字段
- 业务属性：白名单中的参数；方案外多余参数单独展示在「多余参数（方案未定义）」区块
- 多余参数 → **警告**（**不影响合规**）
- 缺失必填参数 → **错误原因** + **不合规**
- 缺失可选参数 → 忽略
- 嵌套键名错误 → **不合规**

## 错误、不合规与警告分类

### 1. 错误原因

导致 `st_status≠1` 或未满足方案要求的问题：

**来源：**
- `st_error_info` 系统校验错误
- 白名单中要求但未上报的参数

| 错误信息 | 说明 |
|----------|------|
| 属性名【xxx】在埋点方案中不存在 | 上报了方案未定义的属性（系统侧拒绝） |
| 必填参数【xxx】缺失 | 缺少必填参数 |

**格式：**
```
错误原因：属性名【current_page_name】在埋点方案中不存在；必填参数【model_id】缺失
```

### 2. 不合规

已入库（`st_status=1`）或已上报但参数/结构与方案不符：

**来源：**
- 嵌套 JSON 结构键名与方案示例不一致
- 缺失**必填**参数（不含注释标注为可选的参数）

**格式：**
```
不合规：【element_content】内应使用【model_id】，实际上报【model_name】
```

### 3. 警告

方案未定义但已随数据上报（通常 `st_status=1` 仍入库成功）的多余参数：

**检测逻辑：**
```python
# 该点位「上报参数详情」白名单
defined_params = ['current_page_name', 'ref_page_url', 'element_name']

# 系统预置参数（不参与校验）
system_params = ['extend', 'adid', 'current_page_url', 'platform_type']

# 实际参数
actual_params = list(properties.keys())

# 多余参数 = 实际参数 - 白名单 - 系统预置参数（仅警告，不影响合规）
extra_params = [p for p in actual_params if p not in defined_params and p not in system_params]

# 缺失必填参数 = 必填参数 - 实际参数（可选参数缺失忽略）
required_params = [p for p in defined_params if p not in optional_params]
missing_params = [p for p in required_params if p not in actual_params]

# 合规 = 无缺失必填参数 且 无嵌套键名错误（extra_params 不计入）
is_compliant = not missing_params and not nested_issues
```

**格式：**
```
警告：参数【ref_page_id、current_page_id、status、register_method】上报参数详情中不要求上报
```

### 4. 展示规则

- **判定记录**：每个点位在所有候选中按 `st_event_time` 取**最新一条**判定是否上报/是否入库
- **入库案例与入库错误原因或警告**：共用同一条 `case_record`（已入库时取最新 `st_status=1` 记录），基于该记录 `properties` **实时**计算合规结果，保证两列数据一致
- 已入库且合规：入库案例展示白名单 + 多余参数区块；无警告/不合规
- 已入库但不合规：同上；显示**不合规**（及可能的**警告**）；错误案例为「无」
- 未入库：显示**错误原因**；错误案例展示 `latest` 完整 JSON

### 5. st_event_datetime 提取

案例 JSON 中 `st_event_datetime` 位于 `st_event_time` 下方，取值优先级：

1. CSV `st_available_message` 中的 `st_event_datetime`
2. 由 `st_raw_message` 内 `st_event_time`（毫秒时间戳）转换：`YYYY-MM-DD HH:MM:SS`

## 同事件多点位区分示例

### 序号93：账户页-侧边栏点击

**上报参数详情白名单：**
```
current_page_name, ref_page_url, element_pos, element_name
```
固定匹配条件：`element_pos=left_nav`

### 序号94：账户页-界面点击

**上报参数详情白名单：**
```
current_page_name, ref_page_url, element_name
```
**不含 element_pos 固定匹配条件** — 带 `element_pos` 的记录若 `st_status=1` 仍可能匹配并入库，多余 `element_pos` 显示为**警告**（不影响合规）。

### 序号91 vs 120：版本迭代与全局汇总

**序号91（页面级，旧规范）：** 不含 `element_tab`
```
current_page_name, ref_page_url, element_module, element_name
```

**序号120（全局汇总，新规范）：** 含 `element_tab`，`model_id` 为可选
```
model_id={模型id} # 有就报，没有就算了  → 可选参数
element_tab={曝光来源...}
```

| 场景 | 判定 |
|------|------|
| 91 实际上报多了 `element_tab` | ✅ 合规 + **警告**（版本迭代新增字段） |
| 120 实际上报无 `model_id` | ✅ 合规（可选参数缺失忽略） |
| 120 实际上报有 `element_tab` 无 `model_id` | ✅ 合规 |
| 方案写 `work_id = {可选参数}` 实际上报无 `work_id` | ✅ 合规（占位语义为可选） |

## 字段映射

### 预置属性和公共属性

| 字段名 | 说明 | 位置 |
|--------|------|------|
| st_pk_id | 主键ID | raw_message顶层 |
| st_status | 入库状态（1=成功，2=事件不存在，3=属性校验失败） | CSV 行 st_status |
| st_user_id | 用户ID | raw_message顶层 |
| st_role_id | 角色ID | raw_message顶层 |
| st_account_id | 账号ID | raw_message顶层 |
| st_distinct_id | 设备ID | raw_message顶层 |
| st_event_name | 事件名称 | raw_message顶层 |
| st_event_time | 事件时间戳 | raw_message顶层 |
| st_event_datetime | 事件时间（可读） | st_available_message 或由 st_event_time 转换 |
| platform_type | 平台类型 | properties |
| adid | 广告ID | properties |

### 系统预置参数（不参与校验）

| 参数名 | 说明 |
|--------|------|
| extend | 扩展信息 |
| adid | 广告ID |
| current_page_url | 当前页面URL |
| platform_type | 平台类型 |

### 业务属性（埋点方案定义）

从Excel「上报参数详情」列解析，如：
- current_page_name
- ref_page_url
- element_module
- element_name
- model_id
- 等

## 匹配条件示例

### 序号35：首页-模型点击

**埋点方案定义：**
- 埋点事件：log_click_client
- 页面标识：home_page
- 额外匹配：element_module=model_click

**CSV匹配条件：**
```python
st_event_name == 'log_click_client'
AND properties.current_page_name == 'home_page'
AND properties.element_module == 'model_click'
```

### 序号44：模型页-搜索确认点击

**埋点方案定义：**
- 埋点事件：log_click_client
- 页面标识：model_page
- 额外匹配：element_module=search_confirm

**CSV匹配条件：**
```python
st_event_name == 'log_click_client'
AND properties.current_page_name == 'model_page'
AND properties.element_module == 'search_confirm'
```

## HTML报告格式

### 汇总栏

| 指标 | 计算方式 |
|------|----------|
| 总点位数 | `len(all_results)` |
| 已上报已入库合规 | `is_reported_stored_compliant(item)` 为真的点位数 |
| 已上报已入库不合规 | `is_reported_stored_non_compliant(item)` 为真的点位数 |
| 已上报未入库 | `is_reported_not_stored(item)` 为真的点位数 |
| 未上报 | `is_not_reported(item)` 为真的点位数 |

恒等式：`总点位数 = 已上报已入库合规 + 已上报已入库不合规 + 已上报未入库 + 未上报`

### Tab 切换

| Tab | DOM id | 筛选规则 | 为空时提示 |
|-----|--------|----------|------------|
| 全部 | `tab-all` | 无筛选 | 暂无验证点位 |
| 已上报已入库合规 | `tab-ok-compliant` | 上报 ✅、入库 ✅、合规 ✅ | 暂无已上报已入库合规的点位 |
| 已上报已入库不合规 | `tab-ok-non-compliant` | 上报 ✅、入库 ✅、合规 ❌ | 暂无已上报已入库不合规的点位 |
| 已上报未入库 | `tab-reported-not-stored` | 上报 ✅、入库 ❌ | 暂无已上报未入库的点位 |
| 未上报 | `tab-not-reported` | 上报 ❌ | 暂无未上报的点位 |

汇总统计与各 Tab 括号内计数一致。

### CSS 列宽变量

| 变量 | 值 | 适用列 |
|------|-----|--------|
| `--col-event-width` | 128px | `.col-event` 埋点事件 |
| `calc(var(--col-event-width) * 2.5)` | 320px | `.col-param` 上报参数详情 |
| `--col-case-width` | 510px（340px × 1.5） | `.col-case` 入库案例/错误案例、`.col-error` 入库错误原因或警告 |

### 布局

- 表格外层 `.table-wrap`：`overflow-x: auto`，整表可横向滚动
- 表格 `width: max-content` + `table-layout: fixed` + `<colgroup>` 固定各列宽度，**避免列宽被压缩重叠**
- 「埋点信息」列 `.col-name`：允许换行（`word-break: break-word`），控制列宽避免单行过长
- 「埋点事件」列 `.col-event`：固定 `--col-event-width`（128px），**可自动换行**
- 「上报参数详情」列 `.col-param`：宽度 `calc(var(--col-event-width) * 2.5)`（320px），**可自动换行**
- 案例/错误列宽 `--col-case-width: 510px`（340px × 1.5）；入库案例、错误案例、入库错误原因或警告**三列同宽**
- 案例/错误区域使用 `.scroll-box` 容器，**固定高度 + 横纵双向滚动**：
  - `.scroll-box.case-box`：入库案例、错误案例（180px 高，深色背景）
  - `.scroll-box.error-box`：入库错误原因或警告（120px 高）
- 案例 JSON 内 `pre.case-json`：`white-space: pre`，行内不折行，由外层 `.scroll-box` 提供横向/纵向滚动

### 列样式速查

| 列 | CSS 类 | 展示方式 |
|----|--------|----------|
| 埋点信息 | `.col-name` | 自动换行，控制列宽 |
| 页面标识 | `.col-spec` | 普通文本 |
| 埋点事件 | `.col-event` | **128px 宽，可换行** |
| 上报参数详情 | `.col-param` + `pre.spec-detail` | **320px（×2.5），可换行**（`pre-wrap`） |
| 入库案例 / 错误案例 | `.col-case` + `.scroll-box.case-box` | 510px 宽，180px 高，横纵滚动 |
| 入库错误原因或警告 | `.col-error` + `.scroll-box.error-box` | 510px 宽，120px 高，横纵滚动 |

### 表格列定义

| 列名 | 说明 | 样式 |
|------|------|------|
| 序号 | 点位序号 | 普通 |
| 埋点信息 | 点位中文名称 | `.col-name`，可换行 |
| 页面标识 | page_id，空则 `—` | `.col-spec` |
| 埋点事件 | 事件名称 | `.col-event`，128px，可换行 |
| 上报参数详情 | Excel 方案原文 | `.col-param` + `pre.spec-detail`，320px（×2.5），可换行 |
| 是否上报 | ✅ 是 / ❌ 否 | 绿色/红色 |
| 是否入库 | ✅ 是 / ❌ 否 | 绿色/红色 |
| 是否合规 | ✅ 是 / ❌ 否 | 绿色/红色 |
| 入库案例 | 最新一条入库记录 JSON | `.col-case` + `.scroll-box.case-box`，510px 宽 |
| 入库错误原因或警告 | 错误原因 / 不合规 / 警告（分行） | `.col-error` + `.scroll-box.error-box`，510px 宽 |
| 错误案例 | 最新一条未入库 JSON；已入库「无」 | `.col-case` + `.scroll-box.case-box`，510px 宽 |

### JSON 案例格式

- 使用 `format_case_json_text`：每个 `"key": value` 独占一行
- `white-space: pre`，值不折行，长内容由外层 `.scroll-box` 横纵滚动查看
-- 入库案例业务属性含方案白名单字段；方案外多余参数单独展示在「多余参数（方案未定义）」区块
- 汇总型点位（含动态 `{...}` 占位参数）在入库案例 JSON 下方追加**动态参数采样**：
  - 从所有候选记录中收集每个动态参数的实际取值，去重后最多展示 20 条
  - 展示格式：
    ```
    ═══ 动态参数取值（最多20条） ═══
      element_tab: value1、value2、…
      current_page_name: value1、value2、…
    ```
  - 可选语义 `{可选参数}` 占位不参与采样
  - 仅已入库点位展示（无候选记录时无采样）

### JSON案例结构（展示格式）

每参数独占一行，行内不折行：

```
{
  "预置属性和公共属性": {
    "st_pk_id": "uuid",
    "st_status": "1",
    "st_event_time": 1234567890,
    "st_event_datetime": "2026-07-09 09:32:48",
    "platform_type": "web"
  },
  "业务属性": {
    "current_page_name": "xxx_page",
    "ref_page_url": "https://..."
  },
  "多余参数（方案未定义）": {
    "element_name": "model_expose",
    "element_pos": "middle_content"
  }
}
```

### HTML 渲染辅助函数（validate.py）

| 函数 | 用途 |
|------|------|
| `parse_dynamic_params_from_detail(detail_str)` | 提取动态参数名（值侧以 `{...}` 开头，排除 `{可选参数}` 等可选语义），返回 `{param_name: placeholder}` |
| `collect_param_samples(all_results, dynamic_params, max_samples=20)` | 从所有匹配记录的 properties 中收集动态参数的实际取值，去重排序后截取最多 max_samples 条 |
| `is_optional_param_line(line)` | 判断参数是否可选：注释短语 或 值侧 `{可选参数}` 等占位 |
| `check_param_compliance(properties, defined_params, detail_str, optional_params)` | 合规校验：多余参数仅警告，缺失必填/嵌套键名错误才不合规 |
| `is_reported_stored_compliant(item)` | 判定点位是否已上报、已入库且合规 |
| `is_reported_stored_non_compliant(item)` | 判定点位是否已上报、已入库但不合规 |
| `is_reported_not_stored(item)` | 判定点位是否已上报但未入库 |
| `is_not_reported(item)` | 判定点位是否未上报 |
| `get_latest_record(results)` | 取最新一条匹配记录，判定是否上报/是否入库 |
| `get_latest_stored_record(results)` | 取最新已入库记录，作为 `case_record` |
| `classify_results(results, point)` | 返回 `latest`、`case_record`、上报/入库/合规状态 |
| `get_compliance_from_record(record, point)` | 基于指定记录 properties 实时计算合规（与入库案例同源） |
| `format_error_or_warning(record, point, stored_only)` | 生成错误/不合规/警告；`stored_only=True` 时仅展示不合规与警告 |
| `render_report_table_rows(all_results, tab_filter)` | 生成表格行；`tab_filter` 取值 `all` / `ok_compliant` / `ok_non_compliant` / `reported_not_stored` / `not_reported` |
| `render_tab_panel(tab_id, rows_html, empty_message, active)` | 生成单个 Tab 面板 HTML |
| `render_case_box(text)` | 入库案例 / 错误案例：`.col-case` + `.scroll-box.case-box`（510px 宽，180px 高，横纵滚动） |
| `render_error_box(text)` | 入库错误原因或警告：`.col-error` + `.scroll-box.error-box`（510px 宽，120px 高，横纵滚动） |
| `format_case_json_text(case)` | 案例 JSON 每参数单行格式化 |
| `escape_html(text)` | HTML 转义 |
