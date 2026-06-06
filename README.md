English version: [README.en.md](README.en.md)

# ncm-listening-profile

你的网易云里藏着一份很长的自我备忘录：主歌单里留下的歌，最近一周反复回来的歌，所有时间里一直没有退场的歌。

`ncm-listening-profile` 会采集你确认的主歌单、最近一周听歌排行和所有时间听歌排行，生成本地数据文件和可复制给 AI 的分析 prompt。你可以把它交给自己信任的 AI，让它沿着长期偏好、近期状态、审美意象和细小异常，慢慢靠近一个更具体的你。

它把材料放到你手里，也把解释权留给你。最终要不要分析、交给谁分析、分享哪些文件，都由你决定。

## 做什么

- 启动或连接 Windows Win32 版 `cloudmusic.exe`。
- 在已登录的网易云音乐客户端页面上下文里请求网易云 `/api`。
- 列出你创建的歌单，并让你选择一个主歌单。
- 采集主歌单、最近一周听歌排行和所有时间听歌排行。
- 写出本地数据文件，并给出两版可复制给 AI 的分析 prompt。

## 环境

需要 Windows、Python 3.10+、支持 Agent Skills 的客户端，以及 NetEase Cloud Music Win32 桌面版 `cloudmusic.exe`。

目前验证过的网易云音乐版本是 `NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35`。其他版本没有保证；失败时先看 `log/collection_diagnostics.json`。

## 下载和安装

推荐从 GitHub Releases 下载打包好的 `ncm-listening-profile.zip`。

请优先下载 release 页面里的 `ncm-listening-profile.zip`，不要下载 GitHub 自动生成的 Source code 压缩包。Source code 压缩包会包含开发规格和归档文件，普通使用不需要这些内容。

解压后，把整个 `ncm-listening-profile/` 目录放到你的 Agent 客户端会扫描的 skills 目录中。不同客户端的 skills 目录可能不同，请以你正在使用的客户端文档为准。

安装 Python 依赖：

```powershell
cd <skills-dir>\ncm-listening-profile
python -m pip install -r scripts/requirements.txt
```

检查环境：

```powershell
python scripts/collect_ncm_profile.py --check
```

## 使用

在你的 Agent 客户端中调用这个 skill，例如：

```text
使用 $ncm-listening-profile 采集我的网易云音乐听歌画像数据。
```

运行时，它通常会检查环境、启动网易云音乐、列出你创建的歌单、让你选择一个主歌单，然后采集主歌单、最近一周排行和所有时间排行。采集完成后，它会输出本次 run 路径和两版分析 prompt。

## 输出文件

采集结果会写到 `outputs/YYYYMMDD-HHMMSS/`。做 AI 分析时通常使用 `aggregate/aggregate.json` 和 `result/*.jsonl`；`csv/` 适合自己打开检查，`raw/` 和 `log/` 主要用于排查问题。

请把 `outputs/` 视为私人数据，不要提交到公开仓库，也不要随意分享。

## 隐私和边界

这个项目按“本机采集、本机落盘、用户自行决定后续分享”的方式设计。

脚本设计上：

- 不要求你粘贴 cookie、token、密码、请求头或请求体。
- 不包含上传采集结果到远程服务器的逻辑。
- Python 进程只直接连接本机 CDP endpoint，例如 `127.0.0.1:9222`。
- 网易云业务 API 请求在已登录客户端页面上下文中执行。
- diagnostics 不记录完整 API response、用户名、歌单全文、歌曲全文列表、cookies、token、headers 或 post data。

本项目不是网易云音乐官方项目，也不与网易云音乐官方存在关联。它面向个人本机数据整理和 AI 辅助分析，不应用于批量采集、绕过权限、共享他人账号数据或任何违反服务条款的行为。

## 许可证

本仓库使用 MIT License，见 `LICENSE`。
