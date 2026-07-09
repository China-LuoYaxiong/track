# odirouter 埋点规范摘要

源文件：`source/副本-5【odirouter】埋点方案与开发计划.xlsx`  
机器可读全量数据：[reference_data.json](reference_data.json)  
示例输出：[examples/discover_page_埋点开发计划.html](examples/discover_page_埋点开发计划.html)

## 开发计划表格列

| 列名 | 说明 |
|------|------|
| 埋点信息 | 中文描述，`{页面}-{所在位置/容器}-{行为}`，尽可能写详细 |
| 页面截图 | 占位列，默认 `-` |
| 页面标识 | snake_case page id |
| 埋点事件 | 事件名；`_client`=前端，`_server`=后端 |
| 上报时机 | 何时触发 |
| 上报参数详情 | 键值参数，换行分隔，`#` 注释 |
| 前后端埋点 | 前端上报 / 后端上报 |

HTML 输出为 **7 列表格**，含「页面截图」占位列（默认 `-`）。

右上角 **「一键复制数据行」** 按钮：仅复制 `<tbody>` 数据行（不含表头），优先 HTML 表格格式粘贴 Excel，备选 TSV。参数列在 HTML 源码中每条参数独占一行。

## 标准事件（13 个）

### 前端（页面截图常用）

| 事件 | 展示名 | 关键属性 |
|------|--------|----------|
| `log_page_expose_client` | 页面曝光 | current_page_name, ref_page_url, ref_page_name |
| `log_page_leave_client` | 页面离开 | + duration（毫秒） |
| `log_click_client` | 点击 | element_pos, element_module, element_name, element_content, model_id, work_id 等 |
| `log_element_expose_client` | 元素曝光 | element_module, element_name, element_content（可 JSON 数组） |

### 后端（全局，非截图页面）

| 事件 | 展示名 |
|------|--------|
| `log_register_server` / `log_register_failed_server` / `log_register_failed_client` | 注册 |
| `log_login_server` / `log_login_failed_server` / `log_login_failed_client` | 登录 |
| `log_apikey_server` | apikey 变动 |
| `log_api_call_server` | api 调用 |
| `log_token_consume_server` | token 消耗 |
| `log_api_call_failed_server` | api 调用失败 |
| `log_credits_server` | 积分变动 |
| `log_order_server` | 订单日志 |

## 字段约定

### element_pos（页面区域）

| 值 | 含义 |
|----|------|
| top_nav | 顶部导航 |
| left_nav | 左侧导航 |
| middle_content | 主内容区 |
| bottom_nav | 底部导航 |
| chat | 对话/输入区 |
| sub_left_nav | 次级左侧导航 |

### element_module（功能模块，常用）

| 值 | 场景 |
|----|------|
| reward_task | 奖励任务弹窗 |
| create_your_account | 注册窗口 |
| create_api_key | 创建 API Key 窗口 |
| category_tab / category | 分类 Tab |
| search / search_confirm | 搜索 |
| model_expose / model_click | 模型列表 |
| api_example / low_balance | playground 弹窗 |

新页面可新增 module，保持 snake_case。

### element_name 写法

- 原则：**点击什么报什么**
- 曝光：`{module}_expose` 或 `{feature}_expose`
- 枚举示例：`logo`、`sign_in`、`switch_language`、`submit`、`input_focus`

### 列表批量曝光

`element_content` 传 JSON 字符串数组（参考 model_page）：

```
[
  {model_id: "gpt-5.5", pos: 0},
  {model_id: "deepseek-v4-flash", pos: 1}
]
```

作品类页面将 `model_id` 换为 `work_id` / `game_id`。

## 扩展属性（产品驱动，非 Excel 原规范）

**原则：** 可以扩展参数，命名以**符合实际产品语义**为准（如评论用 `comment_id`）。Excel 是基准，不够用时扩展。

**登记：** 写入 [extended_attrs.json](extended_attrs.json) → 运行 `scripts/update_reference.py` 合并（`extended: true`）。

**HTML 输出（硬性）：** 凡**不在 Excel 原规范**中的参数，参数名必须用 `<span class="param-ext">...</span>` **红色加粗**，与 Excel 已有字段区分。

```html
<span class="param-ext">comment_id</span>={评论id}   <!-- 扩展：红色加粗 -->
author_id={作者id}                                   <!-- Excel 已有：正常 -->
```

| 事件 | 已登记扩展属性 | 用途 |
|------|----------------|------|
| `log_click_client` | `comment_id` | 评论点赞、回复、提交 |
| `log_element_expose_client` | `comment_id` | 单条评论曝光 |

新增扩展：编辑 `extended_attrs.json` → 同步脚本 → 埋点方案中使用 → HTML 中标红参数名。

## 页面模板（Excel 已有 13 页）

`reference_data.json` → `pages` 字段含每页完整埋点行，可直接复制改 page_id：

| page_id | 埋点数 | 特点 |
|---------|--------|------|
| public_home_page | 9 | 未登录首页，top/middle/bottom_nav |
| home_page | 10 | 登录首页 + create_account_reward |
| login_page | 5 | 表单 + 注册弹窗 |
| model_page | 12 | 分类、搜索、model_expose、model_click |
| playground_page | 12 | chat 区、api_example、low_balance |
| pricing_page | 11 | 定价 |
| usage_page | 7 | 用量 |
| account_page | 7 | 账户 |
| apikey_page | 10 | 创建 key 全流程 |
| request_log_page | 7 | 请求日志 |
| doc_page | 4 | 文档 |
| model_detail_page | 7 | 模型详情 |
| credits_page | 10 | 积分 |

### 通用页面骨架

```
1. {页}-曝光          log_page_expose_client
2. {页}-离开          log_page_leave_client + duration
3. {页}-顶部导航点击   log_click_client + element_pos=top_nav
4. [可选] 奖励任务弹窗  曝光 + 点击
5. [可选] 侧边栏点击   element_pos=left_nav
6. [可选] 主内容交互   element_pos=middle_content
7. [可选] 列表曝光+点击
8. [可选] 弹窗曝光+点击（**成对出现，禁止只写曝光**）
```

### 弹窗 / 下拉 / 抽屉（曝光 + 点击成对）

**硬性规则：** 识别到弹窗、下拉菜单、抽屉、浮层菜单时，默认同时产出：

1. **曝光行** — `log_element_expose_client`，`element_name={module}_expose`
2. **点击行** — `log_click_client`，覆盖弹窗内所有可点击项

有曝光几乎必有点击。菜单项多或含重要转化时，每项单独一行；次要入口可合并一行 + 注释枚举。

示例：`discover_page` 点击侧边栏「更多」→ 更多弹窗曝光 + `发现页-更多弹窗上-联系我们点击` 等各一行（埋点信息须含弹窗名）。

## 多页面 Excel 已覆盖的顶栏 element_name

Models、Pricing、Docs、switch language、Earn More Credits、Sign in、Free credits、account、avatar、API keys、sign out、Home、Playground、View all 等。

新页面顶栏元素按截图实际文案映射为 snake_case 英文名。
