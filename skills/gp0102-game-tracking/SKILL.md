---
name: gp0102-game-tracking
description: >-
  根据 GP0102 游戏项目埋点规范，为新功能/新需求生成完整埋点方案。
  严格复用现有日志表和字段体系，不新增表和字段。
  使用当用户提到埋点方案、打点设计、事件表选择、action 分配、或 GP0102 游戏数据上报相关需求时。
---

# GP0102 游戏埋点方案生成

根据用户描述的**新功能/新需求**，按 GP0102 游戏埋点规范生成**完整埋点方案**。

## 核心约束（硬性）

> **零新增表、零新增字段**：所有新需求必须 100% 复用现有日志表（log_xxx）和已有字段体系。
> 不得创建新表，不得在现有表中新增字段。新业务数据通过现有字段（action、step_type、step_id、extend_1~5 等）承载。

## 必读资源

执行前先读取：

1. [reference.md](reference.md) — 日志表结构、字段定义、action 规范（人类可读，~1800 行）
2. [reference_data.json](reference_data.json) — 机器可读全量数据（119 张日志表 + 字段 + action 编号）
3. `source/【GP0102】运营-平台-游戏需求对接.xlsx` — 原始埋点需求表
4. `source/gp0102日志表结构.csv` — 数据库实际表结构

## 工作流程

```
需求分析 → 选择事件表 → 映射现有字段 → 分配 action → 输出埋点方案
```

### Step 1：分析需求

从用户描述中提取：

- **业务动作**：玩家做了什么（如宣战、领取奖励、兑换道具）
- **打点时机**：何时触发（如成功时、取消时、定时）
- **需要记录的维度**：玩家 ID、对象 ID、数量、结果等
- **是否有消耗/获取**：涉及道具或资源变动

### Step 2：选择事件表（必须从以下现有表中选）

#### 行为追踪类

| 事件表 | 适用场景 |
|---|---|
| `log_game_step` | 行为漏斗、关键操作步骤、功能入口点击 |
| `log_behavior` | 通用行为追踪 |
| `log_task` | 任务完成/领取 |

#### 道具资源类

| 事件表 | 适用场景 |
|---|---|
| `log_item` | 道具获取/消耗 |
| `log_resource` | 资源获取/消耗 |
| `log_item_exchange` | 道具兑换（用 A 换 B） |

#### 战斗行军类

| 事件表 | 适用场景 |
|---|---|
| `log_battle` | 战斗结果、攻防信息 |
| `log_missions` | 行军出征 |
| `log_puzzle` | 关卡/挑战/副本 |
| `log_mass_troops` | 集结 |

#### 活动积分类

| 事件表 | 适用场景 |
|---|---|
| `log_activity_score` | 活动积分变动 |
| `log_activity_award` | 活动奖励领取 |
| `log_activity_join` | 活动参与记录 |
| `log_role_rank` | 排名变动 |

#### 建筑联盟类

| 事件表 | 适用场景 |
|---|---|
| `log_alliance_buildings` | 建筑升级/变更/状态变化 |
| `log_alliance_change` | 联盟成员变动 |
| `log_update_alliances` | 联盟全量信息快照 |

#### 英雄成长类

| 事件表 | 适用场景 |
|---|---|
| `log_hero` | 英雄获取/升级/升星 |
| `log_hero_skill` | 英雄技能变动 |
| `log_evolve` | 进化系统 |
| `log_talent` | 天赋系统 |

#### 其他常用

| 事件表 | 适用场景 |
|---|---|
| `log_energy` | 体力变动 |
| `log_server_score` | 服务器积分 |
| `log_game_mail` | 邮件发放/领取 |
| `log_fly` | 迁城 |

### Step 3：映射现有字段

每个事件表都有以下**固定字段体系**，直接复用：

#### 通用行为字段（大部分表都有）

| 字段 | 类型 | 用途 |
|---|---|---|
| `action` | varchar | 行为标识，区分不同操作类型 |
| `action_id` | varchar | 关联 ID，串联同一业务链 |
| `extend_1` ~ `extend_5` | varchar | 扩展数据，JSON 格式存额外信息 |

#### 通用玩家维度（大部分表都有）

| 字段 | 类型 | 用途 |
|---|---|---|
| `acc_id` | varchar | 账号 ID |
| `role_id` | varchar | 角色 ID |
| `role_name` | varchar | 角色昵称 |
| `server_id` | varchar | 服务器 ID |
| `alliance_id` | varchar | 联盟 ID |
| `base_level` | bigint | 基地等级 |
| `role_level` | bigint | 角色等级 |

#### 道具/资源变动字段（log_item、log_resource 等）

| 字段 | 类型 | 用途 |
|---|---|---|
| `item_id` / `resource_id` | bigint | 道具/资源 ID |
| `nums` | bigint | 改变量（正=获取，负=消耗） |
| `balance` | bigint | 变动后存量 |

#### 行为漏斗字段（log_game_step 专用）

| 字段 | 类型 | 用途 |
|---|---|---|
| `step_type` | varchar | 漏斗/行为大类 |
| `step_id` | varchar | 具体行为步骤 |
| `value` | varchar | 行为值/参数 |

#### 活动维度字段（log_activity_* 系列）

| 字段 | 类型 | 用途 |
|---|---|---|
| `ac_id` | varchar | 活动 ID |
| `ac_type` | bigint | 活动类型 |
| `ac_round` | bigint | 活动轮次 |
| `ac_stage` | bigint | 活动阶段 |
| `ac_cycle` | bigint | 活动周期 |

#### 战斗字段（log_battle 专用）

| 字段 | 类型 | 用途 |
|---|---|---|
| `battle_category` | varchar | 战斗类型分类 |
| `fight_id` | varchar | 战斗唯一 ID |
| `result` | varchar | 战斗结果 |
| `attack_info` / `defence_info` | varchar | 攻防信息（JSON） |
| `attack_damage` / `defence_damage` | varchar | 伤害明细（JSON） |
| `is_pvp` | boolean | 是否 PVP |

#### 建筑字段（log_alliance_buildings、log_buildings）

| 字段 | 类型 | 用途 |
|---|---|---|
| `build_conf_id` | integer/bigint | 建筑配置 ID |
| `pos` | integer/bigint | 建筑位置 |
| `build_level` / `build_old_level` | integer/bigint | 当前/变更前等级 |
| `value` / `last_value` | varchar/bigint | 当前/变更前值 |

#### 关卡字段（log_puzzle 专用）

| 字段 | 类型 | 用途 |
|---|---|---|
| `level_id` | bigint | 关卡 ID |
| `level_chapter` | bigint | 关卡章节 |
| `sub_level_id` | varchar | 子关卡 ID |
| `result` | varchar | 战斗结果 |
| `secs` | bigint | 通关时长（秒） |
| `type` | integer | 0=通关战斗，1=PVP 战斗 |

### Step 4：分配 action 编号

action 值分配规则：

1. **查询 reference_data.json 中已使用的 action 编号**，避免冲突
2. 新 action 按号段规则分配（参考历史号段）
3. 如涉及多个行为，每个行为分配独立 action
4. 关联行为通过相同的 `action_id` 串联

**已知 action 编号段参考**（需查 reference_data.json 确认最新）：

| 号段 | 功能模块 |
|---|---|
| 10001~10011 | 基础活动/道具 |
| 10860~10869 | 特化蚁进化 |
| 10890~10892 | 特化蚁派遣 |
| 11100~11200 | 赛季/集结 |
| 11300~11450 | 伙伴/追赶/火晶/化石 |
| 12000+ | 加速返还等 |

### Step 5：输出埋点方案

输出格式（每行一个埋点点位）：

```
### 需求名称

#### 表 1：{事件表名}

| 属性类别 | 上报字段 | 字段中文名 | 字段类型 | 属性描述/属性值/备注 |
|---|---|---|---|---|
| 玩家基本信息 | acc_id, role_id, ... | — | — | 平台规范字段 |
| {业务类别} | {字段} | {中文名} | {类型} | {说明/取值规范} |
```

**输出要求**：

1. 每个需求点明确标注使用的事件表
2. 详细列出每个字段的填写值和说明
3. 涉及道具/资源变动的，分别写 log_item 和 log_resource 行
4. 通过 `action_id` 标明关联关系
5. 用 `extend_1~5` 承载 JSON 格式的额外业务数据
6. 最后输出 action 编号汇总表和关联关系图

### 关联关系表达

通过 `action_id` 字段串联同一业务链的多条记录：

```
操作 A (表1, action_id=X)
  ├── 结果 B (表2, action_id=X)
  └── 结果 C (表3, action_id=X)
```

### 自检清单

- [ ] 所有事件表均来自 reference_data.json，未新增表
- [ ] 所有字段均来自现有表结构，未新增字段
- [ ] action 编号未与已有编号冲突
- [ ] extend_1~5 用于承载 JSON 格式额外数据
- [ ] action_id 正确串联了同一业务链
- [ ] 涉及道具/资源变动的写了 log_item / log_resource
- [ ] 战斗类需求使用了 log_battle 的 battle_category 区分类型

## 用户可选输入

- 指定使用哪些事件表
- 指定 action 编号范围
- 要求输出为 Excel 格式
- 要求补充验收规范
- 要求关联已有的埋点需求

默认：**输出 Markdown 格式埋点方案**。
