---
name: git-workflow
description: >-
  管理与 GitHub 远程仓库的完整 Git 工作流，包括克隆、拉取、提交、推送、分支管理。
  当用户要求拉取代码、推送更改、查看 Git 状态、管理分支、处理冲突时使用。
---

# Git/GitHub 工作流

管理本项目与 GitHub 远程仓库的完整交互流程。

## 必读资源

执行前先读取：

1. [reference.md](reference.md) — Git 命令速查 + 工作流规范
2. [使用说明.md](使用说明.md) — 快速上手

## 项目 Git 配置

| 配置项 | 值 |
|---|---|
| 远程仓库 | `https://github.com/China-LuoYaxiong/track.git` |
| 工作目录 | `e:\track` |
| 主分支 | `main` |
| 用户名 | `lyx` |
| 邮箱 | `1091372318@qq.com` |

## 工作流程

```
确认状态 → 拉取最新 → 本地修改 → 暂存 → 提交 → 推送
```

### Step 1：确认当前状态

每次操作前先查看仓库状态：

```powershell
cd e:\track
git status                    # 工作区状态
git log --oneline -5          # 最近 5 条提交
git branch -a                 # 所有分支
```

### Step 2：拉取远程最新代码

**标准拉取（合并）：**

```powershell
git pull
```

**拉取并变基（推荐，保持线性历史）：**

```powershell
git pull --rebase
```

**拉取指定分支：**

```powershell
git pull origin main
```

### Step 3：修改文件

在工作目录中进行文件修改（创建、编辑、删除）。

**文件操作约束：**

| 操作 | 工具 | 说明 |
|---|---|---|
| 新建文件 | Write 工具 | 仅在必要时创建 |
| 编辑文件 | SearchReplace 工具 | 优先编辑已有文件 |
| 删除文件 | DeleteFile 工具 | 仅删除明确需要删除的 |
| 文件操作 | 禁止用 Bash | 不要用 Bash 做文件读写 |

### Step 4：暂存更改

```powershell
# 暂存所有更改
git add -A

# 暂存指定文件
git add path/to/file1 path/to/file2

# 暂存指定目录
git add path/to/directory/
```

**暂存前检查：**

```powershell
git status        # 确认哪些文件被修改/新增/删除
git diff          # 查看具体改动内容
git diff --cached # 查看已暂存的改动
```

### Step 5：提交

**提交信息规范：**

```
<type>: <简短描述>

<可选的详细描述>
```

**type 类型：**

| type | 用途 | 示例 |
|---|---|---|
| `feat` | 新功能 | `feat: 新增 gp0102-game-tracking skill` |
| `fix` | 修复 bug | `fix: 修正 reference_data.json 编码问题` |
| `docs` | 文档变更 | `docs: 更新 README.md 使用说明` |
| `style` | 格式调整（不影响逻辑） | `style: 统一缩进为 2 空格` |
| `refactor` | 重构（不新增功能/修复 bug） | `refactor: 拆分 extract_json.py 为模块` |
| `chore` | 构建/工具变更 | `chore: 更新 .gitignore` |
| `delete` | 删除文件 | `delete: 移除根目录临时文件` |
| `rename` | 重命名/移动 | `rename: 示例文件移入子目录` |

**提交命令：**

```powershell
git commit -m "feat: 新增 gp0102-game-tracking skill"
```

**带详细描述的提交：**

```powershell
git commit -m "feat: 新增 gp0102-game-tracking skill

- 包含 SKILL.md 主流程
- reference.md 1884 行完整参考文档
- reference_data.json 119 张日志表结构化数据
- source 目录含原始 Excel 和 CSV"
```

### Step 6：推送到远程

```powershell
# 推送到当前分支
git push

# 推送到指定分支
git push origin main

# 首次推送新分支
git push -u origin <branch-name>
```

**推送失败处理：**

```powershell
# 远程有新提交，先拉取再推送
git pull --rebase
git push

# 如果有冲突，解决后
git add .
git rebase --continue
git push
```

## 分支管理

### 创建与切换分支

```powershell
# 创建并切换到新分支
git checkout -b <branch-name>

# 或用新语法
git switch -c <branch-name>

# 切换到已有分支
git checkout <branch-name>
git switch <branch-name>
```

### 分支命名规范

| 前缀 | 用途 | 示例 |
|---|---|---|
| `feat/` | 新功能开发 | `feat/new-tracking-plan` |
| `fix/` | bug 修复 | `fix/encoding-issue` |
| `docs/` | 文档更新 | `docs/update-readme` |
| `hotfix/` | 紧急修复 | `hotfix/critical-bug` |

### 合并分支

```powershell
# 合并分支到当前分支
git merge <branch-name>

# 合并后推送
git push
```

### 删除分支

```powershell
# 删除本地分支
git branch -d <branch-name>

# 强制删除本地分支
git branch -D <branch-name>

# 删除远程分支
git push origin --delete <branch-name>
```

## 常见问题处理

### 合并冲突

```powershell
# 查看冲突文件
git status

# 编辑冲突文件，解决冲突标记 <<<<<<< ======= >>>>>>>
# 然后
git add .
git commit -m "fix: 解决合并冲突"
git push
```

### 撤销未提交的更改

```powershell
# 撤销工作区修改（未暂存）
git checkout -- <file>
git restore <file>

# 撤销暂存（已 add 未 commit）
git reset HEAD <file>
git restore --staged <file>
```

### 撤销最近一次提交

```powershell
# 保留修改，撤销提交
git reset --soft HEAD~1

# 不保留修改，撤销提交
git reset --hard HEAD~1
```

### 查看历史

```powershell
# 简洁日志
git log --oneline

# 带文件名的日志
git log --oneline --name-status

# 查看某文件的修改历史
git log --oneline path/to/file

# 查看某次提交的详细改动
git show <commit-hash>
```

### .gitignore

确保以下文件不被提交：

```gitignore
# 临时文件
*.tmp
*.bak
__pycache__/
*.pyc

# 系统文件
.DS_Store
Thumbs.db
desktop.ini

# IDE
.idea/
.vscode/
*.swp
*.swo

# 大文件（如有）
*.zip
*.tar.gz
```

## 操作检查清单

### 提交前自检

- [ ] `git status` 确认没有遗漏的文件
- [ ] `git diff` 确认改动内容正确
- [ ] 提交信息符合 `<type>: <描述>` 规范
- [ ] 没有提交敏感信息（密码、token、密钥）
- [ ] 没有提交临时文件（`.pyc`、`__pycache__`）

### 推送前自检

- [ ] 先 `git pull --rebase` 拉取远程最新
- [ ] 没有未解决的合并冲突
- [ ] 提交历史清晰，没有无意义的提交

## 快速命令参考

| 操作 | 命令 |
|---|---|
| 查看状态 | `git status` |
| 查看日志 | `git log --oneline -10` |
| 拉取最新 | `git pull --rebase` |
| 暂存所有 | `git add -A` |
| 提交 | `git commit -m "type: 描述"` |
| 推送 | `git push` |
| 创建分支 | `git checkout -b feat/xxx` |
| 合并分支 | `git merge feat/xxx` |
| 删除分支 | `git branch -d feat/xxx` |
| 查看差异 | `git diff` |
| 撤销修改 | `git restore <file>` |
| 撤销暂存 | `git restore --staged <file>` |

## 用户可选输入

- 指定操作类型（pull/push/branch/merge 等）
- 指定分支名
- 指定提交信息
- 要求查看特定文件的 Git 历史

默认：**先检查状态，再按需操作**。
