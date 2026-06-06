# ncm-listening-profile

Windows 上的 Codex Skill，用于从网易云音乐桌面版采集听歌画像分析所需的数据。

这个 Skill 只负责采集和整理数据，不在采集会话里直接判断“你是一个怎样的人”。采集完成后，它会写出结构化数据文件，并给出可复制到新 AI 会话中的分析 prompt。

## 功能

- 启动或连接 Windows Win32 版 `cloudmusic.exe`。
- 通过 CDP 连接本机 `9222` 调试端口。
- 在已登录的网易云音乐客户端页面上下文里请求网易云 `/api`。
- 采集用户创建歌单列表，并要求用户选择一个主歌单。
- 采集主歌单、最近一周听歌排行、所有时间听歌排行。
- 写出 `raw`、`result`、`csv`、`aggregate` 和 `log` 文件。
- 生成两版供 AI 分析用的 prompt。

## 适用环境

- Windows
- NetEase Cloud Music Win32 桌面版 `cloudmusic.exe`
- Python 3.10+
- Codex Skills 目录结构

当前已验证客户端：

```text
NetEase Cloud Music 3.0.0 Beta 64-bit
Build 201967
Patch dd70f35
```

其他版本没有保证。如果采集失败，优先查看本次 run 的 `log/collection_diagnostics.json`。

## 安装

把 Skill 目录复制到你的 Codex skills 目录下：

```text
.codex/skills/ncm-listening-profile
```

仓库里的 Skill 本体位于：

```text
.codex/skills/ncm-listening-profile/
```

安装依赖：

```powershell
cd .codex/skills/ncm-listening-profile
python -m pip install -r scripts/requirements.txt
```

检查环境：

```powershell
python scripts/collect_ncm_profile.py --check
```

## 使用方式

在 Codex 中提出类似请求：

```text
帮我采集网易云音乐听歌画像数据
```

Skill 的标准流程是：

1. 检查 Python 环境和依赖。
2. 如果网易云音乐已经运行，要求你手动关闭，或选择使用旧数据。
3. 启动带 CDP 端口的网易云音乐客户端。
4. 列出你创建的歌单，只展示编号、歌单名和曲数。
5. 让你选择一个主歌单。
6. 采集主歌单、最近一周排行、所有时间排行。
7. 输出本次 run 路径和两版分析 prompt。

如果 `cloudmusic.exe` 无法自动发现，可以手动指定路径：

```powershell
python scripts/collect_ncm_profile.py --cloudmusic-exe "D:\CloudMusic\cloudmusic.exe" --list-playlists
```

## 输出目录

每次采集会在 Skill 目录下创建：

```text
outputs/
└── YYYYMMDD-HHMMSS/
    ├── raw/
    ├── result/
    ├── csv/
    ├── aggregate/
    └── log/
```

主要文件用途：

- `aggregate/aggregate.json`：预计算统计和中性索引，帮 AI 少做临场计算。
- `result/*.jsonl`：完整事实表，最适合给 AI 做分析。
- `csv/*.csv`：表格预览，适合人工检查。
- `raw/*.jsonl`：排查用的精简源数据。
- `log/collection_diagnostics.json`：本次采集诊断日志。

失败的 run 可能只有 `log/collection_diagnostics.json`，这是正常状态。

## 隐私边界

这个 Skill 会读取你的网易云音乐登录态下可访问的数据，但不会要求你手动粘贴 cookie、token、密码或请求头。

Python 进程只直接访问本机 CDP endpoint：

```text
http://127.0.0.1:9222/json/version
http://127.0.0.1:9222/json
ws://127.0.0.1:9222/...
```

网易云业务 API 请求在已登录客户端页面上下文中执行：

```text
fetch(..., { credentials: "include" })
```

诊断日志不会记录完整 API response、用户名、歌单全文、歌曲全文列表、cookies、token、headers 或 post data。

公开分享或提交代码前，请确认不要提交：

- `.codex/skills/ncm-listening-profile/outputs/`
- 任何真实采集出的 `raw`、`result`、`csv`、`aggregate`、`log`
- 本机路径、账号名、邮箱等你不想公开的信息

## 开发和测试

运行单元测试：

```powershell
python .codex/skills/ncm-listening-profile/scripts/test_ncm_profile.py
```

注意不要使用下面这种形式：

```powershell
python -m unittest .codex/skills/ncm-listening-profile/scripts/test_ncm_profile.py
```

因为 `.codex` 以点开头，`unittest` 会把它当作模块路径语义，可能触发 `ValueError: Empty module name`。

## 仓库结构

```text
.codex/skills/ncm-listening-profile/
├── SKILL.md
├── agents/
├── references/
└── scripts/

openspec/
└── specs and archived change notes
```

`.codex/skills/ncm-listening-profile/` 是实际可安装的 Skill。`openspec/` 是开发过程中的规格和设计记录。

## 非官方声明

本项目不是网易云音乐官方项目，也不与网易云音乐官方存在关联。

它面向个人本机数据整理和 AI 辅助分析，不应用于批量采集、绕过权限、共享他人账号数据或任何违反服务条款的行为。

## 许可证

本仓库暂未选择许可证。正式公开前请添加 `LICENSE` 文件，并在本节更新许可证名称。

如果希望别人可以自由使用、修改、分发和二次开发，推荐使用 MIT License。如果希望别人修改后也必须继续开源，可以选择 GNU GPLv3。如果只是想公开代码但暂时不授权别人复用，可以先不添加开源许可证。
