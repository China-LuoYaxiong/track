# GP0102 运营-平台-游戏埋点需求对接 — 参考文档

> **源文件**: 【GP0102】运营-平台-游戏需求对接.xlsx
> **用途**: 作为后续提炼为 Skill 的参考文档，涵盖埋点规范、事件表结构、字段定义、流程标准等核心知识。

---

## 1. 文档概览

本文档是一份游戏数据埋点（tracking）需求对接与验收管理表，服务于一款 **蚂蚁主题策略游戏**（蚁国），同时覆盖 **海外服** 和 **国服** 两个运营环境。

### 1.1 Sheet 结构

| Sheet 名称 | 行数 | 列数 | 状态 |
|---|---|---|---|
| 海外服打点需求（启用中） | 1023 | 25 | 活跃 |
| 国服打点需求（启用中） | 469 | 25 | 活跃 |
| 海外服打点需求(旧)🔒 | — | — | 归档（只读） |
| 国服打点需求(旧)🔒 | — | — | 归档（只读） |

### 1.2 需求统计

| 维度 | 海外服 | 国服 |
|---|---|---|
| 活跃需求数 | 67 | 29 |
| 新接埋点 | 主要类别 | 主要类别 |
| 异常数据修复 | 有 | 有 |

### 1.3 需求对接排期流程（4 阶段）

```
需求发起 → 需求对接 → 项目组研发排期 → 需求验收
```

| 阶段 | 负责人 | 表格列 | 说明 |
|---|---|---|---|
| 需求发起 | 需求人 | A~H | 填写日期、埋点类别、需求人、埋点需求、优先级、预期上线时间、需求详情、打点时机 |
| 需求对接 | 平台数据产品 | I~O | 填写属性类型、上报字段、字段中文名、字段类型、属性描述、埋点数据表、需求确认 |
| 研发排期 | 项目组负责人员 | P~S | 填写开发人员、预计完成时间、进度、事件名 |
| 需求验收 | 平台数据分析 → 项目组 | T~W | 验收人员、验收结果、验收备注、反馈结果 |

**验收流程**：
- 验收通过 → 数据分析同步对接群 @项目组及平台 PM
- 验收未通过 → 数据分析同步未通过项 → 研发修改 → 再次验收

---

## 2. 表格字段定义（列 A~W）

| 列序 | 列名 | 负责方 | 说明 |
|---|---|---|---|
| A | 日期 | 需求人 | 需求发起日期 |
| B | 埋点类别 | 需求人 | `新接埋点` / `异常数据` / `异常修复` |
| C | 需求人 | 需求人 | 发起人姓名 |
| D | 埋点需求 | 需求人 | 需求标题/名称 |
| E | 优先级 | 需求人 | `S` / `A` / `B` / `C`（S 最高） |
| F | 预期上线时间 | 需求人 | 目标上线日期 |
| G | 需求详情 | 需求人 | 详细描述，包括背景、目标、预期行为 |
| H | 打点时机 | 需求人 | 触发埋点的具体时机（如"兑换时"、"战斗结束时"） |
| I | 属性类型 | 平台数据产品 | 数据属性分组（如"玩家基本信息"、"行为数据"） |
| J | 上报字段 | 平台数据产品 | 字段英文名 |
| K | 字段中文名 | 平台数据产品 | 字段中文说明 |
| L | 字段类型 | 平台数据产品 | `string` / `int` / `bigint` / `json` / `double` 等 |
| M | 属性描述/属性值/备注 | 平台数据产品 | 字段含义、取值规范、JSON 示例 |
| N | 埋点数据表 | 平台数据产品 | 目标数据表名（如 `log_game_step`） |
| O | 需求确认 | 平台数据产品 | `已确认` / 空 |
| P | 开发人员 | 项目组 | 负责开发的人员 |
| Q | 预计完成时间 | 项目组 | 开发完成日期 |
| R | 进度 | 项目组 | `已完成` / 进行中描述 |
| S | 事件名 | 项目组（研发填） | 游戏端定义的 action / event 标识 |
| T | 验收人员 | 数据分析 | 负责验收的人员 |
| U | 验收结果 | 数据分析 | `通过` / `未通过` / `未修改` |
| V | 验收备注 | 数据分析 | 验收详情、问题说明 |
| W | 反馈结果 | 项目组 | 修改说明（需加反馈日期） |

---

## 3. 埋点事件表（Event Tables）汇总

### 3.1 核心事件表一览

以下是文档中涉及的所有埋点数据表，按使用频率排列：

| 事件表 | 用途 | 海外服引用次数 | 国服引用次数 |
|---|---|---|---|
| `log_game_step` | 行为漏斗/步骤追踪 | 9 | 3 |
| `log_item` | 道具变动日志 | 7 | 7 |
| `log_resource` | 资源变动日志 | 6 | 6 |
| `log_activity_score` | 活动积分日志 | 8 | 3 |
| `log_missions` | 行军/出征日志 | 4 | 1 |
| `log_battle` | 战斗日志 | 1 | 1 |
| `log_alliance_buildings` | 联盟建筑日志 | 2 | 2 |
| `log_server_score` | 服务器积分日志 | 2 | 2 |
| `log_update_payments` / `payments` | 支付订单日志 | 3+2 | 1+1 |
| `log_item_exchange` | 道具兑换日志 | 1 | — |
| `log_goods_event` | 商城展示事件 | 1 | — |
| `log_fly` | 迁城日志 | 1 | — |
| `log_task` | 任务日志 | 1 | — |
| `log_hero` | 英雄日志 | — | 1 |
| `log_hero_skill` | 英雄技能日志 | 1 | 1 |
| `log_evolve` | 进化日志 | 1 | — |
| `log_intensify` | 强化/异化日志 | 2 | — |
| `log_energy` | 体力日志 | — | 1 |
| `log_bind_accounts` | 绑定账号日志 | 1 | — |
| `log_login_role` | 登录/登出日志 | 1 | — |
| `log_update_alliances` / `alliances` | 联盟信息日志 | 1+1 | 1 |
| `log_troops` | 部队日志 | 1 | — |
| `log_update_devices` | 设备信息日志 | 1 | — |

### 3.2 通用字段（所有事件表共有）

每个事件表都包含 **玩家基本信息** 作为基础维度字段：

| 字段 | 说明 |
|---|---|
| `account_id` / `acc_id` | 平台账号 ID |
| `role_id` | 角色 ID |
| `name` / `role_name` | 角色昵称 |
| `server_id` | 服务器 ID |
| `alliance_id` | 玩家所属联盟 ID |
| `base_level` | 玩家当前基地等级 |
| `created_at` | 事件发生时间戳（部分表） |

---

## 4. 各事件表详细字段结构

### 4.1 log_game_step — 行为漏斗追踪

用于追踪玩家在游戏中的关键行为步骤和漏斗转化。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 行为数据 | `step_type` | 漏斗类型/行为类型 | string | 标记行为大类（如赛季 ID、活动 ID） |
| 行为数据 | `step_id` | 漏斗 ID/行为 ID | string | 标记具体行为步骤 |
| 行为数据 | `value` | 具体行为 | string | 行为的具体值/参数 |
| 行为数据 | `behavior_id` | 行为 ID | string | 读取游戏配置，标记行为 |

**典型使用场景**：
- 赛季相关打点（`step_type` = 赛季 ID 如 `100100000`）
- 商城入口点击追踪（`step_id` = `openBuildRecruit_from_xxx`）
- 特化蚁孵化界面入口追踪
- 玩家登录/登出行为

### 4.2 log_item — 道具变动日志

追踪道具的获取与消耗。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 道具信息 | `item_id` | 道具 ID | int | 读取游戏道具配置 |
| 道具信息 | `nums` | 改变量 | int | 获取为正数，消耗为负数 |
| 道具信息 | `balance` | 累积量 | int | 变动后道具存量 |
| 行为字段 | `action` | 引发事件 | string | 区分道具变动原因 |
| 行为字段 | `action_id` | 关联 ID | string | 关联的订单 ID / 邮件 ID 等 |

**action 规范示例**：
- `100001` — 购买获得蚁国币
- `100002` — 消费蚁国币购买
- `100006` — prize 礼包
- `100007~100010` — 区域祈福活动相关
- `10891` — 特化蚁普通奖励
- `10892` — 特化蚁派遣额外奖励

### 4.3 log_resource — 资源变动日志

追踪游戏资源的变动（结构与 log_item 类似）。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 资源信息 | `resource_id` | 资源 ID | int | 读取游戏配置 |
| 资源信息 | `nums` | 改变量 | int | 获取为正，消耗为负 |
| 资源信息 | `balance` | 累积量 | int | 变动后存量 |
| 行为字段 | `action` | 引发事件 | string | 区分资源变动原因 |
| 行为字段 | `action_id` | 关联 ID | string | 关联 ID |

**action 规范示例**：
- `100003` — 通过 37 充值返利获得钻石
- `100011` — 钻石瓜分活动

### 4.4 log_activity_score — 活动积分日志

追踪各类活动的积分变动。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 积分数据 | `ac_id` | 活动 ID | int/string | 读取游戏配置 |
| 积分数据 | `ac_round` | 活动轮次 | int | 1/2/3... 若无轮次记录 UTC 时间戳 |
| 积分数据 | `score` | 贡献总分 | int | 结算值 |
| 积分数据 | `rank` | 排名 | int | 排名 |
| 积分数据 | `behavior_id` | 行为 ID | string | 标记达成积分档位 |
| 行为字段 | `action` | 引发事件 | string | 区分积分来源 |
| 奖励数据 | — | 档位详情 | string (json) | `{"ac_id":"xxx","award_node":xxx,"node_type":xxx}` |

### 4.5 log_missions — 行军/出征日志

追踪玩家行军出征行为。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 行军信息 | `troops_id` | 队伍 ID | string | — |
| 行军信息 | `category` | 行军类型 | int | 区分行军类型（区域祈福、打野等） |
| 行军信息 | `is_return` | 是否返回 | int | 1:返回，0:出征 |
| 行军信息 | `finish_time` | 最终结束时间 | int | — |
| 行军信息 | `start_x` / `start_y` | 起始坐标 | int | — |
| 行军信息 | `stop_x` / `stop_y` | 目标坐标 | int | — |
| 行军信息 | `actual_x` / `actual_y` | 实际到达坐标 | int | — |
| 行军信息 | `battle_id` | 对决对象 ID | string | 玩家/npc 记录角色 ID；资源田/建筑记录配置 ID |
| 行军信息 | `is_mutiplayer` | 个人/集结 | int | 0:个人，1:集结 |
| 行军信息 | `army_id` | 行军详情 | string (json) | 包含野怪、英雄、兵蚁信息 |
| 行军信息 | `beast_info` | 巨兽详情 | json | `{beast_id, beast_level, beast_star}` |
| 行军信息 | `hero_info` | 出征英雄详情 | json | 含 hero_id, level, star, skills, row（站位） |
| 行为字段 | `action` | 引发事件 | string | — |
| 行为字段 | `action_id` | 关联 ID | string | — |

**行军类型 category 规范**：`28` = 区域祈福活动等

### 4.6 log_battle — 战斗日志

追踪战斗过程与结果。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 战斗数据 | — | 攻击方基本信息 | json | 包含攻击方详情 |
| 战斗数据 | — | 战斗结果 | — | — |

### 4.7 log_item_exchange — 道具兑换日志

追踪道具兑换行为。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 道具兑换 | `item_id` | 兑换的道具 ID | int | — |
| 道具兑换 | `consume_item_id` | 消耗的物品 ID | int | — |
| 道具兑换 | `consume_nums` | 消耗的物品数量 | int | — |
| 道具兑换 | `extend_1` | 兑换的物品数量 | string | — |
| 道具兑换 | `action` | 引发事件 | string | 区分兑换来源 |

### 4.8 log_alliance_buildings — 联盟建筑日志

追踪联盟建筑的建造、升级、补给等行为。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 基础信息 | `build_conf_id` | 建筑 ID | int | 读取游戏建筑配置 |
| 基础信息 | `pos` | 坐标 | int | — |
| 补充信息 | `firm_level` | 当前建筑加固等级 | int | 增幅等级 |
| 行为字段 | `action` | 引发事件 | string | 区分建造/升级/补给等 |
| 活动补充信息 | `ac_type` | 活动类型 ID | int | 读取游戏配置 |

### 4.9 log_server_score — 服务器积分日志

追踪服务器段位赛积分。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 基础信息 | `ac_id` | 活动 ID | string | 读取游戏配置 |
| 基础信息 | `ac_round` | 活动轮次 | int | — |
| 基础信息 | `score` | 贡献总分 | int | 结算值 |
| 基础信息 | `rank` | 排名 | int | — |
| 分组信息 | `opposite_server_id` | 对阵服务器 ID | string | — |
| 分组信息 | `race_type` | 赛制类型 | int | 1:正赛，2:热身赛，3:预选赛 |
| 分组信息 | `stage_group` | 段位分组 | string | 黄金/白银/青铜赛（仅正赛） |
| 分组信息 | `stage_score` | 段位分数 | int | — |
| 行为字段 | `action` | 引发事件 | string | `1116`:日结算，`1117`:周结算 |

### 4.10 log_hero / log_hero_skill — 英雄日志

追踪英雄相关行为。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 英雄信息 | `hero_id` | 英雄 ID | int | — |
| 英雄信息 | `hero_level` | 英雄等级 | int | — |
| 英雄信息 | `hero_star` | 英雄星级 | int | — |
| 行为字段 | `action` | 引发事件 | string | 如 `10167`:英雄技能突破 |

### 4.11 log_evolve / log_intensify — 进化/强化日志

追踪特化蚁进化系统。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 进化系统 | `type` | 进化类型 | int | 读取游戏配置 |
| 槽位信息 | `slot_id` | 槽位 ID | int | — |
| 行为字段 | `action` | 引发事件 | string | 进化突破/激活/分解/切换/槽位等 |
| 战力信息 | `nums` | 战力变化量 | int | 减少为负，增加为正 |

### 4.12 log_energy — 体力日志

追踪赛季体力变动。

### 4.13 log_task — 任务日志

追踪任务完成情况。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 任务基础信息 | `ac_id` | 活动 ID | string | 读取游戏配置 |
| 任务基础信息 | `ac_round` | 活动轮次 | int | — |
| 任务补充信息 | `extend_1` | 奖励详情 | string (json) | `[{"conf_id":"xxx","amount":xxx}]` |
| 行为字段 | `action` | 引发事件 | string | 如 `10890`:特化蚁完成派遣 |

### 4.14 log_update_payments / payments — 支付订单日志

追踪玩家充值与支付行为。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 蚁国币订单 | `role_id` | 角色 ID | string | — |
| 蚁国币订单 | `account_id` | 平台账号 ID | string | — |
| 蚁国币订单 | `device_id` | 设备号 | string | Android: mac 地址，iOS: appsflyer_id |
| 蚁国币订单 | `server_id` | 服务器 ID | string | — |
| 蚁国币订单 | `uuid` | 游戏唯一订单 ID | string | — |
| 蚁国币订单 | `order_id` | 平台订单 ID | string | — |
| 蚁国币订单 | `product_id` | 商品 ID | string | — |
| 蚁国币订单 | `pay_type` | 支付类型 | int | 1:内购，2:三方，3:第三方转账，4:公众号购买 |
| 蚁国币订单 | `pay_channel` | 支付渠道 | string | app_store / google_play / china_token / china_h5 等 |
| 蚁国币订单 | `currency` | 币种 | string | 美元等 |
| 蚁国币订单 | `local_price` | 当地币种金额 | double | 消费蚁国币时为 0 |
| 蚁国币订单 | `price` | 金额（美元） | double | 消费蚁国币时为 0 |
| 蚁国币订单 | `coin` | 游戏币数量 | int | 购买/消费蚁国币数量 |
| 蚁国币订单 | `charged_at` | 付款时间戳 | bigint | — |

### 4.15 log_game_mail — 游戏邮件日志

追踪邮件发放与领取。

| 属性类别 | 字段名 | 中文名 | 类型 | 说明 |
|---|---|---|---|---|
| 基本信息 | `mail_id` | 邮件唯一 ID | string | — |
| 基本信息 | `mail_type` | 邮件类型 ID | int | 联盟/活动/工作室/野怪报告等 |
| 基本信息 | `mail_show` | 邮件事件说明 ID | string | 区分 prizeID 调用等 |
| 基本信息 | `extend_1` | 邮件详情 | string (json) | `[{"item_id":xxxx,"amount":1}]` |
| 基本信息 | `extend_2` | 备注说明 | string | 如 prizeID、buy_token_china 等 |
| 行为字段 | `action` | 引发原因 | string | — |

### 4.16 log_fly — 迁城日志

追踪玩家迁城行为。

### 4.17 log_update_devices — 设备信息日志

追踪设备信息变动。

### 4.18 log_troops — 部队日志

追踪部队相关信息。

---

## 5. 属性类别（Attribute Categories）体系

每个事件表的字段按属性类别分组，以下是完整的属性类别体系：

### 5.1 基础维度类

| 属性类别 | 包含字段 | 说明 |
|---|---|---|
| **玩家基本信息** | account_id, role_id, role_name, server_id, alliance_id, base_level | 所有事件表必带的基础维度 |
| **联盟基本信息** | alliance_id, alliance_name, alliance_level 等 | 联盟维度信息 |
| **玩家信息** | acc_id, role_id 等 | 简化版玩家信息 |

### 5.2 行为/事件类

| 属性类别 | 包含字段 | 说明 |
|---|---|---|
| **行为数据** | step_type, step_id, value, behavior_id | log_game_step 的行为漏斗字段 |
| **行为字段** | action, action_id | 几乎所有事件表的行为标记字段 |

### 5.3 业务数据类

| 属性类别 | 包含字段 | 说明 |
|---|---|---|
| **道具信息** / **道具/资源** | item_id, nums, balance | 道具变动字段 |
| **资源信息** | resource_id, nums, balance | 资源变动字段 |
| **积分数据** | ac_id, ac_round, score, rank | 活动积分字段 |
| **奖励数据** | ac_id, award_node, node_type | 活动奖励档位 |
| **兑换数据** | item_id, consume_item_id, consume_nums | 兑换行为字段 |
| **行军信息** | troops_id, category, is_return, battle_id 等 | 行军出征字段 |
| **战斗数据** | attack_info, battle_id 等 | 战斗相关字段 |
| **建筑** | build_conf_id, pos, firm_level | 建筑相关字段 |
| **基础信息** | ac_id, race_type, opposite_server_id 等 | 活动/赛季基础字段 |
| **分组信息** | race_type, stage_group, stage_score | 赛制分组字段 |
| **英雄信息** | hero_id, hero_level, hero_star, skills | 英雄维度字段 |
| **英雄技能** | skill_id, skill_level | 英雄技能字段 |
| **野怪伙伴** | partner_id | 野怪伙伴维度 |
| **进化系统** | type, slot_id | 特化蚁进化系统 |
| **进阶天赋系统** | talent_type | 天赋系统 |
| **槽位信息** / **槽位放置信息** | slot_id | 槽位维度 |
| **战力信息** | nums (战力变化量) | 战力变动 |
| **队伍** / **队伍信息** | fight_id | 队伍/阵容维度 |
| **任务基础信息** / **任务补充信息** | ac_id, ac_round, extend_1 | 任务维度 |
| **活动基础信息** / **活动补充信息** | ac_id, ac_type | 活动维度 |
| **关卡数据** | type, level_id, sub_level_id, secs, result | 关卡/挑战维度 |
| **订阅信息** | — | 订阅相关 |
| **曝光** | conf_id_type, position, event_name, show_time | 商城曝光维度 |

---

## 6. Action 命名规范

`action` 字段是区分事件细分类型的核心字段，遵循以下命名规范：

### 6.1 数字编号 action

大型功能使用数字编号，按功能模块分配号段：

| 号段 | 功能模块 | 示例 |
|---|---|---|
| 1001~1010 | 基础玩法 | — |
| 1383 | 建筑增幅升级 | — |
| 5409 | 区域迁徙 | — |
| 6126 | 队伍返回兵量异常 | — |
| 6205~6207 | 建筑加固（加固/完成/立即完成） | — |
| 6209 | 增幅建筑立即完成 | — |
| 10001~10011 | 基础活动/道具 | 行军、37 充值返利、祈福露珠、钻石瓜分等 |
| 10143 | 跨区召集 | — |
| 10167~10168 | 英雄技能突破/返还 | — |
| 10218~10222 | 落潮海岸活动 | 抽奖/一键抽奖/攻击怪物 |
| 10342~10348 | 批量操作 | 一键急速/发展技能/补充/收获等 |
| 10372~10375 | 黑 5 积分商店 | 购买积分/兑换英雄/野怪 |
| 10703~10704 | 投票活动 | 投票/取消投票 |
| 10860~10862 | 特化蚁进化 | 进化/突破/均衡突破 |
| 10869 | 特化蚁进化技能进阶 | — |
| 10890~10892 | 特化蚁派遣 | 完成派遣/普通奖励/额外奖励 |
| 10916 | 活跃奖励重置刷新 | — |
| 1116~1117 | 服务器积分结算 | 日结算/周结算 |
| 11201 | 自动集结加入 | — |
| 11300~11302 | 野怪伙伴 | 合成/升级/孵化 |
| 11330 | 感染蚁试炼奖励 | — |
| 11344~11346 | 追赶系统 | 领取奖励/积分变化/排行榜 |
| 11370~11374 | 进阶/火晶系统 | 进阶突破/天赋激活/重置/领奖等 |
| 11391~11395 | 魔芋州活动 | 驻扎积分/战斗积分/争夺期日志 |
| 11400 | 四赛季 NPC 建筑补给值 | — |
| 11407 | 火晶系统预告领奖 | — |
| 11448~11450 | 化石系统 | 解锁/升级/子等级 |
| 11501 | 自动集结行军 | — |
| 12001 | 加速溢出返还道具 | — |
| 13000 | 火晶科技兑换增幅结晶碎片 | — |

### 6.2 字符串标识 action

部分功能使用字符串标识：

| action 值 | 含义 |
|---|---|
| `unlock_apc_queue` | 解锁预设队列页签 |
| `use_apc_queue` | 使用预设队列页签 |
| `web_recharge_jump_info` | 网页充值跳转信息 |
| `season_group_rest_vote` | 赛季分组投票 |
| `hero_evolution` | 英雄进化（StepType） |

### 6.3 action 命名原则

1. **唯一性**：同一事件表中，action 值必须唯一标识一种行为类型
2. **可关联**：action 需与 action_id 配合使用，action_id 关联上下文（如订单 ID、邮件 ID）
3. **版本兼容**：新增 action 时不能与已有编号冲突，按号段规则分配
4. **可读性**：字符串 action 应使用 snake_case 命名，含义明确

---

## 7. 埋点数据规范

### 7.1 数据类型规范

| 类型 | 说明 | 示例 |
|---|---|---|
| `string` | 字符串 | — |
| `int` | 整数 | — |
| `bigint` | 长整数（时间戳等） | — |
| `double` | 浮点数（金额等） | — |
| `json` | JSON 格式字符串 | 见下方 JSON 规范 |

### 7.2 JSON 格式规范

#### 道具/奖励 JSON
```json
[{"item_id": "xxxx", "amount": 1}]
```

#### 行军详情 JSON
```json
{
  "beast": "id",
  "armymsg": [
    {"heroid": 1000161, "armytype": 107003, "armyamount": 10572}
  ]
}
```

#### 英雄出征详情 JSON
```json
[
  {
    "row": "1",
    "hero_id": "xxx",
    "hero_level": "xx",
    "hero_star": "xx",
    "skills": {"skill_id": "xxx", "skill_level": "xxx"}
  }
]
```

#### 巨兽详情 JSON
```json
[{"beast_id": "AAA", "beast_level": "XXX", "beast_star": "xxx"}]
```

#### 积分档位 JSON
```json
{"ac_id": "xxx", "award_node": "xxx", "node_type": "xxx"}
```
> `node_type`: 1 = 个人积分，2 = 联盟积分

### 7.3 改变量（nums）规范

- 获取道具/资源 → `nums` 为 **正数**
- 消耗道具/资源 → `nums` 为 **负数**
- `balance` 始终记录变动后的 **当前存量**

### 7.4 时间戳规范

- `created_at`：事件发生时间戳（Unix timestamp，秒级或毫秒级）
- `charged_at`：付款时间戳
- `finish_time`：事件最终结束时间

---

## 8. 优先级定义

| 优先级 | 含义 | 说明 |
|---|---|---|
| **S** | 最高优先级 | 紧急需求，需立即处理 |
| **A** | 高优先级 | 重要需求，正常排期 |
| **B** | 中优先级 | 一般需求，可适当延后 |
| **C** | 低优先级 | 低优先级需求 |

---

## 9. 埋点类别

| 类别 | 说明 |
|---|---|
| **新接埋点** | 新增的埋点需求，需要新建事件表字段或新增 action |
| **异常数据** | 已有埋点数据异常，需要排查修复 |

---

## 10. 海外服与国服差异

| 维度 | 海外服 | 国服 |
|---|---|---|
| 需求量 | 67 条 | 29 条 |
| 特有事件表 | `log_bind_accounts`（绑定手机）、`log_login_role`（IP 记录） | — |
| 特有功能 | 公众号购买蚁国币 | 抖音 CDK 兑换、国服充值返利关联订单号 |
| 验收标准 | 与国服一致 | 国服可能有额外合规要求 |

---

## 11. 验收常见问题

从验收备注中总结的常见问题类型：

1. **字段缺失**：如 `alliance_id` 未记录、`stage_group` 为空
2. **数据对不上**：如服务器积分数不一致
3. **action 未正确区分**：如加固建筑应分两条上报不同 action
4. **JSON 格式错误**：如道具 ID、数量字段不规范
5. **时间字段问题**：如 extend_2 应记录时长而非时间戳
6. **等级字段错误**：如 `build_level` 等级有误
7. **关联 ID 缺失**：如需要关联 `log_team` 但未提供 `action_id`
8. **数据无法产生**：如特定条件下的数据上报逻辑未实现

---

## 12. Skill 提炼方向建议

基于本文档，可提炼以下类型的 Skill：

| Skill 名称 | 用途 | 核心能力 |
|---|---|---|
| **埋点需求分析** | 分析新需求应使用哪个事件表和 action | 根据需求描述匹配事件表、字段、action 编号 |
| **埋点字段定义** | 根据业务场景生成完整的字段定义 | 输出字段名、中文名、类型、描述、JSON 示例 |
| **埋点验收检查** | 检查埋点实现是否符合规范 | 验证字段完整性、数据类型、action 命名、JSON 格式 |
| **埋点数据表选择** | 根据打点时机推荐合适的事件表 | 匹配打点时机 → 事件表映射 |
| **action 编号管理** | 分配和管理 action 编号 | 检查编号冲突、按号段规则分配新编号 |
| **埋点需求文档生成** | 根据简要需求描述生成完整的埋点需求行 | 自动填充表格所有列，包括字段定义、JSON 示例 |

---

## 13. 日志表数据库结构（gp0102 日志表）

> 数据来源：gp0102日志表结构.csv，共 **119 张日志表**，以下按业务领域分类，列出每张表的用途说明和完整字段定义。

### 13.1 通用字段说明

几乎所有日志表都包含以下公共字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `pk_id` | bigint | 主键 ID（分区键） |
| `created_at` | bigint | 事件发生时间戳 |
| `save_time` | bigint | 数据入库时间戳 |
| `extend_1` ~ `extend_5` | varchar | 扩展字段（JSON 格式，用于存放动态属性） |
| `init_device_os` | varchar | 初始设备系统类型 |
| `device_os` | varchar | 设备操作系统 |
| `year` / `month` / `day` | integer | 分区日期字段 |

几乎所有面向玩家的日志表都包含以下 **玩家基础维度**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `acc_id` | varchar | 平台账号 ID |
| `role_id` | varchar | 角色 ID |
| `role_name` | varchar | 角色昵称 |
| `server_id` | varchar | 服务器 ID |
| `alliance_id` | varchar | 联盟 ID |
| `base_level` | bigint | 基地等级 |
| `role_level` | bigint | 角色等级 |

---

### 13.2 账号与登录类

#### log_accounts — 账号注册信息
记录玩家注册时的设备和渠道信息。

| 字段 | 类型 | 说明 |
|---|---|---|
| `acc_id` | varchar | 平台账号 ID |
| `channel_id` | bigint | 渠道 ID |
| `sdk_id` | varchar | SDK ID |
| `device_name` | varchar | 设备名称 |
| `device_id` | varchar | 设备 ID |
| `adid` | varchar | 广告 ID |
| `device_os` | varchar | 设备操作系统 |
| `country` | varchar | 国家 |
| `ip` | varchar | IP 地址 |
| `province` | varchar | 省份 |
| `created_at` | bigint | 注册时间 |

#### log_login_acc — 账号级登录
记录账号维度的登录事件。

| 字段 | 类型 | 说明 |
|---|---|---|
| `acc_id` | varchar | 平台账号 ID |
| `channel_id` | bigint | 渠道 ID |
| `sdk_id` | varchar | SDK ID |
| `device_name` | varchar | 设备名称 |
| `device_id` | varchar | 设备 ID |
| `adid` | varchar | 广告 ID |
| `ip` | varchar | IP 地址 |
| `app_version` | varchar | 应用版本 |
| `device_os` | varchar | 设备系统 |
| `country` | varchar | 国家 |

#### log_login_behavior — 登录行为
记录登录行为详情，包含首次登录、重连、在线时长等。

| 字段 | 类型 | 说明 |
|---|---|---|
| `device` / `device_id` / `adid` | varchar | 设备标识 |
| `level` | bigint | 角色等级 |
| `base_level` | bigint | 基地等级 |
| `ip` | varchar | IP 地址 |
| `first_login` | boolean | 是否首次登录 |
| `is_login` | boolean | 是否登录 |
| `login_mark_id` | varchar | 登录标记 ID |
| `is_reconnect` | boolean | 是否重连 |
| `ip_source` | varchar | IP 来源 |
| `online_time` | bigint | 在线时长 |
| `is_paid` | integer | 是否付费玩家 |

#### log_login_role — 角色级登录
记录角色维度的登录/登出事件，包含版本、包名等。

| 字段 | 类型 | 说明 |
|---|---|---|
| `device` / `device_id` / `adid` | varchar | 设备标识 |
| `first_login` | boolean | 是否首次登录 |
| `login_mark_id` | varchar | 登录标记 |
| `is_reconnect` | boolean | 是否重连 |
| `ip_source` | varchar | IP 来源 |
| `game_version` | varchar | 游戏版本 |
| `package_name` | varchar | 包名 |
| `gid` | varchar | GID |

#### log_logout — 登出
记录玩家登出事件和在线时长。

| 字段 | 类型 | 说明 |
|---|---|---|
| `online_time` | bigint | 本次在线时长 |
| `is_paid` | integer | 是否付费玩家 |
| `is_reconnect` | boolean | 是否重连 |
| `ip` / `ip_source` | varchar | IP 及来源 |

#### log_connects — 连接信息
记录客户端连接服务器的详细信息。

| 字段 | 类型 | 说明 |
|---|---|---|
| `game_version` / `app_version` | varchar | 游戏/应用版本 |
| `hot_update` | integer | 热更新标识 |
| `is_server_down` | boolean | 服务器是否宕机 |
| `method` | varchar | 连接方式 |
| `login_suc` | bigint | 登录是否成功 |
| `err` | varchar | 错误信息 |
| `ip_source` | varchar | IP 来源 |
| `is_reconnect` | boolean | 是否重连 |

#### log_create_role — 创建角色
按服务器统计创建角色数量。

| 字段 | 类型 | 说明 |
|---|---|---|
| `users` | bigint | 创建角色数 |
| `interval` | bigint | 统计间隔 |

#### log_update_accounts — 账号信息更新
记录账号绑定、封禁等变更。

| 字段 | 类型 | 说明 |
|---|---|---|
| `uuid` | varchar | 唯一标识 |
| `platform` | integer | 平台类型 |
| `platform_id` | varchar | 平台 ID |
| `ban_expire` | bigint | 封禁到期时间 |
| `bind` | boolean | 是否绑定 |
| `is_delete` | boolean | 是否删除 |
| `init_server_id` | varchar | 初始服务器 |

#### log_update_roles — 角色信息更新（50 列）
全量记录角色状态快照，用于维度分析。

| 字段 | 类型 | 说明 |
|---|---|---|
| `uuid` | varchar | 唯一标识 |
| `account_id` | varchar | 平台账号 |
| `power` | bigint | 战力 |
| `energy` | bigint | 体力 |
| `vip_level` | integer | VIP 等级 |
| `officer` | varchar | 官职 |
| `career` | varchar | 职业 |
| `buildings_power` | bigint | 建筑战力 |
| `armies_power` | bigint | 部队战力 |
| `techs_power` | bigint | 科技战力 |
| `is_internal` | boolean | 是否内部号 |
| `forbid` | boolean | 是否封禁 |
| `season_id` | varchar | 赛季 ID |
| `is_subscribed` | integer | 是否订阅 |

#### log_update_devices — 设备信息更新

| 字段 | 类型 | 说明 |
|---|---|---|
| `uuid` | varchar | 唯一标识 |
| `device_os` | varchar | 设备系统 |
| `ban_expire` | bigint | 封禁到期 |
| `device` | varchar | 设备型号 |
| `device_ad_id` | varchar | 广告 ID |
| `ip` | varchar | IP 地址 |
| `device_memory` | bigint | 设备内存 |

#### log_bind_accounts — 绑定账号

| 字段 | 类型 | 说明 |
|---|---|---|
| `open_id` | varchar | OpenID |
| `platform` | integer | 绑定平台 |
| `created_time` | bigint | 绑定时间 |

#### log_delete — 删除数据

| 字段 | 类型 | 说明 |
|---|---|---|
| `action` | varchar | 删除操作类型 |
| `checker` | varchar | 审核人 |
| `item_id` | bigint | 被删除项 ID |
| `delete_type` | integer | 删除类型 |
| `reason` | varchar | 删除原因 |

---

### 13.3 道具与资源类

#### log_item — 道具变动日志
**核心表**：记录所有道具的获取与消耗。

| 字段 | 类型 | 说明 |
|---|---|---|
| `item_id` | bigint | 道具 ID |
| `action` | varchar | 引发事件（action 编号） |
| `action_id` | varchar | 关联 ID（订单、邮件等） |
| `nums` | bigint | 改变量（正=获取，负=消耗） |
| `balance` | bigint | 变动后存量 |
| `large_nums` | varchar | 大数值存储 |
| `large_balance` | varchar | 大数值存量 |
| `is_debt` | integer | 是否欠款 |
| `unique_id` | varchar | 唯一标识 |

#### log_resource — 资源变动日志
**核心表**：记录所有资源的获取与消耗，结构与 log_item 类似。

| 字段 | 类型 | 说明 |
|---|---|---|
| `resource_id` | bigint | 资源 ID |
| `action` | varchar | 引发事件 |
| `nums` | bigint | 改变量 |
| `balance` | bigint | 变动后存量 |
| `large_nums` | varchar | 大数值存储 |
| `large_balance` | varchar | 大数值存量 |
| `is_debt` | integer | 是否欠款 |

#### log_item_exchange — 道具兑换日志
记录道具兑换行为。

| 字段 | 类型 | 说明 |
|---|---|---|
| `ac_id` | varchar | 活动 ID |
| `ac_type` / `ac_round` / `ac_stage` | bigint | 活动类型/轮次/阶段 |
| `item_id` | bigint | 兑换获得的道具 ID |
| `consume_item_id` | bigint | 消耗的道具 ID |
| `consume_nums` | bigint | 消耗数量 |
| `item_info` | varchar | 道具信息（JSON） |
| `consume_item_info` | varchar | 消耗道具信息（JSON） |
| `is_multiple` | boolean | 是否批量兑换 |
| `ac_level` | bigint | 活动等级 |

#### log_debt — 道具/资源欠款
记录道具或资源的欠款与偿还。

| 字段 | 类型 | 说明 |
|---|---|---|
| `stuff_type` | varchar | 物品类型 |
| `stuff_id` | varchar | 物品 ID |
| `operate_status` | integer | 操作状态 |
| `operator` | varchar | 操作人 |

#### log_armies — 部队日志
记录部队数量变动。

| 字段 | 类型 | 说明 |
|---|---|---|
| `army_id` | varchar | 部队 ID |
| `action` | varchar | 引发事件 |
| `nums` | bigint | 改变量 |
| `balance` | bigint | 变动后数量 |

#### log_armies_dead — 部队死亡日志
记录部队阵亡情况，字段结构与 log_armies 一致。

#### log_injured_armies — 部队受伤日志
记录部队受伤情况，字段结构与 log_armies 一致。

#### log_troops — 部队变动日志
记录部队招募、训练、升级等变动。

| 字段 | 类型 | 说明 |
|---|---|---|
| `army_type` | varchar | 部队类型 |
| `change_type` | varchar | 变动类型 |
| `army_tier` | varchar | 部队品阶 |
| `sub_change_type` | integer | 子变动类型 |
| `sub_change_balance` | bigint | 子变动余额 |
| `nums` / `balance` | bigint | 改变量/存量 |

---

### 13.4 建筑与联盟类

#### log_buildings — 建筑日志
记录建筑升级、建造、加固等行为。

| 字段 | 类型 | 说明 |
|---|---|---|
| `function_id` | bigint | 功能 ID |
| `pos` | bigint | 建筑位置 |
| `build_conf_id` | bigint | 建筑配置 ID |
| `build_level` | bigint | 当前等级 |
| `old_level` | bigint | 变更前等级 |
| `firm_level` | integer | 加固等级 |
| `firm_old_level` | integer | 变更前加固等级 |
| `value` | varchar | 当前值 |
| `last_value` | bigint | 变更前值 |
| `progress` / `last_progress` | integer | 建造进度 |

#### log_alliance_buildings — 联盟建筑日志
记录联盟建筑的建造、升级、补给。

| 字段 | 类型 | 说明 |
|---|---|---|
| `build_conf_id` | integer | 建筑配置 ID |
| `pos` | integer | 位置 |
| `build_level` / `build_old_level` | integer | 当前/变更前等级 |
| `build_exp` / `last_build_exp` | bigint | 建筑经验 |
| `value` / `last_value` | varchar/bigint | 当前/变更前值 |

#### log_build_occupy — 建筑占领

| 字段 | 类型 | 说明 |
|---|---|---|
| `build_id` | bigint | 建筑 ID |
| `pos` | bigint | 位置 |
| `action` | varchar | 占领/放弃等 |

#### log_alliance_change — 联盟变动
记录联盟成员加入、退出、职位变动。

| 字段 | 类型 | 说明 |
|---|---|---|
| `alliance_level` | varchar | 联盟等级 |
| `alliance_short` | varchar | 联盟简称 |
| `alliance_name` | varchar | 联盟名称 |
| `action` | varchar | 变动类型 |

#### log_update_alliances — 联盟信息全量更新（33 列）
全量记录联盟状态快照。

| 字段 | 类型 | 说明 |
|---|---|---|
| `alliance_roles` | integer | 联盟人数 |
| `alliance_power` | double | 联盟战力 |
| `alliance_tag` | varchar | 联盟标签 |
| `alliance_owner_id` / `alliance_owner_name` | varchar | 盟主信息 |
| `alliance_level` | varchar | 联盟等级 |
| `alliance_kill` | bigint | 联盟击杀 |
| `alliance_activity_score` | bigint | 联盟活动积分 |
| `alliance_mass_nums` | bigint | 联盟集结次数 |
| `alliance_declaration` | varchar | 联盟宣言 |
| `alliance_announcement` | varchar | 联盟公告 |
| `alliance_messageboard` | varchar | 联盟留言板 |
| `alliance_status` | integer | 联盟状态 |

#### log_alliance_award — 联盟奖励

| 字段 | 类型 | 说明 |
|---|---|---|
| `award_type` | bigint | 奖励类型 |
| `award_node` | bigint | 奖励节点 |
| `action` | varchar | 引发事件 |

#### log_alliance_rank — 联盟排名

| 字段 | 类型 | 说明 |
|---|---|---|
| `alliance_rank` | bigint | 联盟排名 |
| `alliance_score` | bigint | 联盟积分 |
| `rank_type` | bigint | 排名类型 |
| `alliance_stage` | varchar | 联盟段位 |
| `ac_cycle` | bigint | 活动周期 |
| `ac_group` | varchar | 活动分组 |
| `time_session` | bigint | 时间段 |

#### log_alliance_resource — 联盟资源

| 字段 | 类型 | 说明 |
|---|---|---|
| `resource_id` | integer | 资源 ID |
| `nums` / `balance` | bigint | 改变量/存量 |

#### log_alliance_score — 联盟积分

| 字段 | 类型 | 说明 |
|---|---|---|
| `nums_type` | integer | 积分类型 |
| `nums` / `balance` | bigint | 变动量/存量 |
| `award_node` | bigint | 奖励节点 |

#### log_alliance_task — 联盟任务

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | varchar | 任务 ID |
| `task_type` | integer | 任务类型 |
| `daily_task_num` | bigint | 每日任务数 |
| `success_id` | varchar | 完成标识 |
| `map_id` | varchar | 地图 ID |

#### log_alliance_tech — 联盟科技

| 字段 | 类型 | 说明 |
|---|---|---|
| `tech_id` | bigint | 科技 ID |
| `tech_level` / `tech_last_level` | bigint | 当前/变更前等级 |

---

### 13.5 英雄与技能类

#### log_hero — 英雄日志（39 列）
记录英雄获取、升级、升星等全生命周期。

| 字段 | 类型 | 说明 |
|---|---|---|
| `hero_type` | integer | 英雄类型 |
| `hero_id` | integer | 英雄 ID |
| `position` | integer | 出战位置 |
| `hero_level` | integer | 英雄等级 |
| `hero_star` | integer | 英雄星级 |
| `hero_power` | bigint | 英雄战力 |
| `hero_intensify_level` | integer | 强化等级 |
| `event_type` | integer | 事件类型 |
| `hero_score` | bigint | 英雄积分 |
| `pos_id` / `pos_level` | varchar/bigint | 槽位信息 |
| `hero_sub_star` | integer | 子星级 |
| `hero_evolve_level` | integer | 进化等级 |
| `exp_nums` / `exp_balance` | bigint | 经验变动/存量 |
| `premium_level` / `last_premium_level` | bigint | 高级等级 |

#### log_hero_skill — 英雄技能日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `hero_type` / `hero_id` | integer | 英雄类型/ID |
| `hero_level` / `hero_star` | integer | 等级/星级 |
| `skill_id` | integer | 技能 ID |
| `skill_last_level` / `skill_level` | integer | 变更前/当前技能等级 |
| `skill_status` | integer | 技能状态 |
| `hero_sub_star` | integer | 子星级 |

#### log_hero_cell — 英雄细胞日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `cell_type` | integer | 细胞类型 |
| `hero_cell_id` | integer | 细胞 ID |
| `hero_id` | integer | 所属英雄 |
| `cell_level` / `cell_star` | integer | 细胞等级/星级 |
| `cell_break_level` | integer | 突破等级 |
| `is_dress` / `is_del` | integer | 是否穿戴/删除 |
| `cell_evolve` | integer | 进化值 |

#### log_hero_haved — 英雄拥有日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `hero_id` | bigint | 英雄 ID |
| `action` | varchar | 获取/分解等 |

#### log_hero_synergy — 英雄协同日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `synergy_id` | integer | 协同 ID |
| `synergy_type` | varchar | 协同类型 |
| `synergy_level` / `synergy_last_level` | integer | 当前/变更前等级 |

#### log_hero_tmp — 英雄临时日志
结构与 log_hero 类似，用于临时数据记录。

---

### 13.6 活动与积分类

#### log_activity_score — 活动积分日志
**核心表**：记录各类活动的积分变动。

| 字段 | 类型 | 说明 |
|---|---|---|
| `ac_id` | varchar | 活动 ID |
| `ac_type` | bigint | 活动类型 |
| `ac_round` | bigint | 活动轮次 |
| `ac_stage` | bigint | 活动阶段 |
| `award_node` | bigint | 奖励节点 |
| `nums` | bigint | 积分变动量 |
| `balance` | bigint | 积分存量 |
| `large_nums` / `large_balance` | varchar | 大数值存储 |
| `ac_cycle` | bigint | 活动周期 |
| `ac_group` | varchar | 活动分组 |

#### log_activity_award — 活动奖励

| 字段 | 类型 | 说明 |
|---|---|---|
| `award_node` | bigint | 奖励节点 |
| `ac_cycle` | bigint | 活动周期 |
| `action` | varchar | 引发事件 |

#### log_activity_join — 活动参与

| 字段 | 类型 | 说明 |
|---|---|---|
| `ac_stage_begin` / `ac_stage_end` | bigint | 活动阶段起止 |
| `ac_event` | varchar | 活动事件 |
| `ac_group` | varchar | 活动分组 |
| `ac_mode` | varchar | 活动模式 |

#### log_role_rank — 角色排名

| 字段 | 类型 | 说明 |
|---|---|---|
| `role_rank` | integer | 角色排名 |
| `role_score` | integer | 角色积分 |
| `rank_type` | integer | 排名类型 |
| `ac_cycle` | integer | 活动周期 |
| `ac_group` | varchar | 活动分组 |
| `group_id` | varchar | 分组 ID |

---

### 13.7 行军与战斗类

#### log_missions — 行军日志（38 列）
**核心表**：记录所有行军出征行为。

| 字段 | 类型 | 说明 |
|---|---|---|
| `troops_id` | varchar | 部队 ID |
| `finish_time` | bigint | 完成时间 |
| `start_x` / `start_y` | integer | 起始坐标 |
| `stop_x` / `stop_y` | integer | 目标坐标 |
| `actual_x` / `actual_y` | integer | 实际到达坐标 |
| `battle_id` | varchar | 对决对象 ID |
| `category` | bigint | 行军类型 |
| `is_return` | bigint | 是否返回（1=返回，0=出征） |
| `army_id` | varchar | 部队详情（JSON） |
| `beast_info` | varchar | 巨兽信息（JSON） |
| `hero_info` | varchar | 英雄信息（JSON） |
| `return_reason` | bigint | 返回原因 |
| `is_mutiplayer` | integer | 个人/集结（0=个人，1=集结） |

#### log_battle — 战斗日志（38 列）
**核心表**：记录战斗过程与结果。

| 字段 | 类型 | 说明 |
|---|---|---|
| `attack_info` / `defence_info` | varchar | 攻击/防御方信息（JSON） |
| `battle_category` | varchar | 战斗类型 |
| `battle_server_id` | varchar | 战斗服务器 |
| `battle_x` / `battle_y` | integer | 战斗坐标 |
| `fight_id` | varchar | 战斗 ID |
| `result` | varchar | 战斗结果 |
| `attack_action_id` / `defence_action_id` | varchar | 攻击/防御方 action |
| `attack_damage` / `defence_damage` | varchar | 攻击/防御伤害 |
| `is_pvp` | boolean | 是否 PVP |
| `attack_team_attributes` / `defence_team_attributes` | varchar | 攻击/防御队伍属性 |
| `attack_skill_info` / `defence_skill_info` | varchar | 攻击/防御技能信息 |
| `defence_harm` | varchar | 防御伤害详情 |
| `defence_type` | integer | 防御类型 |
| `pos` | integer | 战斗位置 |

#### log_mass_troops — 集结日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `mass_result` | bigint | 集结结果 |
| `mass_secs` | bigint | 集结时长 |
| `mass_type` | bigint | 集结类型 |

#### log_puzzle — 关卡/挑战日志（47 列）
记录关卡战斗、特化蚁挑战等行为。

| 字段 | 类型 | 说明 |
|---|---|---|
| `level_id` | bigint | 关卡 ID |
| `level_chapter` | bigint | 关卡章节 |
| `sub_level_id` | varchar | 子关卡 ID |
| `result` | varchar | 战斗结果 |
| `secs` | bigint | 通关时长 |
| `is_auto_fight` | boolean | 是否自动战斗 |
| `is_first_kill` | boolean | 是否首杀 |
| `fight_times` | integer | 战斗次数 |
| `consume_power` | bigint | 消耗体力 |
| `get_gift` / `first_get_gift` | varchar | 获得奖励 |
| `type` | integer | 关卡类型（0=通关，1=PVP） |
| `fight_type` | integer | 战斗类型 |
| `stage_level` | integer | 段位等级 |
| `difficulty_level` | varchar | 难度等级 |
| `hero_info` / `beast_info` | varchar | 英雄/巨兽信息（JSON） |
| `battle_hero_info` / `battle_beast_info` | varchar | 对战方信息（JSON） |
| `fight_damage` / `battle_damage` | varchar | 伤害信息（JSON） |

---

### 13.8 游戏行为与系统类

#### log_game_step — 游戏步骤日志
**核心表**：记录行为漏斗和关键操作步骤。

| 字段 | 类型 | 说明 |
|---|---|---|
| `device_id` | varchar | 设备 ID |
| `step_type` | varchar | 漏斗类型/行为类型 |
| `step_id` | varchar | 漏斗 ID/行为 ID |
| `value` | varchar | 具体行为值 |
| `game_version` / `app_version` | varchar | 游戏/应用版本 |
| `channel_id` | bigint | 渠道 ID |
| `open_id` | varchar | OpenID |

#### log_behavior — 行为日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `behavior_id` | varchar | 行为 ID |
| `country` | varchar | 国家 |
| `action` | varchar | 引发事件 |

#### log_behavior_client — 客户端行为

| 字段 | 类型 | 说明 |
|---|---|---|
| `behavior_id` | varchar | 行为 ID |
| `behavior_type` | integer | 行为类型 |

#### log_behavior_time — 行为时间日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `behavior_id` | varchar | 行为 ID |
| `ac_id` / `ac_type` / `ac_round` / `ac_stage` | — | 活动维度 |
| `type` | bigint | 类型 |
| `secs` | bigint | 耗时（秒） |

#### log_client_behavior — 客户端行为

| 字段 | 类型 | 说明 |
|---|---|---|
| `behavior_id` | varchar | 行为 ID |
| `behavior_type` | integer | 行为类型 |
| `ext1` ~ `ext10` | integer | 扩展字段（10 个） |

#### log_task — 任务日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | varchar | 任务 ID |
| `task_type` | integer | 任务类型 |
| `daily_task_num` | bigint | 每日任务数 |
| `success_id` | varchar | 完成标识 |
| `ac_id` / `ac_type` / `ac_round` / `ac_stage` | — | 活动维度 |
| `ac_group` | varchar | 活动分组 |
| `large_daily_task_num` | varchar | 大数值存储 |

#### log_game_mail — 游戏邮件日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `mail_id` | varchar | 邮件唯一 ID |
| `mail_show` | varchar | 邮件事件说明 |
| `mail_type` | bigint | 邮件类型 |
| `unique_id` | varchar | 唯一标识 |
| `action` | varchar | 引发事件 |

#### log_notice — 公告日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `notice_id` | varchar | 公告 ID |
| `notice_source` | varchar | 公告来源 |
| `step_id` | varchar | 步骤 ID |

#### log_questionnaire — 问卷日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `questionnaire_id` | bigint | 问卷 ID |
| `option` | varchar | 选项 |

#### log_feedback — 反馈日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `score` | real | 评分 |
| `feedback` | varchar | 反馈内容 |

#### log_rename — 改名日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `new_name` | varchar | 新名字 |

#### log_role_msg — 角色消息

| 字段 | 类型 | 说明 |
|---|---|---|
| `language` | bigint | 语言 |
| `source` | varchar | 来源 |
| `msg` | varchar | 消息内容 |
| `relation_role_id` / `relation_role_name` | varchar | 关联角色 |

#### log_role_declaration — 联盟宣言/留言板

| 字段 | 类型 | 说明 |
|---|---|---|
| `new_declaration` | varchar | 新宣言内容 |
| `operator` | varchar | 操作人 |
| `category` | integer | 分类 |

#### log_role_behavoir — 角色行为

| 字段 | 类型 | 说明 |
|---|---|---|
| `behavoir_name` | varchar | 行为名称 |
| `behavoir_type` | varchar | 行为类型 |
| `behavoir_detail` | varchar | 行为详情 |

#### log_role_data — 角色数据

| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | integer | 数据类型 |
| `params` | varchar | 参数 |
| `dress_params` | varchar | 穿戴参数 |

---

### 13.9 等级与成长类

#### log_base_level — 基地等级日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `base_level` / `last_base_level` | bigint | 当前/变更前等级 |

#### log_level — 角色等级日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `nums` / `balance` | bigint | 经验变动/存量 |

#### log_exp — 经验日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `level` / `last_level` | integer | 当前/变更前等级 |
| `nums` / `balance` | bigint | 经验变动/存量 |
| `large_nums` / `large_balance` | varchar | 大数值存储 |

#### log_vip — VIP 日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `last_vip_level` / `vip_level` | bigint | 变更前/当前 VIP 等级 |
| `last_vip_points` / `vip_points` | bigint | 变更前/当前 VIP 积分 |

#### log_tech — 科技日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `tech_id` | bigint | 科技 ID |
| `tech_type` | bigint | 科技类型 |
| `tech_level` / `tech_last_level` | bigint | 当前/变更前等级 |

#### log_skill — 技能日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `skill_id` | integer | 技能 ID |
| `skill_last_level` / `skill_level` | integer | 变更前/当前等级 |

#### log_evolve — 进化日志（35 列）
记录特化蚁进化系统。

| 字段 | 类型 | 说明 |
|---|---|---|
| `evolve_id` | varchar | 进化 ID |
| `type` | integer | 进化类型 |
| `evolve_level` / `last_evolve_level` | integer | 当前/变更前进化等级 |
| `break_level` / `last_break_level` | integer | 当前/变更前突破等级 |
| `advance_level` / `last_advance_level` | integer | 当前/变更前进阶等级 |
| `object` / `last_object` | varchar | 进化对象 |

#### log_intensify — 强化日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `pos_id` | varchar | 槽位 ID |
| `pos_level` / `last_pos_level` | bigint | 当前/变更前等级 |
| `material` | varchar | 消耗材料（JSON） |
| `pos_type` | varchar | 槽位类型 |

#### log_talent — 天赋日志（34 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `talent_id` | varchar | 天赋 ID |
| `talent_type` | varchar | 天赋类型 |
| `talent_category` | varchar | 天赋分类 |
| `talent_level` / `last_talent_level` | integer | 当前/变更前等级 |
| `talent_intensify_level` / `last_talent_intensify_level` | integer | 强化等级 |
| `object_type` | integer | 所属对象类型 |
| `object_conf_id` / `object_uuid` | varchar | 所属对象信息 |
| `talent_info` | varchar | 天赋详情（JSON） |

#### log_premium_talent — 高级天赋日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `talent_type` | varchar | 天赋类型 |
| `talent_category` | integer | 天赋分类 |
| `talent_info` | varchar | 天赋详情 |

#### log_gene_change — 基因变动日志（42 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `gene_id` | varchar | 基因 ID |
| `gene_conf_id` | integer | 基因配置 ID |
| `gene_type` | integer | 基因类型 |
| `gene_level` / `gene_star` / `gene_break_level` | integer | 等级/星级/突破等级 |
| `gene_position` | bigint | 基因位置 |
| `position_level` | integer | 位置等级 |
| `gene_quality` | integer | 基因品质 |
| `sub_gene_type` | integer | 子基因类型 |
| `power` / `last_power` | bigint | 战力变动 |
| `evolve_level` | integer | 进化等级 |
| `material` | varchar | 消耗材料 |

#### log_formation — 阵型日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `formation_id` | integer | 阵型 ID |
| `formation_level` / `last_formation_level` | integer | 当前/变更前等级 |
| `formation_node` | varchar | 阵型节点 |
| `exp_num` / `exp_balance` | bigint | 经验变动/存量 |
| `type` | integer | 阵型类型 |

#### log_stage — 段位日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `stage_id` | bigint | 段位 ID |
| `rank` / `last_rank` | bigint | 当前/变更前排名 |
| `level` / `last_level` | bigint | 当前/变更前等级 |
| `stage_score` | bigint | 段位积分 |
| `rank_type` | bigint | 排名类型 |
| `large_stage_score` | varchar | 大数值存储 |

#### log_medal — 勋章日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `medal_id` | bigint | 勋章 ID |
| `medal_level` | bigint | 勋章等级 |

#### log_dress_up — 穿戴日志（36 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `skin_id` | integer | 皮肤 ID |
| `use_item_id` | integer | 使用道具 ID |
| `level` / `last_level` | integer | 当前/变更前等级 |
| `star` / `last_star` | integer | 当前/变更前星级 |
| `dress_up_mark` | integer | 穿戴标记 |
| `valid_time` / `valid_time_type` / `valid_end_time` | — | 有效期相关 |
| `object_type` / `object_conf_id` / `object_uuid` | — | 所属对象 |

#### log_habit — 习惯日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `item_id` | bigint | 物品 ID |
| `before_habit` / `habit` | bigint | 变更前/当前习惯值 |
| `habit_level` / `last_habit_level` | integer | 当前/变更前习惯等级 |
| `exp_nums` / `exp_balance` | integer | 经验变动/存量 |

#### log_reform — 改造日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `slot_id` / `slot_type` | integer | 槽位 ID/类型 |
| `reform_id` | integer | 改造 ID |
| `reform_quality` | integer | 改造品质 |
| `reform_level` / `last_reform_level` | integer | 当前/变更前等级 |
| `material` | varchar | 消耗材料 |
| `slot_info` | varchar | 槽位信息 |

#### log_relation — 关系日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `relation_type` | varchar | 关系类型 |
| `sub_relation_type` | varchar | 子关系类型 |
| `partner_id` | varchar | 伙伴 ID |
| `level` / `last_level` | integer | 当前/变更前等级 |
| `nums` / `balance` | bigint | 变动量/存量 |

#### log_synergy — 协同日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `synergy_id` | integer | 协同 ID |
| `synergy_stage` | integer | 协同阶段 |
| `synergy_star` / `last_synergy_star` / `total_synergy_star` | integer | 星级相关 |
| `is_active` | boolean | 是否激活 |

---

### 13.10 怪兽与伙伴类

#### log_giant_beast — 巨兽日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `beast_id` | bigint | 巨兽 ID |
| `beast_level` | bigint | 巨兽等级 |
| `beast_power` | bigint | 巨兽战力 |
| `beast_max_health` | bigint | 巨兽最大血量 |
| `nums` / `balance` | bigint | 变动量/存量 |

#### log_giant_beast_exp — 巨兽经验日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `beast_id` / `beast_level` | bigint | 巨兽 ID/等级 |
| `nums` / `balance` | bigint | 经验变动/存量 |

#### log_giant_beast_skill — 巨兽技能日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `beast_id` | integer | 巨兽 ID |
| `skill_id` | integer | 技能 ID |
| `skill_last_level` / `skill_level` | integer | 变更前/当前等级 |

#### log_partner — 野怪伙伴日志（33 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `partner_id` | varchar | 伙伴 ID |
| `partner_type` | integer | 伙伴类型 |
| `partner_power` | bigint | 伙伴战力 |
| `partner_level` / `partner_last_level` | integer | 当前/变更前等级 |
| `partner_star` / `partner_last_star` | integer | 当前/变更前星级 |
| `partner_sub_star` / `partner_last_sub_star` | integer | 子星级 |
| `partner_break_level` / `partner_last_break_level` | integer | 突破等级 |
| `material_info` | varchar | 消耗材料（JSON） |
| `relation_id` / `relation_uuid` | varchar | 关联 ID |

---

### 13.11 支付与订单类

#### log_update_payments — 支付订单日志（61 列）
**核心表**：记录所有充值支付订单。

| 字段 | 类型 | 说明 |
|---|---|---|
| `uuid` | varchar | 唯一订单 ID |
| `order_id` | varchar | 平台订单 ID |
| `account_id` | varchar | 平台账号 |
| `role_id` | varchar | 角色 ID |
| `product_id` | varchar | 商品 ID |
| `product_content` | varchar | 商品内容（JSON） |
| `pay_type` | integer | 支付类型（1=内购，2=三方，3=转账，4=公众号） |
| `pay_channel` | varchar | 支付渠道 |
| `price` | double | 金额（美元） |
| `local_price` | double | 当地币种金额 |
| `currency` | varchar | 币种 |
| `coin` | integer | 游戏币数量 |
| `status` | integer | 订单状态 |
| `is_paid` | integer | 是否已支付 |
| `is_shipped` | integer | 是否已发货 |
| `is_internal` | boolean | 是否内部订单 |
| `is_test` | integer | 是否测试订单 |
| `conf_id` | integer | 商品配置 ID |
| `conf_id_type` | varchar | 配置 ID 类型 |
| `conf_id_group` | varchar | 配置 ID 分组 |
| `flow_id` | varchar | 第三方渠道订单 ID |
| `relation_id` | varchar | 订单关联 ID（补单生成） |
| `device_id` | varchar | 设备 ID |
| `ip` / `ip_source` | varchar | IP 及来源 |
| `country` | varchar | 国家 |
| `language` | bigint | 语言 |
| `created_time` | bigint | 创建订单时间 |
| `charged_at` | bigint | 付款时间 |
| `finish_at` | bigint | 完成时间 |
| `voided_time_millis` | bigint | 退款时间 |
| `voided_reason` | integer | 退款原因 |
| `event_name` | varchar | 事件名称 |
| `source` | varchar | 来源 |
| `goods_position` | bigint | 商品位置 |
| `custom_content` | varchar | 自定义内容 |
| `usd_price` | double | 美元价格 |
| `exchange_rate` | double | 汇率 |
| `ga_client_id` | varchar | Google Analytics Client ID |

#### log_third_party_payments — 第三方支付日志（57 列）
结构与 log_update_payments 类似，记录第三方支付详情。

#### log_payment_warning — 支付预警日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `order_num` | bigint | 订单数 |
| `pay_num` | bigint | 支付数 |
| `shipped_num` | bigint | 发货数 |
| `voided_num` | bigint | 退款数 |
| `pay_channel` | varchar | 支付渠道 |
| `pay_amount` | double | 支付金额 |

---

### 13.12 能量与战力类

#### log_energy — 体力日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `energy_id` | bigint | 体力 ID |
| `nums` / `balance` | bigint | 体力变动/存量 |

#### log_power_change — 战力变动日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `power_type` | bigint | 战力类型 |
| `power_balance` | bigint | 战力存量 |
| `nums` / `balance` | bigint | 变动量/存量 |
| `large_nums` / `large_power_balance` | varchar | 大数值存储 |

---

### 13.13 装备与道具类

#### log_equip — 装备日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `equip_id` | bigint | 装备 ID |
| `nums` / `balance` | bigint | 变动量/存量 |

#### log_recruit — 招募日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `recruit_type` | integer | 招募类型 |
| `recruit_gold_type` | integer | 金币招募类型 |
| `nums` / `balance` | bigint | 变动量/存量 |

#### log_free_goods — 免费商品日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `conf_id` | integer | 商品配置 ID |
| `conf_id_price` | real | 商品价格 |
| `conf_id_type` | varchar | 商品类型 |
| `conf_id_group` | varchar | 商品分组 |
| `position` | integer | 展示位置 |

#### log_goods_event — 商城事件日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `conf_id` | integer | 商品配置 ID |
| `conf_id_price` | double | 商品价格 |
| `conf_id_type` | varchar | 商品类型 |
| `conf_id_group` | varchar | 商品分组 |
| `position` | integer | 展示位置 |
| `event_name` | varchar | 事件名称 |
| `show_time` | bigint | 曝光时长 |
| `is_purchase` | integer | 是否购买 |
| `click_times` | integer | 点击次数 |
| `event_name_raw` | integer | 原始事件名 |

#### log_gradually — 逐步日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `grad_type` | bigint | 逐步类型 |
| `grad_secs` | bigint | 逐步时长 |
| `is_cancel` | boolean | 是否取消 |

#### log_capacity — 容量日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `capacity_conf_id` | integer | 容量配置 ID |
| `data_type` | integer | 数据类型 |
| `nums` / `balance` | bigint | 变动量/存量 |

---

### 13.14 服务器与系统类

#### log_server_score — 服务器积分日志
**核心表**：记录服务器段位赛积分。

| 字段 | 类型 | 说明 |
|---|---|---|
| `server_id` | varchar | 服务器 ID |
| `ac_id` | varchar | 活动 ID |
| `ac_round` | bigint | 活动轮次 |
| `stage_group` | varchar | 段位分组 |
| `stage_score` | bigint | 段位积分 |
| `score` | double | 贡献总分 |
| `rank` | bigint | 排名 |
| `opposite_server_id` | bigint | 对阵服务器 |
| `race_type` | integer | 赛制类型 |
| `action` | varchar | 引发事件（日/周结算） |

#### log_onlines — 在线人数

| 字段 | 类型 | 说明 |
|---|---|---|
| `avg_users` | bigint | 平均在线 |
| `max_users` | bigint | 最高在线 |
| `now_users` | bigint | 当前在线 |
| `interval` | bigint | 统计间隔 |
| `online_type` | bigint | 在线类型 |

#### log_session — 会话日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `device_id` | varchar | 设备 ID |
| `secs` | bigint | 会话时长 |
| `game_version` / `app_version` | varchar | 版本信息 |

#### log_login_warning — 登录预警

| 字段 | 类型 | 说明 |
|---|---|---|
| `start_time` | bigint | 开始时间 |
| `all_num` | bigint | 总登录数 |
| `fail_num` | bigint | 失败数 |
| `success_num` | bigint | 成功数 |

---

### 13.15 设备与客户端类

#### log_device_msg — 设备详细信息（39 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `device_id` / `adid` | varchar | 设备标识 |
| `mac_address` | varchar | MAC 地址 |
| `os_version` | varchar | 系统版本 |
| `cpu_name` | varchar | CPU 型号 |
| `android_id` | varchar | Android ID |
| `board` / `cpu_abi` | varchar | 主板/ABI |
| `device_display` / `device_model` / `device_manufacturer` | varchar | 设备型号信息 |
| `is_emulator` / `is_root` / `is_proxy` | boolean | 模拟器/Root/代理检测 |
| `device_app_list` | varchar | 已安装应用列表 |
| `device_storage` | varchar | 存储空间 |
| `device_memory` | bigint | 内存 |
| `device_sensor_list` | varchar | 传感器列表 |
| `idfa` / `idfv` | varchar | iOS 广告标识 |
| `lan_ip` | varchar | 局域网 IP |
| `imei` | varchar | IMEI |
| `open_id` / `open_id_type` | varchar | OpenID |
| `email` | varchar | 邮箱 |

#### log_computer_info — 电脑信息

| 字段 | 类型 | 说明 |
|---|---|---|
| `lan_ip` | varchar | 局域网 IP |
| `mac_address` | varchar | MAC 地址 |
| `cpu_name` | varchar | CPU 型号 |
| `pc_name` | varchar | 电脑名称 |
| `os_version` | varchar | 系统版本 |

#### log_computer_info_pc — 电脑信息（PC 端）
结构与 log_computer_info 类似，增加 `relation_id` 字段。

#### log_downloader_msg — 下载器信息
记录客户端下载和热更新相关信息。

| 字段 | 类型 | 说明 |
|---|---|---|
| `app_version` | varchar | 应用版本 |
| `error` | varchar | 错误信息 |
| `link_source` | varchar | 链接来源 |
| `media_source` | varchar | 媒体来源 |
| `u1` ~ `u4` | varchar | 自定义参数 |

#### log_downloader_msg_pc — 下载器信息（PC 端）
结构与 log_downloader_msg 类似。

---

### 13.16 网页访问与客户端行为类

#### log_visit_web — 网页访问日志（48 列）
记录 H5/网页端的用户行为。

| 字段 | 类型 | 说明 |
|---|---|---|
| `address` | varchar | 访问地址 |
| `app_key` | varchar | 应用标识 |
| `behavior_id` / `behavior_type` | varchar/int | 行为标识/类型 |
| `event_name` | varchar | 事件名称 |
| `source` | varchar | 来源 |
| `stay_secs` | integer | 停留时长 |
| `browser_id` | varchar | 浏览器 ID |
| `link_source` | varchar | 链接来源 |
| `starunion_id` | varchar | StarUnion ID |
| `media_source` | varchar | 媒体来源 |
| `u1` ~ `u4` | varchar | 自定义参数 |
| `platform_language` | varchar | 平台语言 |
| `behavior_value` | varchar | 行为值 |
| `source_type` | varchar | 来源类型 |
| `ga_client_id` | varchar | GA Client ID |

#### log_visit_web_pc — 网页访问日志（PC 端）
结构与 log_visit_web 类似，减少部分字段。

---

### 13.17 其他系统类

#### log_use_cdkey — CDK 使用日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `cdk_id` | varchar | CDK ID |
| `cdk_group_id` | varchar | CDK 组 ID |
| `package_name` | varchar | 包名 |
| `award_info` | varchar | 奖励信息 |
| `use_channel` | integer | 使用渠道 |
| `project` | varchar | 项目 |

#### log_update_subscribes — 订阅日志（37 列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `uuid` | varchar | 唯一标识 |
| `start_at` / `end_at` / `cancel_at` | bigint | 开始/结束/取消时间 |
| `event_type` | integer | 事件类型 |
| `event_name` | varchar | 事件名称 |
| `in_trial_period` | integer | 是否试用期 |
| `is_pre_period` | integer | 是否预付期 |
| `auto_renew_status` | integer | 自动续费状态 |
| `group_id` | varchar | 分组 ID |
| `offer_type` | integer | 优惠类型 |
| `pay_channel` | varchar | 支付渠道 |

#### log_npc_alliance — NPC 联盟日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `role_class` | varchar | 角色分类 |
| `map_id` | varchar | 地图 ID |
| `ac_cycle` | integer | 活动周期 |

#### log_notice — 公告日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `notice_id` | varchar | 公告 ID |
| `notice_source` | varchar | 公告来源 |
| `step_id` | varchar | 步骤 ID |

#### log_check_events — 关卡校验日志

| 字段 | 类型 | 说明 |
|---|---|---|
| `check_data` | integer | 校验数据 |
| `level_id` / `level_chapter` | bigint | 关卡 ID/章节 |
| `result` | varchar | 校验结果 |
| `puzzle_id` | varchar | 拼图 ID |
| `check_category` | varchar | 校验分类 |
| `board_data` | varchar | 棋盘数据 |
| `operates` | varchar | 操作记录 |
| `attack_data` / `defence_data` | varchar | 攻防数据 |

---

### 13.18 日志表分类索引

| 分类 | 日志表 | 用途 |
|---|---|---|
| **账号登录** | log_accounts, log_login_acc, log_login_behavior, log_login_role, log_logout, log_connects, log_create_role, log_update_accounts, log_update_roles, log_update_devices, log_bind_accounts, log_delete, log_roles | 账号注册、登录、登出、绑定、设备信息 |
| **道具资源** | log_item, log_resource, log_item_exchange, log_debt, log_armies, log_armies_dead, log_injured_armies, log_troops | 道具/资源/部队变动 |
| **建筑联盟** | log_buildings, log_alliance_buildings, log_build_occupy, log_alliance_change, log_update_alliances, log_alliance_award, log_alliance_rank, log_alliance_resource, log_alliance_score, log_alliance_task, log_alliance_tech, log_npc_alliance | 建筑升级、联盟运营 |
| **英雄技能** | log_hero, log_hero_skill, log_hero_cell, log_hero_haved, log_hero_synergy, log_hero_tmp | 英雄全生命周期 |
| **活动积分** | log_activity_score, log_activity_award, log_activity_join, log_role_rank | 活动参与与积分 |
| **行军战斗** | log_missions, log_battle, log_mass_troops, log_puzzle, log_check_events | 行军出征、战斗、关卡 |
| **游戏行为** | log_game_step, log_behavior, log_behavior_client, log_behavior_time, log_client_behavior, log_task, log_game_mail, log_notice, log_questionnaire, log_feedback, log_rename, log_role_msg, log_role_declaration, log_role_behavoir, log_role_data | 行为追踪、任务、邮件、反馈 |
| **等级成长** | log_base_level, log_level, log_exp, log_vip, log_tech, log_skill, log_evolve, log_intensify, log_talent, log_premium_talent, log_gene_change, log_formation, log_stage, log_medal, log_dress_up, log_habit, log_reform, log_relation, log_synergy | 等级、科技、技能、进化、天赋、基因、阵型、段位、穿戴 |
| **怪兽伙伴** | log_giant_beast, log_giant_beast_exp, log_giant_beast_skill, log_partner | 巨兽、野怪伙伴 |
| **支付订单** | log_update_payments, log_third_party_payments, log_payment_warning, log_payments_warning_test | 充值支付、订单、退款 |
| **能量战力** | log_energy, log_power_change | 体力、战力变动 |
| **装备道具** | log_equip, log_recruit, log_free_goods, log_goods_event, log_gradually, log_capacity | 装备、招募、商城 |
| **服务器系统** | log_server_score, log_onlines, log_session, log_session_emr, log_login_warning, log_login_warning_test | 服务器积分、在线统计 |
| **设备客户端** | log_device_msg, log_computer_info, log_computer_info_pc, log_downloader_msg, log_downloader_msg_pc | 设备信息、电脑信息、下载器 |
| **网页行为** | log_visit_web, log_visit_web_pc | H5/PC 网页访问 |
| **其他系统** | log_use_cdkey, log_update_subscribes | CDK、订阅 |
