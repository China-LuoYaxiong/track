# 示例：discover_page（SeaVerse 发现页）

输入：页面截图（顶栏 + 创作输入框 + 分类 Tab + 作品卡片流 + Start Chat 下拉「前往创作平台」）

输出：`discover_page_埋点开发计划.html`（14 条，仅埋点清单）

## 页面标识

`discover_page`

## 与 Excel 模板的映射

| 截图模块 | 参考模板 | 本页 adaptation |
|----------|----------|-----------------|
| 顶栏 | home_page top_nav | + open_in_app、start_chat、start_chat_dropdown_toggle |
| Start Chat 下拉 | apikey_page 弹窗模式 | 曝光 + 菜单项点击（成对） |
| 更多弹窗 | 侧边栏 more 触发 | element_module=more_menu；曝光 + 各菜单项点击各一行 |
| 分类 Tab | model_page category_tab | tab_key: hot/latest/crazy... |
| 作品卡片流 | model_page model_expose/click | work_expose/work_click + work_id |
| 创作输入 | playground_page chat | element_module=create_input |

## 埋点列表摘要

| 埋点信息 | 事件 |
|----------|------|
| 发现页-曝光 | log_page_expose_client |
| 发现页-离开 | log_page_leave_client |
| 发现页-顶部导航点击 | log_click_client |
| 发现页-Start Chat 下拉曝光 | log_element_expose_client |
| 发现页-前往创作平台点击 | log_click_client |
| 发现页-创作输入框聚焦 | log_click_client |
| 发现页-创作能力标签点击 | log_click_client |
| 发现页-创作输入提交 | log_click_client |
| 发现页-分类 Tab 点击 | log_click_client |
| 发现页-作品卡片曝光 | log_element_expose_client |
| 发现页-作品卡片点击 | log_click_client |
| 发现页-卡片内交互点击 | log_click_client |
| 发现页-列表加载失败曝光 | log_element_expose_client |
| 发现页-列表空状态曝光 | log_element_expose_client |
| 发现页-更多弹窗曝光 | log_element_expose_client |
| 发现页-更多弹窗上-各菜单项点击 | log_click_client（关于 SeaMe、条款隐私、联系我们、FAQ、创作者中心、设置 各一行） |

## 关键参数示例

**前往创作平台（用户箭头标注项，单独成行）：**

```
element_pos=top_nav
element_module=start_chat_dropdown
element_name=go_to_create_platform
element_content=前往创作平台
```

**作品卡片曝光（批量 JSON）：**

```
element_module=work_expose
element_name=work_card_expose
element_tab={当前 tab_key}
element_content=[{work_id:"xxx", game_id:"xxx", pos:0}, ...]
```

完整 HTML 见 [examples/discover_page_埋点开发计划.html](examples/discover_page_埋点开发计划.html)。

---

# 示例：work_detail_page（作品详情页）

输入：刷小游戏流右侧信息栏（作者、关注、点赞/收藏/分享/改编、评论区）

输出：`work_detail_page_埋点开发计划.html`（11 条）

## 特殊规则

- **左侧游戏区域不做埋点**（游戏内交互不管）
- **所有事件带 `work_id`**
- 评论相关用扩展属性 `comment_id`（红色加粗），作者用 `author_id`

## 埋点列表摘要

| 埋点信息 | 事件 |
|----------|------|
| 作品详情页-曝光 / 离开 | log_page_expose_client / log_page_leave_client |
| 作品详情页-作者区点击 / 关注点击 | log_click_client |
| 作品详情页-互动栏点击 / 改编点击 | log_click_client |
| 作品详情页-评论区曝光 | log_element_expose_client |
| 作品详情页-评论点赞/回复/输入聚焦/提交 | log_click_client |

完整 HTML 见 [examples/work_detail_page_埋点开发计划.html](examples/work_detail_page_埋点开发计划.html)。
