---
name: ncm-listening-profile
description: 当用户想在 Windows 或 macOS 上采集网易云音乐桌面版听歌画像数据时使用。此 Skill 通过 CDP 启动或连接本机网易云音乐桌面客户端，在已登录页面上下文用网易云 `/api` 采集用户创建歌单、主歌单、最近一周听歌排行和所有时间听歌排行，写出 raw/result/csv/aggregate/log 文件，并给出两版分析 prompt；本 Skill 不在采集会话内做人格或画像分析。
---

# 网易云音乐听歌画像数据采集

## 定位

这个 Skill 只负责采集和整理网易云音乐数据，不负责在当前会话里分析“用户是一个怎样的人”。采集完成后，给用户输出结果路径、CSV 字段释义，以及两版可复制给 AI 的分析 prompt。

所有命令都在当前 Skill 根目录执行，也就是本文件所在目录。不要把修复路径写死到某个项目；在哪个 Skill 实例被调用，就修复哪个 Skill 实例。

## 用户沟通契约

Skill 被调用后的第一条用户可见回复，先输出这句话，再开始运行命令：

```text
我会帮你采集供 AI 做听歌画像分析的数据：包括你创建的歌单列表、你确认的主歌单、最近一周和所有时间听歌排行，并整理成数据文件和分析 prompt；本轮先不直接做画像结论。
```

这句话只在首次回应时说一次。后续遇到网易云已运行、端口占用、路径不唯一、需要用户选择歌单或采集成功时，直接进入对应步骤，不再重复解释 Skill 作用。

脚本 JSON 是内部材料，不要原样展示给用户。面向用户时，只展示当前步骤需要用户判断的信息。

## Python 环境

开始采集前必须先运行：

```powershell
python scripts/collect_ncm_profile.py --check
```

脚本需要 `Python 3.10+`、`psutil`、`requests`、`websocket-client`；缺依赖时用当前活跃的 Python 安装依赖。Windows 通常执行 `python -m pip install -r scripts/requirements.txt`，macOS 如果 `python` 不是 `Python 3.10+`，执行 `python3 -m pip install -r scripts/requirements.txt`。

## 标准流程

1. 进入 Skill 根目录。
2. 运行 Python 环境检查：

```powershell
python scripts/collect_ncm_profile.py --check
```

3. 如果检测到 NetEase Cloud Music 已经打开，立即停止，不要采集、不要分析、不要自动复用旧数据。展示检测到的 PID 和客户端路径，方便用户确认确实有进程存在，然后询问用户：
   - 重新采集：让用户手动关闭网易云音乐，然后继续下面的采集流程。
   - 使用旧数据：先再次运行 `python scripts/collect_ncm_profile.py --check`，再运行 `python scripts/collect_ncm_profile.py --list-runs`，让用户选择一个已有 run，并只输出路径和 prompt。

4. 重新采集时，先列出用户创建歌单：

```powershell
python scripts/collect_ncm_profile.py --list-playlists
```

5. 把用户创建歌单编号列表展示给用户，让用户确认一个主歌单。即使用户已经说出了歌单名，也必须先列表再确认。展示表格前使用这句固定话术：

```text
下面是你创建的歌单。主歌单会作为这次画像数据的对照基准(只能选一个喔www)。你可以回复编号或歌单名。
```

用户可见表格只展示：

```text
编号
歌单名
曲数
```

不要向用户展示 `playlistId`、`playCount`、`specialType`、`privacy`、`updateTime`、`source` 或脚本原始 JSON。

6. 用户选定后继续采集。通常复用第 4 步由本 Skill 启动的 9222 调试会话，优先使用用户选择的编号：

```powershell
python scripts/collect_ncm_profile.py --connect-existing-cdp --playlist-index <index>
```

如果用户明确确认歌单名，也可以按歌单名匹配：

```powershell
python scripts/collect_ncm_profile.py --connect-existing-cdp --playlist-name "<name>"
```

用户只按编号或歌单名选择主歌单；内部需要的 `playlistId` 由脚本解析后使用。

7. 采集成功后，用下面的结构收口：
   - 说明采集完成，本轮只整理数据和 prompt，不直接输出画像结论。
   - 只展示本次 run 目录，不要在 prompt 前逐条列出每个 result、CSV、aggregate 或 log 文件的完整路径。
   - 用简短列表概括 run 目录里主要文件夹和文件用途：
     - `aggregate/aggregate.json`：预计算统计和索引，帮 AI 少做临场计算。
     - `result/*.jsonl`：完整事实表，最适合给 AI 做分析。
     - `csv/*.csv`：表格预览，适合用户自己打开检查。
     - `raw/*.jsonl`：排查用的精简源数据。
     - `log/collection_diagnostics.json`：本次采集诊断日志。
   - 不展开 CSV 字段释义；告诉用户“CSV 字段释义这次不展开；如果你看 CSV 时有不清楚的字段，可以直接问 AI。”
   - 展示极简版 prompt 和适用场景说明。
   - 展示引导版 prompt 和适用场景说明。

不要输出画像分析结论。输出两版 prompt 时，“适用场景说明”必须完整复制本文件中的原文，不要概括、缩短或改写。

## Reference 路由

- 环境检测、进程、端口、路径：读 `references/environment.md`。
- API 结构、歌单筛选、接口字段：读 `references/api-patterns.md`。
- result、raw、CSV、aggregate、输出布局或 diagnostics 字段变更：读 `references/schemas.md`。
- 采集失败、输出质量可疑或需要自修复：读 `references/troubleshooting.md`。

## 输出目录

每次采集尝试都会创建：

```text
outputs/
└── YYYYMMDD-HHMMSS/
    └── log/
        └── collection_diagnostics.json
```

成功采集还会包含：

```text
outputs/
└── YYYYMMDD-HHMMSS/
    ├── raw/
    │   ├── primary_playlist.jsonl
    │   ├── ranking_recent_week.jsonl
    │   └── ranking_all_time.jsonl
    ├── result/
    │   ├── primary_playlist.jsonl
    │   ├── ranking_recent_week.jsonl
    │   └── ranking_all_time.jsonl
    ├── csv/
    │   ├── primary_playlist.csv
    │   ├── ranking_recent_week.csv
    │   └── ranking_all_time.csv
    ├── aggregate/
    │   └── aggregate.json
    └── log/
        └── collection_diagnostics.json
```

失败的 run 可以只有 `log/collection_diagnostics.json`。这是正常状态，后续 agent 应该先读这份日志定位问题。

不要创建 `index.jsonl`、`latest_run.txt`、manifest、collection report、`analysis_prompt.txt` 或其他 prompt 文件。

## 文件用途

- `result/*.jsonl`：完整逐行事实表，正式给 AI/agent 做分析和计算。它保留数字类型，适合计算平均歌长、长短曲比例、添加时间分布、排行重合度。
- `aggregate/aggregate.json`：预计算统计和中性索引，用来减轻 AI 临场计算压力。它不是画像结论，也不是完整事实来源。
- `csv/*.csv`：给人类预览和手工检查，也适合用户复制到普通表格工具。
- `raw/*.jsonl`：排错用，保留精简 API 源字段，例如歌曲、艺人、专辑、歌长、加入时间、排行、播放次数和可选 `score`。

`aggregate` 里带有 `top`、`bottom`、`earliest`、`latest`、`overlap`、`sample` 的字段，都是按字段名写明数量和排序口径的截断索引，不代表分析边界。完整逐行数据仍以 `result/*.jsonl` 为准。

## Raw 边界

raw 只写：

```text
raw/primary_playlist.jsonl
raw/ranking_recent_week.jsonl
raw/ranking_all_time.jsonl
```

`/api/user/playlist` 只用于让用户选择主歌单，不写 `raw/user_playlists.jsonl`。

raw 不保存以下内容：

```text
creator
subscribers
privileges
coverImgUrl
recommendInfo
完整 API response
cookies/token/header/post data
```

## Result 字段

`result/primary_playlist.jsonl` 和 `csv/primary_playlist.csv` 字段：

```text
order
title
artistNames
album
duration
durationMs
addedAt
```

`result/ranking_recent_week.jsonl`、`result/ranking_all_time.jsonl` 及对应 CSV 字段：

```text
rank
title
artistNames
playCount
```

`songId`、`artistId`、`albumId`、`score` 不出现在 result/csv。`score` 如存在，只允许保留在 raw。

`title` 可能包含特殊字符或不可见 Unicode 字符，不要把这种歌曲当成空标题删除。

## CSV 字段释义

`primary_playlist.csv`：

```text
order        主歌单中的顺序
title        歌名；可能包含特殊字符或不可见字符，不要自动删除
artistNames  艺人名，多个艺人用 / 连接
album        专辑名
duration     人类可读歌长，如 03:58
durationMs   毫秒歌长，用于计算平均歌长、长曲比例、短曲比例
addedAt      加入主歌单的时间
```

`ranking_recent_week.csv` / `ranking_all_time.csv`：

```text
rank         排名
title        歌名
artistNames  艺人名，多个艺人用 / 连接
playCount    播放次数
```

## Aggregate 口径

`aggregate/aggregate.json` 是一份 JSON 树，主要包含：

```text
sources             本次聚合读取的 result/raw 相对路径
counts              主歌单、最近一周排行、所有时间排行行数
durationStats       平均/中位/最短/最长歌长，短中长分布，最长/最短索引
addedAtStats        最早/最新加入时间，年/月/小时/星期分布，最早/最新加入索引
rankingStats        播放总量、Top1/Top3/Top10 占比，排行头尾索引
overlapStats        主歌单、最近一周、所有时间之间的重合数量和重合索引
recentLongTermShiftStats 最近一周排行和所有时间排行之间的核心重合、活跃延续和排名升降索引
artistStats         艺人出现次数、播放量索引、单曲艺人数量和样本
albumStats          专辑出现次数、播放量索引、单曲专辑数量和样本
lexicalStats        歌名、专辑、艺人文本词频和字符类型统计
sampleIndexes       若干常用样本索引
```

aggregate 只做计算，不写人格画像、不写证据强弱、不替 AI 固定分析模板。

## 极简版 Prompt

采集完成后，把 `<run_dir>` 替换为本次 run 的绝对路径：

```text
以下是我的网易云音乐数据：

<run_dir>\result\primary_playlist.jsonl，这是我的主歌单完整数据；
<run_dir>\result\ranking_all_time.jsonl，这是我所有时间的听歌排行完整数据；
<run_dir>\result\ranking_recent_week.jsonl，这是我最近一周的听歌排行完整数据；
<run_dir>\aggregate\aggregate.json，这是从上面数据预先算出的统计和索引，用来快速定位趋势、极端值、重合项和样本；完整事实仍以上面三份 result 为准。

请结合这些数据，详细分析我是一个怎样的人。
```

适合已经很熟悉和 AI 对话的人，也适合你想保留一点未知感和神秘感的时候。它不给AI太多方向，只把数据交出去，让对方自己靠近、观察和理解你。适合期待更自由、更意外、更像一次重新相识的分析。

## 引导版 Prompt

采集完成后，把 `<run_dir>` 替换为本次 run 的绝对路径：

```text
以下是我的网易云音乐数据：

<run_dir>\result\primary_playlist.jsonl，这是我的主歌单完整数据；
<run_dir>\result\ranking_all_time.jsonl，这是我所有时间的听歌排行完整数据；
<run_dir>\result\ranking_recent_week.jsonl，这是我最近一周的听歌排行完整数据；
<run_dir>\aggregate\aggregate.json，这是从上面数据预先算出的统计和索引，用来快速定位趋势、极端值、重合项和样本；完整事实仍以上面三份 result 为准。

请结合这些数据，详细地分析我是一个怎样的人。

我希望你把这些音乐数据当作认识一个人的线索：它们既有长期留下来的偏好，也有最近一周的状态波动；既有高频反复出现的核心，也有低频、边缘、偶然出现但可能很重要的细节。

请尽量写得像是在认真理解一个具体的人，而不是在汇报一份数据表。统计数字只在它能照亮判断时出现，歌曲、艺人、专辑、添加时间、播放排行和重合关系，都可以成为你展开理解的依据。

你可以从这些角度自由展开：
- 长期稳定的音乐偏好和审美气质；
- 最近一周透露出的状态变化；
- 主歌单、长期排行、最近排行之间的关系；
- 歌曲标题、专辑名、艺人分布里反复出现的意象；
- 歌曲时长、添加时间、播放集中度透露出的生活节奏；
- 可能的情绪结构、注意力模式、亲密关系和自我关系倾向；
- 高频核心之外，那些低频、异常、很早加入、最近加入、倒数或边缘的数据里可能藏着的细节。

请在有把握的地方写得清晰一点，在只是轻微线索的地方保持细腻和克制。最终我希望看到的不是“音乐品味总结”，而是一幅有证据、有温度、有细节的人物画像。
```

适合你希望被认真看见的时候。它会引导AI慢下来，从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解你，而不是只给出一份音乐品味总结。适合想要更稳定、更细腻、更有温度回答的场景。

## 运行规则

- 支持 Windows 桌面版 `cloudmusic.exe` 和 macOS 桌面版 `NeteaseMusic.app`。
- 固定使用 CDP 端口 `9222`，不要尝试其他端口。
- 如果 NetEase Cloud Music 已经运行，要求用户手动关闭；不要 kill 进程。
- 如果客户端找不到或找到多个候选路径，询问用户准确路径并传入 `--client-path`。
- Windows 显式路径示例：`python scripts/collect_ncm_profile.py --client-path "D:\CloudMusic\cloudmusic.exe" --list-playlists`。
- macOS 显式路径示例：`python3 scripts/collect_ncm_profile.py --client-path "/Applications/NeteaseMusic.app" --list-playlists`。
- 如果端口 `9222` 被占用，要求用户关闭占用程序。
- Python 只连接本机 CDP endpoint；网易云业务数据必须在已登录页面上下文内通过 `fetch(..., { credentials: "include" })` 获取。
- 主动业务 API 只允许使用 `/api/nuser/account/get`、`/api/user/playlist`、`/api/v6/playlist/detail`、`/api/v1/play/record`。
- 任何关键 API 失败、状态异常、返回结构不符合预期或关键数据集为空，本次采集失败并写 diagnostics；`ranking_recent_week` 允许 0 行，表示最近一周没有听歌记录。
- `durationMs` 来自 API 毫秒歌长，`duration` 由 `durationMs` 格式化。

## 诊断和自修复

每次采集尝试都会写 `log/collection_diagnostics.json`。如果采集失败，后续 agent 必须先读这份日志，按 `failedPhase`、`errorCode`、`repairHints` 定位问题，并优先在当前被调用的 Skill 实例内修复兼容性。

诊断日志不记录完整 API response、用户名、歌单全文、歌曲全文列表、cookies、token、headers 或 post data。它只记录版本/环境、阶段状态、接口路径、状态码、响应形状、结果行数、质量计数、错误摘要和修复提示。

已验证环境：

```text
Windows：已在 Windows 10 + NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35，以及更高 Windows 系统和更新网易云桌面客户端上真实采集通过。
macOS：已在 macOS 26.3.1 arm64 + NeteaseMusicDesktop/3.1.7.3283 上真实采集通过。
```

采集链路主要依赖网易云桌面客户端提供的已登录页面上下文和本机 CDP；数据结构兼容性主要取决于网易云服务端 API。客户端或系统版本通常不是主要风险，除非它影响客户端启动、CDP 暴露、登录态或页面上下文执行。

按前面的 Reference 路由读取对应参考文档。
