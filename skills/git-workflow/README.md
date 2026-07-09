# git-workflow

管理与 GitHub 远程仓库的完整 Git 工作流 Skill。覆盖克隆、拉取、提交、推送、分支管理、冲突处理。

## 目录结构

```
git-workflow/
├── SKILL.md          # Agent 主流程
├── reference.md      # Git 命令速查 + 工作流规范
├── README.md         # 本文件
└── 使用说明.md       # 快速上手
```

## 安装

**项目级（推荐）：** 复制到 `<项目>/.cursor/skills/git-workflow/`

**全局：** `~/.cursor/skills/git-workflow/`

## 使用

```
@git-workflow 拉取最新代码
@git-workflow 推送所有更改
@git-workflow 创建新分支 feat/xxx
@git-workflow 查看最近提交记录
```

## 核心能力

| 能力 | 说明 |
|---|---|
| 拉取代码 | `git pull --rebase` 保持线性历史 |
| 提交推送 | 规范提交信息，自动检查状态 |
| 分支管理 | 创建/切换/合并/删除分支 |
| 冲突处理 | 识别冲突、引导解决、继续操作 |
| 历史查看 | 文件历史、提交详情、差异对比 |
| 安全约束 | 禁止强制推送、禁止提交敏感信息 |

## 项目配置

| 配置 | 值 |
|---|---|
| 远程仓库 | `https://github.com/China-LuoYaxiong/track.git` |
| 工作目录 | `e:\track` |
| 主分支 | `main` |
| Shell | PowerShell |

## 文件说明

| 文件 | 作用 |
|---|---|
| SKILL.md | Agent 主流程，定义完整工作流 |
| reference.md | 命令速查表 + 规范 + 安全红线 |
| 使用说明.md | 快速上手指南 |
