# Git/GitHub 工作流规范

## 项目信息

| 项目 | 值 |
|---|---|
| 远程仓库 | `https://github.com/China-LuoYaxiong/track.git` |
| 工作目录 | `e:\track` |
| 主分支 | `main` |
| 用户名 | `lyx` |
| 邮箱 | `1091372318@qq.com` |
| Shell | PowerShell (`C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`) |

## 操作系统特殊说明

本项目运行在 **Windows PowerShell** 环境下：

- **不支持 `&&`** 作为命令分隔符，必须用 `;`
- **不支持 `rm -rf`**，使用 `Remove-Item -Recurse -Force`
- **不支持 `ls -la`**，使用 `Get-ChildItem`
- **不支持 `cat`**，使用 `Get-Content` 或 Read 工具

### PowerShell 常用等价命令

| Linux/Mac | PowerShell |
|---|---|
| `ls -la` | `Get-ChildItem -Force` |
| `rm file` | `Remove-Item file -Force` |
| `rm -rf dir` | `Remove-Item dir -Recurse -Force` |
| `cat file` | `Get-Content file` |
| `echo "text" > file` | `"text" \| Out-File file` |
| `mkdir dir` | `New-Item -ItemType Directory dir` |
| `cp src dst` | `Copy-Item src dst` |
| `mv src dst` | `Move-Item src dst` |
| `pwd` | `Get-Location` |
| `cd dir` | `Set-Location dir` 或 `cd dir` |

## Git 工作流

### 日常流程

```
1. git pull --rebase     # 拉取远程最新
2. 本地修改文件          # 使用 Read/Edit 工具
3. git add -A            # 暂存所有更改
4. git status            # 检查暂存内容
5. git commit -m "..."   # 提交
6. git push              # 推送到远程
```

### 提交信息格式

```
<type>: <简短描述>

<可选详细描述，每行以 - 开头>
```

**type 枚举：**

| type | 含义 | 使用场景 |
|---|---|---|
| feat | 新功能 | 新增文件、新增功能 |
| fix | 修复 bug | 修正错误、修复问题 |
| docs | 文档变更 | README、使用说明等 |
| style | 格式调整 | 缩进、换行、空格 |
| refactor | 重构 | 代码结构调整，不改功能 |
| chore | 工具/构建 | .gitignore、脚本等 |
| delete | 删除 | 移除文件/目录 |
| rename | 重命名 | 移动/重命名文件 |

**提交信息示例：**

```
feat: 新增 gp0102-game-tracking skill

- 包含 SKILL.md 主流程定义
- reference.md 1884 行完整参考文档
- reference_data.json 119 张日志表结构化数据
```

```
fix: 修正 reference_data.json 编码问题
```

```
delete: 移除根目录临时文件
```

## 分支管理

### 命名规范

| 前缀 | 用途 | 示例 |
|---|---|---|
| feat/ | 新功能 | `feat/new-tracking-plan` |
| fix/ | bug 修复 | `fix/encoding-issue` |
| docs/ | 文档更新 | `docs/update-readme` |
| hotfix/ | 紧急修复 | `hotfix/critical-bug` |

### 操作命令

```powershell
# 创建并切换分支
git checkout -b feat/new-feature

# 推送新分支
git push -u origin feat/new-feature

# 合并到 main
git checkout main
git merge feat/new-feature
git push

# 删除已合并的分支
git branch -d feat/new-feature
git push origin --delete feat/new-feature
```

## 常见问题

### 1. 远程有新提交，push 被拒绝

```powershell
git pull --rebase
git push
```

### 2. 合并冲突

```powershell
# 查看冲突文件
git status

# 解决冲突后
git add .
git commit -m "fix: 解决合并冲突"
git push
```

### 3. 撤销未提交的修改

```powershell
# 工作区修改（未暂存）
git restore <file>

# 已暂存（add 了但没 commit）
git restore --staged <file>
```

### 4. 撤销最近一次提交

```powershell
# 保留修改，只撤销提交
git reset --soft HEAD~1

# 不保留修改，完全回退
git reset --hard HEAD~1
```

### 5. 查看文件的 Git 历史

```powershell
# 文件的提交历史
git log --oneline path/to/file

# 文件的修改差异
git log -p path/to/file

# 某次提交的详细内容
git show <commit-hash>
```

## .gitignore 规则

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/

# 临时文件
*.tmp
*.bak
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
desktop.ini

# IDE
.idea/
.vscode/
*.swp

# Node
node_modules/
```

## 安全红线

| 禁止 | 说明 |
|---|---|
| 提交密码/token | 敏感信息不得进入 Git 历史 |
| `git push --force` | 除非用户明确要求，禁止强制推送 |
| `git reset --hard` | 除非用户明确要求，禁止硬回退 |
| 提交大文件 | 超过 10MB 的文件不提交 |
| `git rm -rf /` | 禁止危险删除命令 |
| 修改 `.git/config` | 不修改 Git 配置文件 |
