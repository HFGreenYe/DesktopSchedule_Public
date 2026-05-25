# Device Sync Guide

本文件记录本项目在台式机、笔记本之间通过临时私有仓库 `DesktopSchedule_Temp` 同步工作的流程。

## 当前同步策略

- 临时 GitHub 仓库：`https://github.com/HFGreenYe/DesktopSchedule_Temp.git`
- 当前本地分支：`main`
- 当前本地 `main` 已跟踪：`temp/main`
- 原正式仓库 remote 仍保留为 `origin`，但当前阶段不要推送到 `origin`。

注意：后续只使用临时仓库同步，不执行：

```cmd
git push origin main
```

## 台式机当前状态

台式机项目目录：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule
```

台式机已经完成：

```cmd
git push -u temp main
```

并确认：

```text
main -> temp/main
working tree clean
```

台式机这几天不再改代码，因此后续回来时可以直接从 `temp/main` 拉取。

## 笔记本第一次接手

在笔记本上选择工作目录，例如：

```cmd
cd /d D:\CodeProjects
```

克隆临时私有仓库：

```cmd
git clone https://github.com/HFGreenYe/DesktopSchedule_Temp.git DesktopSchedule
cd DesktopSchedule
```

创建虚拟环境并安装依赖：

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

确认状态：

```cmd
git status
git branch -vv
```

预期：

- 工作区干净。
- `main` 跟踪远端 `origin/main` 或克隆仓库默认远端分支。

## 笔记本日常工作流程

开始工作前先拉取：

```cmd
git pull
git status
```

完成一个小阶段后提交：

```cmd
git add ...
git commit -m "..."
git push
```

如果不确定应该提交哪些文件，先运行：

```cmd
git status
git diff --name-only
```

不要提交无关本地文件、临时文件或虚拟环境目录。

## 回到台式机继续工作

因为台式机期间不会改代码，所以回到台式机后直接：

```cmd
cd /d D:\CodeProjects\DesktopSchedule\DesktopSchedule
git pull
git status
```

这会把笔记本推到 `DesktopSchedule_Temp` 的更新原地拉回台式机项目目录。

不要下载 ZIP 覆盖本地目录。使用 `git pull` 更安全，因为它会保留 `.git` 历史和本地环境。

## 依赖处理

`.venv` 通常不会进入 Git。台式机原来的虚拟环境会保留。

如果笔记本期间没有修改 `requirements.txt`，回到台式机后一般不需要重装依赖。

如果笔记本期间修改了 `requirements.txt`，回到台式机 `git pull` 后执行：

```cmd
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 代理问题

当前 Git 全局代理已改为：

```cmd
http://127.0.0.1:7897
```

可用以下命令检查：

```cmd
git config --global --get http.proxy
git config --global --get https.proxy
```

如 GitHub 推送失败并出现类似：

```text
Failed to connect to github.com port 443 via 127.0.0.1
```

通常说明代理软件未启动，或端口不一致。

确认代理软件端口后重新设置，例如：

```cmd
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
```

如果当前网络可直连 GitHub，可临时取消代理：

```cmd
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 如果发生本地未提交改动

回到台式机后，如果执行：

```cmd
git status
```

发现有未提交改动，不要直接 `git pull`。先记录状态：

```cmd
git status
git diff --name-only
```

然后再决定：

- 提交本地改动。
- 暂存本地改动。
- 备份后丢弃本地改动。

如果不确定，先不要操作，把 `git status` 输出交给顾问窗口判断。

## 当前项目进度标记

截至本次同步：

- 第一轮：已归档。
- 第二轮：已归档。
- 第三轮：已归档。
- 第四轮：已归档。
- 下一步：第五轮“提醒与运行期状态服务”阶段合同/规划。

进度估算：

- 按核心 8 轮架构改写算：约 50%。
- 如果把第九轮新功能准备也算入总目标：约 44%。
