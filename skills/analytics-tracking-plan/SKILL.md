---
name: analytics-tracking-plan
description: >-
  Generates frontend analytics tracking plans (埋点清单) from page screenshots,
  following the odirouter Excel spec (事件自定义属性 + 开发计划). Outputs a
  standalone HTML table with one-click copy to Excel. Use when the user provides
  a page screenshot, asks for 埋点/埋点方案/埋点清单/开发计划, or mentions
  analytics tracking for a new page.
---

# 页面截图 → 埋点开发计划

根据用户提供的**页面截图**，按 odirouter 埋点规范生成 **HTML 埋点清单**（仅「埋点清单」表格，无额外说明章节）。

## 必读资源

执行前先读取：

1. [reference.md](reference.md) — 事件、字段、页面模板规则（人类可读）
2. [reference_data.json](reference_data.json) — Excel 全量提取 + 扩展属性（13 事件 + 13 页面范例 + 全局后端埋点）
3. [extended_attrs.json](extended_attrs.json) — Skill 扩展事件属性（非 Excel 原规范）
4. [template.html](template.html) — HTML 输出模板（7 列表格 + 一键复制数据行）
5. [examples.md](examples.md) — discover_page / work_detail_page 示例

源规范：`source/副本-5【odirouter】埋点方案与开发计划.xlsx`（Sheet「事件自定义属性」「开发计划」）

## 工作流程

```
截图分析 → 确定 page_id → 匹配页面模板 → 识别 UI 元素 → 生成埋点行 → 输出 HTML
```

### Step 1：分析截图

识别并列出：

- 页面类型（首页 / 列表 / 详情 / 表单 / 弹窗层 / 刷游戏流等）
- 区域：`top_nav`、`left_nav`、`middle_content`、`bottom_nav`、`chat` 等
- 可交互元素：按钮、Tab、输入框、下拉、卡片、弹窗
- 列表/Feed：是否需批量曝光（`element_content` JSON 数组）
- 用户是否标注/red arrow 指向的元素（优先单独成行）

**业务排除（用户明确时）：**

- **游戏游玩区域**（类似抖音 刷视频，我方刷小游戏）：游戏内交互**不做埋点**，只埋页面壳层（作者、互动栏、评论区等）
- 左侧预览/模拟器若仅为游戏展示，同上

若用户未给 `page_id`，按 `{功能}_page` snake_case 命名（如 `discover_page`、`work_detail_page`）。

若用户要求某页所有事件带 `work_id`（如作品详情），**每一行**上报参数均须含 `work_id={作品id}`。

### Step 2：匹配 Excel 页面模板

在 [reference_data.json](reference_data.json) 的 `pages` 中找最相似页面，优先复用其埋点结构与参数写法：

| 页面场景 | 参考 page_id |
|----------|--------------|
| 未登录公共首页 | `public_home_page` |
| 登录后首页 | `home_page` |
| 模型/内容列表 | `model_page` |
| 对话/输入 | `playground_page` |
| 登录注册 | `login_page` |
| API Key 管理 | `apikey_page` |
| 定价 | `pricing_page` |
| 模型/作品详情 | `model_detail_page` |

**每个页面试点基线（有则必含）：**

1. `{页面中文名}-曝光` → `log_page_expose_client`
2. `{页面中文名}-离开` → `log_page_leave_client` + `duration`
3. 若有顶栏 → `{页面中文名}-顶部导航点击` → `log_click_client` + `element_pos=top_nav`
4. 若有侧边栏 → `{页面中文名}-侧边栏点击` → `element_pos=left_nav`
5. 若有奖励任务弹窗 → 曝光 + 点击（`element_module=reward_task`）
6. 若有列表 Feed → 批量曝光 + 单项点击
7. 若有弹窗/抽屉/下拉菜单 → **曝光 + 弹窗内点击**（见下方「弹窗埋点规则」，缺一不可）

只输出截图中**可见或合理推断存在**的埋点；边界态（空状态、加载失败）仅在截图出现或用户要求时添加。

### 弹窗 / 下拉 / 抽屉埋点规则（硬性）

**原则：有弹窗曝光，几乎一定有弹窗内点击。** 设计弹窗类埋点时，曝光与点击必须成对出现，**禁止只写曝光不写点击**。

| 步骤 | 事件 | 说明 |
|------|------|------|
| 1. 弹窗曝光 | `log_element_expose_client` | 弹窗/菜单/抽屉展示时上报 |
| 2. 弹窗内点击 | `log_click_client` | 弹窗内每个可交互项的上报 |

**写法：**

```
{页面}-{弹窗名}曝光     → element_module={弹窗模块}  element_name={弹窗模块}_expose
{页面}-{菜单项A}点击     → element_module={弹窗模块}  element_name={菜单项key}
{页面}-{菜单项B}点击     → …
```

**拆分 vs 合并：**

- 菜单项 ≤ 3 个、且均为次要入口 → 可合并为一行点击，`element_name={点击什么报什么}` + 注释枚举
- 菜单项 ≥ 4 个、或有重要转化项（设置、创作者中心、登录等）→ **每项单独一行**
- 用户 red arrow 标注的菜单项 → **必须单独一行**

**常见遗漏（生成后自检）：**

- 只写了「XX 弹窗曝光」，忘记补弹窗内各按钮/链接的点击行
- 弹窗由侧边栏/顶栏某按钮触发：触发按钮记在导航点击行；弹窗本体用独立 `element_module`

**示例（discover_page「更多」弹窗）：**

| 埋点信息 | 事件 |
|----------|------|
| 发现页-更多弹窗曝光 | log_element_expose_client |
| 发现页-更多弹窗上-关于 SeaMe 点击 | log_click_client |
| 发现页-更多弹窗上-条款隐私点击 | log_click_client |
| …（弹窗内其余菜单项各一行，均带「更多弹窗上」前缀） | log_click_client |

### Step 3：选择事件与字段

**事件后缀：** `_client` = 前端，`_server` = 后端。截图页面默认只用前端事件：

| 事件 | 用途 |
|------|------|
| `log_page_expose_client` | 页面曝光 |
| `log_page_leave_client` | 页面离开 |
| `log_click_client` | 点击 |
| `log_element_expose_client` | 元素/弹窗/列表曝光 |

**公共参数（几乎每行都有）：**

```
current_page_name = {page_id}
ref_page_url={前页的url}
```

**命名规则：**

- `element_pos`：页面区域（`top_nav` / `middle_content` / `left_nav` / `bottom_nav` / `chat`），**不是**列表序号
- `element_module`：功能模块（`reward_task`、`category_tab`、`work_comment` 等），可新增，保持 snake_case
- `element_name`：具体元素，**点击什么报什么**；曝光常用 `{module}_expose`
- `element_content`：补充内容、Tab 展示名、prompt、JSON 曝光列表
- 注释用 `#`，写在参数行末尾

**参数规则（Excel 基准 + 允许扩展）：**

Excel「事件自定义属性」是**基准字段库**，优先复用。当产品语义更清晰时，**可以扩展新参数**，命名建议：

- snake_case，贴合业务（如 `comment_id` 优于复用 `post_id` 表示评论）
- 与同类页面/事件命名风格一致
- 扩展后登记到 [extended_attrs.json](extended_attrs.json)，并运行 `scripts/update_reference.py` 合并进 `reference_data.json`

**HTML 输出标记（硬性）：**

| 参数来源 | 判定方式 | HTML 输出样式 |
|----------|----------|---------------|
| Excel 原规范 | `reference_data.json` → `events.{事件}.attrs` 中**无** `extended` | 正常黑色 |
| 扩展参数 | 不在 Excel 原规范中（含 `extended_attrs.json` 登记的） | 参数名 **红色加粗** |

扩展参数在 HTML 中写法：

```html
<span class="param-ext">comment_id</span>={评论id}
```

> 目的：开发/评审一眼区分「规范已有字段」与「产品新增字段」。复制进 Excel 后仅为纯文本，红色标记用于 HTML 评审稿。

**禁止：** 使用未在 Excel 且未登记的临时字段名；应优先选 Excel 已有字段，不够用时扩展并标红。

### Step 4：编写埋点行

每行 **7 列**（Excel「开发计划」6 列 + 第 2 列插入「页面截图」）：

| 列 | 说明 |
|----|------|
| 埋点信息 | `{页面中文名}-{所在位置/容器}-{行为}`，**尽可能写详细** |
| 页面截图 | 占位列，默认 `-` |
| 页面标识 | snake_case page id |
| 埋点事件 | 事件名 |
| 上报时机 | 简短中文 |
| 上报参数详情 | 每参数一行，带 `# 注释` |
| 前后端埋点 | 默认「前端上报」 |

**埋点信息命名（尽可能详细）：**

- 格式：`{页面中文名}-{所在位置/容器}-{具体元素/行为}`
- 弹窗内点击须标明弹窗：`{页面}-{弹窗名}上-{菜单项}点击`，如 `发现页-更多弹窗上-联系我们点击`
- 卡片内交互须标明卡片：`{页面}-作品卡片上-{操作}点击`，如 `发现页-作品卡片上-点赞点击`
- 避免歧义：单独写「联系我们点击」不够清晰，须体现它发生在哪个 UI 容器上

**合并 vs 拆分：**

- 同类顶栏按钮 → 一行汇总，`element_name={点击什么报什么}` + 注释枚举
- 重要转化按钮、用户箭头标注项、下拉菜单项 → **单独一行**
- 弹窗 / 下拉 / 抽屉：**曝光一行 + 弹窗内点击（至少一行，重要菜单项逐项拆分）**——有曝光必有点击，见「弹窗埋点规则」

### Step 5：输出 HTML 文件

**必须基于 [template.html](template.html) 完整复制**，包含：

| 组件 | 要求 |
|------|------|
| 7 列表头 | 埋点信息 / **页面截图** / 页面标识 / 埋点事件 / 上报时机 / 上报参数详情 / 前后端埋点 |
| 页面截图列 | 每行填 `-` |
| `id="tracking-table"` | 复制脚本依赖 |
| **一键复制数据行** 按钮 | 见下方复制规范 |
| `.param-ext` 样式 | 扩展参数红色加粗 |
| 复制脚本 | 内联 `<script>`，与 template 保持一致 |

**编写 tbody 行：**

1. 参数列 `class="params"`，每条参数独占一行（HTML 源码中换行）
2. 注释 `<span class="comment"># ...</span>`
3. **扩展参数**（不在 Excel 原规范中）：参数名必须用 `<span class="param-ext">param_name</span>` **红色加粗**
4. 事件名、page_id 用 `<code>` 包裹
5. 写入：`{page_id}_埋点开发计划.html`

**一键复制数据行规范：**

- 按钮文案：**「一键复制数据行」**
- **仅复制 `<tbody>` 数据行**，不含表头（便于粘贴到已有 Excel「开发计划」Sheet）
- 优先 **CF_HTML** 表格格式写入剪贴板（Excel 列对齐）
- 单元格多行参数：复制时转为 `<br style="mso-data-placement:same-cell;">`
- 备选 **TSV**（含换行的字段自动加双引号）

**只输出埋点清单表格**，不附加页面说明、修订记录等章节。

### 维护脚本

| 脚本 | 用途 |
|------|------|
| `scripts/update_reference.py` | Excel 更新后刷新 `reference_data.json`，自动合并 `extended_attrs.json` |
| `scripts/sync_html_shell.py` | template 外壳（复制按钮/样式/脚本）变更后，同步到已有 `*_埋点开发计划.html` |

## 质量检查

- [ ] 事件名均来自 reference，未自造 `_client` 事件
- [ ] `current_page_name` 与页面标识一致
- [ ] `element_pos` 未混用为列表序号
- [ ] Excel 原规范字段正常显示；**不在 Excel 中的扩展参数**已用 `param-ext` 红色加粗
- [ ] 7 列齐全，「页面截图」列均为 `-`
- [ ] 游戏区域内交互未误埋（用户要求排除时）
- [ ] 用户要求的 `work_id` 等业务字段已覆盖所有行
- [ ] 含「一键复制数据行」按钮，复制后仅数据行、可粘贴 Excel
- [ ] **每个弹窗/下拉/抽屉曝光行，均已配套弹窗内点击行**（有曝光必有点击）

## 用户可选输入

- 指定 `page_id` 或页面中文名
- 指定输出路径
- 要求拆分/合并某些埋点
- 要求全事件带 `work_id` 等业务 id
- 要求排除游戏区域埋点
- 要求补充后端 `_server` 埋点（参考 `reference_data.json` → `_global`）

默认：**仅前端埋点 + HTML 输出**。
