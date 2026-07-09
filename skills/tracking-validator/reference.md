# 埋点验证参考文档

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
- **多余参数不阻断入库判定**（仅生成警告）

**结果：**
- ✅ 是：最新一条 `st_status=1`
- ❌ 否：无匹配记录，或最新一条 `st_status≠1`

### 3. 参数校验（用于错误原因 / 警告）

**每个点位的白名单 = 「上报参数详情」解析出的参数名列表。**

**对比内容：**
- 实际上报参数 vs 该点位白名单

**分类：**
- 预置属性和公共属性：必有字段
- 业务属性：白名单中的参数（入库案例 JSON 仅展示白名单字段）
- 多余参数 → **警告**（不导致入库失败）
- 缺失参数 → **错误原因**

## 错误与警告分类

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

### 2. 警告

方案未定义但已随数据上报（通常 `st_status=1` 仍入库成功）的多余参数：

**检测逻辑：**
```python
# 该点位「上报参数详情」白名单
defined_params = ['current_page_name', 'ref_page_url', 'element_name']

# 系统预置参数（不参与校验）
system_params = ['extend', 'adid', 'current_page_url', 'platform_type']

# 实际参数
actual_params = list(properties.keys())

# 多余参数 = 实际参数 - 白名单 - 系统预置参数
extra_params = [p for p in actual_params if p not in defined_params and p not in system_params]

# 缺失参数 = 白名单 - 实际参数
missing_params = [p for p in defined_params if p not in actual_params]
```

**格式：**
```
警告：参数【ref_page_id、current_page_id、status、register_method】上报参数详情中不要求上报
```

### 3. 展示规则

- **判定记录**：每个点位在所有候选中按 `st_event_time` 取**最新一条**
- 已入库（最新一条 `st_status=1`）：入库案例展示白名单字段；有多余参数则显示**警告**；错误案例为「无」
- 未入库（最新一条 `st_status≠1`）：显示**错误原因**（及可能的警告）；错误案例展示最新一条完整 JSON
- 两者可同时出现（未入库时既有错误原因也有警告）

### 4. st_event_datetime 提取

案例 JSON 中 `st_event_datetime` 位于 `st_event_time` 下方，取值优先级：

1. CSV `st_available_message` 中的 `st_event_datetime`
2. 由 `st_event_time`（毫秒时间戳）转换：`YYYY-MM-DD HH:MM:SS`
3. 兜底：CSV 的 `st_update_at` / `st_report_time` / `st_event_date`

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
**不含 element_pos 固定匹配条件** — 带 `element_pos` 的记录若 `st_status=1` 仍可能匹配并入库，多余 `element_pos` 显示为**警告**。

## 字段映射

### 预置属性和公共属性

| 字段名 | 说明 | 位置 |
|--------|------|------|
| st_pk_id | 主键ID | raw_message顶层 |
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
| 入库案例 | 最新一条入库记录 JSON | `.col-case` + `.scroll-box.case-box`，510px 宽 |
| 入库错误原因或警告 | 错误原因 / 警告（分行） | `.col-error` + `.scroll-box.error-box`，510px 宽 |
| 错误案例 | 最新一条未入库 JSON；已入库「无」 | `.col-case` + `.scroll-box.case-box`，510px 宽 |

### JSON 案例格式

- 使用 `format_case_json_text`：每个 `"key": value` 独占一行
- `white-space: pre`，值不折行，长内容由外层 `.scroll-box` 横纵滚动查看
- 入库案例业务属性仅含方案白名单字段

### JSON案例结构（展示格式）

每参数独占一行，行内不折行：

```
{
  "预置属性和公共属性": {
    "st_pk_id": "uuid",
    "st_event_time": 1234567890,
    "st_event_datetime": "2026-07-09 09:32:48",
    "platform_type": "web"
  },
  "业务属性": {
    "current_page_name": "xxx_page",
    "ref_page_url": "https://..."
  }
}
```

### HTML 渲染辅助函数（validate.py）

| 函数 | 用途 |
|------|------|
| `render_case_box(text)` | 入库案例 / 错误案例：`.col-case` + `.scroll-box.case-box`（510px 宽，180px 高，横纵滚动） |
| `render_error_box(text)` | 入库错误原因或警告：`.col-error` + `.scroll-box.error-box`（510px 宽，120px 高，横纵滚动） |
| `format_case_json_text(case)` | 案例 JSON 每参数单行格式化 |
| `escape_html(text)` | HTML 转义 |
