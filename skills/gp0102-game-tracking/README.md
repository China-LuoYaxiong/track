# gp0102-game-tracking

GP0102 游戏项目**埋点方案生成** Skill。根据新功能需求，复用现有日志表和字段体系，生成完整埋点方案。

**核心约束**：零新增表、零新增字段。

## 目录结构

```
gp0102-game-tracking/
├── SKILL.md                    # Agent 主流程（自动读取）
├── reference.md                # 日志表结构 + 字段定义 + action 规范（~1800 行）
├── reference_data.json         # 机器可读全量数据（119 张日志表 + 字段 + action）
├── README.md                   # 本文件
├── 使用说明.md                  # 快速上手
├── source/
│   ├── 【GP0102】运营-平台-游戏需求对接.xlsx   # 原始埋点需求表
│   └── gp0102日志表结构.csv                     # 数据库实际表结构
└── examples/                    # 示例输出
```

## 安装

**项目级（推荐）：** 复制到 `<项目>/.cursor/skills/gp0102-game-tracking/`

**全局：** `~/.cursor/skills/gp0102-game-tracking/`

## 使用

```
@gp0102-game-tracking 帮我出宣战功能的埋点方案
```

描述你的功能需求，agent 会：

1. 分析业务动作和打点时机
2. 从 119 张现有日志表中选择最合适的表
3. 映射现有字段，用 extend_1~5 承载 JSON 额外数据
4. 分配 action 编号（避免冲突）
5. 输出完整 Markdown 埋点方案

## 核心能力

| 能力 | 说明 |
|---|---|
| 事件表选择 | 根据业务场景从 119 张现有表中推荐最佳匹配 |
| 字段映射 | 将新需求映射到现有字段体系，用 extend 承载额外数据 |
| action 管理 | 分配和校验 action 编号，避免与已有编号冲突 |
| 关联关系 | 通过 action_id 串联同一业务链的多条记录 |
| 方案校验 | 自检是否违反"零新增"约束 |

## 约束红线

- **禁止新增日志表**（如 log_outpost_change 等）
- **禁止新增字段**（如在现有表中加列）
- 新业务数据通过 `extend_1~5`（JSON 格式）承载
- 新行为类型通过 `action`、`step_type`、`step_id` 等现有字段的值区分

## 文件说明

| 文件 | 作用 |
|---|---|
| SKILL.md | Agent 主流程，定义工作流和约束 |
| reference.md | 人类可读的完整参考（119 表 + 字段 + action） |
| reference_data.json | 机器可读全量数据，供 agent 精确查询 |
| source/*.xlsx | 原始埋点需求对接表 |
| source/*.csv | 数据库实际表结构 |
