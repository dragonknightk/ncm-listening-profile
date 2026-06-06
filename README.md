# ncm-listening-profile

<p align="right">
  <strong>简体中文</strong> · <a href="README.en.md">English</a>
</p>

你的网易云里藏着一份很长的自我备忘录：主歌单里留下的歌，最近一周反复回来的歌，所有时间里一直没有退场的歌。

`ncm-listening-profile` 会采集你确认的主歌单、最近一周听歌排行和所有时间听歌排行，生成本地数据文件和可复制给 AI 的分析 prompt。你可以把它交给自己信任的 AI，让它沿着长期偏好、近期状态、审美意象和细小异常，慢慢靠近一个更具体的你。

它把材料放到你手里，也把解释权留给你。最终要不要分析、交给谁分析、分享哪些文件，都由你决定。

## 画像片段示例

下面是虚构数据生成的压缩片段，只展示分析风格，不来自真实用户数据。

> **长期底色**  
> 主歌单 260 首里，有 71 首也出现在长期 Top 100；长期前 20 里，有 12 首已经在主歌单里待了两年以上。反复出现的曲名意象集中在 `night`、`river`、`home`、`cloud`、`light`、`distance`，歌长也偏向中长段落：很多歌不是为了三分钟内给出副歌，而是慢慢铺开一个场景。
>
> 这会让你的长期底色不像“热烈表达”，更像“搭建内部环境”。你不是只在收藏好听的旋律，而是在保存一些可以反复进入的房间：夜路、远方、回声、低亮度的光。音乐对你来说不只是情绪出口，也像一种整理方式。它让那些说不清的东西先有地方停下。

> **最近一周**  
> 最近一周总播放 390 次，但集中度很高：前 3 首占了 30% 以上，第一名一周内出现了 50 多次。它们并不全是长期榜的核心老歌，其中有两首是最近才加入主歌单的，说明这不是简单的怀旧循环，而是近期状态突然需要某种声音。
>
> 这种短期集中很像“把自己固定住”。你可能最近不是在广泛探索，而是在抓住几段稳定旋律反复确认：确认节奏、确认情绪、确认自己还在一个可控的位置。长期榜告诉我们你平时如何安放自己，最近一周则更像一张温度计，显示某些感受正在变得更近、更急、更需要被听见。

> **情绪结构和亲密关系**  
> 数据里反复出现两组相反的意象：一组是 `home`、`light`、`arrival`、`stay`，另一组是 `alone`、`run away`、`darkness`、`farewell`。这不是简单的矛盾，更像一种亲密结构：你需要靠近，但也需要退路；你向往被理解，但不喜欢被太快定义。
>
> 所以这份画像不会把你读成“冷淡”或“脆弱”。更准确地说，你像是一个对亲密很认真、也很谨慎的人。你愿意把真正重要的东西留很久，但它必须待在一个足够安全的距离里。音乐在这里像边界，也像暗号：它替你保管柔软，同时筛掉那些太响、太快、太粗糙的理解。

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

推荐从 [GitHub Releases](https://github.com/dragonknightk/ncm-listening-profile/releases/latest) 下载打包好的 `ncm-listening-profile.zip`。

不要下载 GitHub 自动生成的 Source code 压缩包。Source code 压缩包会包含开发规格和归档文件，普通使用不需要这些内容。

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
