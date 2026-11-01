# GitHub 新手使用指南

这份指南面向第一次系统使用 GitHub 的用户，结合你的账号 `shanghaiLiyuu` 和本次三个算法项目说明常用操作。

## 1. 先分清 Git 和 GitHub

- **Git**：安装在电脑上的版本管理工具，记录文件每次修改。
- **GitHub**：托管 Git 仓库的网站，提供展示、协作、备份、Issue 和自动测试。
- **仓库（repository / repo）**：一个项目及其版本历史。
- **提交（commit）**：一次有说明的本地修改快照。
- **推送（push）**：把本地提交上传到 GitHub。
- **拉取（pull）**：把 GitHub 上的新提交下载并合并到本地。
- **克隆（clone）**：第一次把远程仓库完整下载到电脑。
- **分支（branch）**：独立开发线，适合尝试新功能而不直接影响稳定版本。

最常见的日常流程是：

```text
修改文件 -> git add -> git commit -> git push
```

在另一台电脑继续工作前，先执行 `git pull`。

## 2. 一次性配置

安装 Git 后，在 Git Bash 或终端中设置提交署名：

```bash
git config --global user.name "shanghaiLiyuu"
git config --global user.email "你的 GitHub 绑定邮箱"
```

查看配置：

```bash
git config --global --list
```

GitHub 邮箱应与账号设置中的邮箱一致。如果不想公开私人邮箱，可以在 GitHub 的 **Settings -> Emails** 中启用隐私邮箱，然后使用网站提供的 `ID+shanghaiLiyuu@users.noreply.github.com` 地址。

## 3. 登录和凭据安全

HTTPS 推送时，**GitHub 密码不能代替访问令牌**。推荐使用 Git Credential Manager 的浏览器登录，系统会安全保存授权凭据。

如果系统提示输入 Personal Access Token：

1. 打开 GitHub **Settings -> Developer settings -> Personal access tokens**。
2. 创建令牌，只授予当前需要的仓库权限。
3. 把令牌当作密码使用，并存入系统凭据管理器。
4. 不要把令牌写进代码、README、截图或聊天记录。

如果不慎泄露令牌，应立即在 GitHub 撤销并重新创建。

## 4. 创建你的 GitHub 主页

GitHub 有一个特殊规则：创建与你的用户名完全相同的公开仓库，仓库根目录的 `README.md` 就会显示在个人主页。

你的主页仓库地址应为：

```text
https://github.com/shanghaiLiyuu/shanghaiLiyuu
```

操作步骤：

1. 点击 GitHub 右上角的 `+`，选择 **New repository**。
2. Repository name 填写 `shanghaiLiyuu`。
3. 选择 **Public**。
4. 初始化后，把本次生成的 `profile/README.md` 内容放入根目录的 `README.md`。
5. 提交并刷新个人主页。

以后修改这个文件，就能更新主页介绍。图片链接使用公开仓库中的实际文件地址，避免引用不存在的图片。

## 5. 创建算法项目仓库

分别创建以下三个公开仓库，不要在网页初始化时添加 README，以免与本地首次推送产生无关历史：

```text
structural-fem-lab
orbit-dynamics-lab
robot-motion-lab
```

推荐的仓库简介：

- `structural-fem-lab`：`3D truss finite element solver with NumPy, tests and visualization.`
- `orbit-dynamics-lab`：`Two-body and J2 orbital propagation with RK4 and numerical diagnostics.`
- `robot-motion-lab`：`Planar robot kinematics, damped least-squares IK and minimum-jerk trajectories.`

推荐主题（Topics）：

- 共同：`python`、`numpy`、`numerical-methods`、`algorithms`
- 力学：`finite-element-method`、`structural-analysis`、`computational-mechanics`
- 航天：`orbital-mechanics`、`astrodynamics`、`j2`、`rk4`
- 机器人：`robotics`、`kinematics`、`trajectory-planning`

## 6. 用命令行发布本地项目

以下以力学项目为例。假设本地文件夹是 `structural-fem-lab`，先进入该文件夹：

```bash
cd /你的路径/structural-fem-lab
git init -b main
git add .
git status
git commit -m "Initial release: 3D truss FEM solver"
git remote add origin https://github.com/shanghaiLiyuu/structural-fem-lab.git
git push -u origin main
```

检查 `git status` 很重要：确认没有虚拟环境、缓存、密码或大文件后再提交。

如果网页创建仓库时误加了 README，先执行：

```bash
git pull origin main --allow-unrelated-histories
```

处理可能的冲突后再推送。遇到冲突时不要盲目覆盖，见第 13 节。

另外两个项目只需替换文件夹名和远程地址：

```text
https://github.com/shanghaiLiyuu/orbit-dynamics-lab.git
https://github.com/shanghaiLiyuu/robot-motion-lab.git
```

## 7. 下载和运行别人的或自己的项目

以机器人项目为例：

```bash
git clone https://github.com/shanghaiLiyuu/robot-motion-lab.git
cd robot-motion-lab
python -m pip install -r requirements.txt
python -m examples.planar_arm
python -m unittest discover -s tests -v
```

更推荐为每个项目建立独立虚拟环境：

```bash
python -m venv .venv
```

Windows Git Bash 激活：

```bash
source .venv/Scripts/activate
```

Windows PowerShell 激活：

```powershell
.venv\Scripts\Activate.ps1
```

macOS／Linux 激活：

```bash
source .venv/bin/activate
```

随后再安装依赖。`.venv/` 已写入项目的 `.gitignore`，不会被提交。

## 8. 日常修改代码

每次开始工作前：

```bash
git status
git pull
```

修改后查看差异：

```bash
git status
git diff
```

暂存并提交：

```bash
git add README.md
git commit -m "Improve project usage instructions"
git push
```

一次提交添加所有受跟踪修改：

```bash
git add -u
git commit -m "Update solver documentation and tests"
```

`git add .` 会把当前目录下所有未忽略的新文件也加入暂存区，使用前应检查 `git status`。

## 9. 写好提交信息

提交信息应简短说明“做了什么”，例如：

```text
Add J2 perturbation acceleration
Fix singular support validation
Add analytical truss benchmark
Improve robot tracking figure
```

不推荐只写 `update`、`fix`、`123`。相关的小修改放在同一次提交，无关修改尽量拆开。

常用前缀可按团队习惯使用：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档
- `test:` 测试
- `refactor:` 不改变行为的代码重构

## 10. 使用分支开发新功能

创建并切换分支：

```bash
git switch -c add-beam-element
```

正常修改、提交后推送：

```bash
git push -u origin add-beam-element
```

在 GitHub 页面点击 **Compare & pull request**，检查差异并创建 Pull Request。即使独自开发，Pull Request 也有助于查看修改和等待自动测试。

功能稳定后合并，再回到主分支并更新：

```bash
git switch main
git pull
```

本地分支不再需要时可删除：

```bash
git branch -d add-beam-element
```

## 11. README、图片和自动测试

一个容易使用的算法仓库，README 至少应包含：

1. 项目解决什么问题。
2. 核心算法与适用范围。
3. 安装与运行命令。
4. 输入、输出和单位。
5. 示例结果图。
6. 测试命令。
7. 已知限制与后续方向。

Markdown 常用写法：

````markdown
# 一级标题
## 二级标题

[链接文字](https://github.com/shanghaiLiyuu)

![结果图](docs/images/example.png)

```python
print("code block")
```
````

本次三个项目都配置了 GitHub Actions。每次推送后，打开仓库的 **Actions** 页面即可查看测试是否通过。红色失败时，先点进失败任务查看第一条真正错误，不要只看最后一行。

## 12. .gitignore 与大文件

`.gitignore` 用来排除不应进入版本历史的文件，例如：

```text
__pycache__/
.venv/
*.pyc
.env
```

密钥文件 `.env` 即使只提交过一次，也可能保留在历史中；泄露后应立即更换密钥，而不只是删除文件。

GitHub 对单文件大小和仓库体积有限制。大型网格、仿真结果、视频和数据集不应直接堆进代码仓库，可使用 Release、对象存储或 Git LFS，并在 README 说明获取方式。

## 13. 常见问题

### 推送被拒绝：fetch first / non-fast-forward

远程有本地没有的新提交。先查看并合并：

```bash
git pull origin main
```

如果 Git 提示需要指定合并方式，可使用常规合并：

```bash
git pull --no-rebase origin main
```

解决冲突后：

```bash
git add 冲突文件
git commit -m "Resolve merge conflicts"
git push
```

### 文件出现冲突标记

冲突文件中可能出现：

```text
<<<<<<< HEAD
本地内容
=======
远程内容
>>>>>>> main
```

手动保留正确内容，删除这些标记，并运行测试后再提交。

### 撤销尚未提交的文件修改

先用 `git diff` 确认修改确实不需要，再恢复：

```bash
git restore 文件名
```

这个操作会丢弃该文件未提交的修改，执行前必须确认。

### 文件只是误加入暂存区，还未提交

保留文件内容，仅取消暂存：

```bash
git restore --staged 文件名
```

### 想看历史

```bash
git log --oneline --graph --decorate -10
```

### 远程地址填错

```bash
git remote -v
git remote set-url origin https://github.com/shanghaiLiyuu/正确仓库名.git
```

## 14. 发布版本

当一个算法项目达到稳定状态，可以在仓库 **Releases -> Create a new release** 中创建版本：

```text
Tag: v0.1.0
Title: v0.1.0 - Initial algorithm release
```

版本说明列出新增功能、修复、运行方式和已知限制。版本号建议遵循语义化版本：

- 主版本：不兼容的重大变化
- 次版本：向后兼容的新功能
- 修订号：向后兼容的问题修复

## 15. 推荐的长期维护节奏

1. 每次改算法先补一个可验证的测试。
2. 推送前运行测试和示例。
3. README 中的命令必须能直接执行。
4. 每个仓库只聚焦一个清晰主题。
5. 不把“能运行”当作“结果正确”，应保留解析解、守恒量或文献算例验证。
6. 在 Issues 中记录后续想法，不必一次把所有功能做完。
7. 定期检查依赖更新和 Actions 状态。

## 16. 最常用命令速查

```bash
git status                         # 查看状态
git diff                           # 查看未暂存修改
git log --oneline -10              # 查看最近十条提交
git clone 仓库地址                 # 克隆项目
git pull                           # 更新本地项目
git add 文件名                     # 暂存文件
git add .                          # 暂存当前目录全部未忽略文件
git commit -m "说明"              # 创建提交
git push                           # 推送提交
git switch -c 分支名               # 创建并切换分支
git switch main                    # 返回主分支
git remote -v                      # 查看远程地址
python -m unittest discover -s tests -v  # 运行本项目测试
```

刚开始只需熟练掌握 `status`、`add`、`commit`、`push`、`pull` 五个命令。其他操作遇到具体场景再查即可。
