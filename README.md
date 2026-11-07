# ncm-listening-profile

<p align="right">
  <strong>简体中文</strong> · <a href="README.en.md">English</a>
</p>

<p>
  <a href="https://github.com/dragonknightk/ncm-listening-profile/releases"><img src="https://img.shields.io/badge/version-1.0.2-334155" alt="Version 1.0.2"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-475569" alt="Platform Windows | macOS">
  <img src="https://img.shields.io/badge/python-3.10%2B-475569" alt="Python 3.10+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT--0-64748b" alt="License MIT-0"></a>
  <a href="https://www.skills.sh/dragonknightk/ncm-listening-profile/ncm-listening-profile"><img src="https://img.shields.io/badge/skills.sh-ncm--listening--profile-0f172a" alt="skills.sh"></a>
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

- 启动或连接 Windows 版 `cloudmusic.exe` 或 macOS 版 `NeteaseMusic.app`。
- 在已登录的网易云音乐客户端页面上下文里请求网易云 `/api`。
- 列出你创建的歌单，并让你选择一个主歌单。
- 采集主歌单、最近一周听歌排行和所有时间听歌排行。
- 写出本地数据文件，并给出两版可复制给 AI 的分析 prompt。

## 为什么不止于“截图给 AI”

直接把听歌排行的长截图发给大模型也能聊出几句感想，但往往停留在表面的歌手和歌名联想。这个项目做的是把零散痕迹整理成有纵深、可核对的赛博档案：

- **完整的时间线，而非静态的一屏**：除了最近一周和所有时间双榜，还会拉取完整主歌单、**每首歌加入歌单的精确时间戳（`addedAt`）**以及**毫秒级曲长（`durationMs`）**。哪首歌陪了你三年、哪批歌是某个深夜连续加进来的，数据里都有迹可循。
- **预计算 10 大主题、82 项统计指标（`aggregate.json`）**：在交给 AI 之前，本地脚本会预先算好三榜重合度、近期与长期的排名升降、曲长分布、加歌年代/月份/深夜时段分布、播放集中度（Top 1 / Top 3 / Top 10 占比）、高频词频以及“只出现过一次”的单曲孤品样本。AI 不必临场数行或心算比例，大幅减少统计幻觉，把注意力留给真正的观察。
- **数据采集与画像解读解耦**：采集过程不内置死板的打分模板，也不绑定特定大模型。同一份干净的本地数据，你可以随时交给不同 AI，从不同切面重新认识自己。

## 环境

需要 Windows 或 macOS、Python 3.10+、支持 Agent Skills 的客户端，以及网易云音乐桌面版客户端。

已验证环境：

- Windows：已在 Windows 10 + `NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35`，以及更高 Windows 系统和更新网易云桌面客户端上真实采集通过。
- macOS：已在 `macOS 26.3.1 arm64` + `NeteaseMusicDesktop/3.1.7.3283` 上真实采集通过。

采集依赖本机客户端提供的已登录页面上下文和 `9222` CDP。数据结构兼容性主要取决于网易云服务端 API；客户端或系统版本通常不是主要风险，除非它影响客户端启动、CDP 暴露、登录态或页面上下文执行。失败时先看 `log/collection_diagnostics.json`。

## 下载和安装

### skills.sh

如果你使用支持 `skills.sh` 的 Agent 客户端，可以通过 CLI 直接安装：

```powershell
npx skills add dragonknightk/ncm-listening-profile
```

也可以打开 [skills.sh 页面](https://www.skills.sh/dragonknightk/ncm-listening-profile/ncm-listening-profile) 查看当前收录信息。

### ClawHub

OpenClaw 用户可以通过原生命令安装：

```powershell
openclaw skills install ncm-listening-profile
```

也可以使用 ClawHub CLI 直接安装到当前工作目录的 `skills/`：

```powershell
clawhub install ncm-listening-profile
```

### LobeHub

可以通过 LobeHub Market CLI 安装。下面示例安装到 Codex 的全局 skills 目录：

```powershell
npx -y @lobehub/market-cli skills install ncm-listening-profile --agent codex -g
```

如果你使用其他客户端，把 `--agent codex` 换成对应目标，例如 `open-claw`、`claude-code` 或 `cursor`。

这些安装命令只负责安装 Skill 文件。首次运行前仍需要按下面步骤安装 Python 依赖。

### GitHub

如果你不使用 marketplace CLI，也可以直接克隆 `main` 分支：

```powershell
git clone --branch main --depth 1 https://github.com/dragonknightk/ncm-listening-profile.git
```

下载后，把整个 `ncm-listening-profile/` 目录放到你的 Agent 客户端会扫描的 skills 目录中。不同客户端的 skills 目录可能不同，请以你正在使用的客户端文档为准。

安装 Python 依赖：

```powershell
cd <skills-dir>\ncm-listening-profile
python -m pip install -r scripts/requirements.txt
```

检查环境：

```powershell
python scripts/collect_ncm_profile.py --check
```

macOS 如果 `python` 不是 `Python 3.10+`，把上面命令里的 `python` 换成 `python3`。

## 使用

在你的 Agent 客户端中调用这个 skill，例如：

```text
使用 $ncm-listening-profile 采集我的网易云音乐听歌画像数据。
```

### 3 步交互流程预览

1. **检查环境并列出歌单**  
   Skill 会先检查本机环境、启动或连接网易云音乐桌面端，并把你创建的歌单整理成编号表，让你确认一个作为对照基准的主歌单：
   ```text
   下面是你创建的歌单。主歌单会作为这次画像数据的对照基准(只能选一个喔www)。你可以回复编号或歌单名。

   编号  歌单名              曲数
   1     我喜欢的音乐        260
   2     夜路与长途车        48
   3     2024 冬             31
   ```
2. **本机采集与预计算聚合**  
   回复编号或歌单名后，脚本会在几秒内完成主歌单、最近一周排行与所有时间排行的采集，并自动在 `outputs/YYYYMMDD-HHMMSS/` 下写出清洗后的事实表与 82 项预计算指标。
3. **获取路径与双版本分析 Prompt**  
   采集完成后，Skill 会输出本次 run 目录路径，以及自动填好路径的**极简版 Prompt** 和**引导版 Prompt**。你可以把喜欢的版本复制给任意信任的 AI 开始分析。

<details>
<summary><strong>点击预览：内置「极简版 Prompt」</strong>（留白更多，适合期待意外感和自由靠近）</summary>

<br>

> 适合已经很熟悉和 AI 对话的人，也适合你想保留一点未知感和神秘感的时候。它不给 AI 太多方向，只把数据交出去，让对方自己靠近、观察和理解你。适合期待更自由、更意外、更像一次重新相识的分析。

```text
以下是我的网易云音乐数据：

<run_dir>\result\primary_playlist.jsonl，这是我的主歌单完整数据；
<run_dir>\result\ranking_all_time.jsonl，这是我所有时间的听歌排行完整数据；
<run_dir>\result\ranking_recent_week.jsonl，这是我最近一周的听歌排行完整数据；
<run_dir>\aggregate\aggregate.json，这是从上面数据预先算出的统计和索引，用来快速定位趋势、极端值、重合项和样本；完整事实仍以上面三份 result 为准。

请结合这些数据，详细分析我是一个怎样的人。
```

</details>

<details>
<summary><strong>点击预览：内置「引导版 Prompt」</strong>（细腻慢读，适合希望被认真看见与多维拆解）</summary>

<br>

> 适合你希望被认真看见的时候。它会引导 AI 慢下来，从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解你，而不是只给出一份音乐品味总结。适合想要更稳定、更细腻、更有温度回答的场景。

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

</details>

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

## 缘起：一首《月光》

这个项目始于一次很小的巧合。

最开始只是在测试 AI 的桌面操作能力，让它用网易云放一首最喜欢的音乐。它说想放德彪西的《月光》（*Clair de Lune*），但因为没找到全局搜索框，只看到了我的歌单。我让它顺着歌单认真往下翻——翻着翻着，它发现我的歌单里也藏着那首《月光》。那种“在漫长列表里偶遇知音”的喜悦，一下子从它的文字里冒了出来。

也是从那一刻起我意识到：听歌是私密的审美，不需要装作什么人来迎合谁，喜欢与不喜欢都会诚实地留在痕迹里。为了不靠粗糙的长截图、也不受制于易变的界面控件，我和 AI 一路从 UI 自动化深挖到本地 CDP 与客户端内建 API，最终把跨平台采集、10 个主题共 82 项预计算指标和两版分析 Prompt 打磨成了这个 Skill。

好玩的是，全部开发做完后，我又让它在我的歌单里盲挑一首最爱听的曲子。它选的依然是《月光》。

## 开发和发布分支

- `main` 是发布分支，只保留用户安装和 marketplace 发布需要的内容。
- `dev` 是开发分支，保留 `openspec/`、`development_diary.md` 等完整开发材料。
- 对外发布和上传 ClawHub/LobeHub 时，从 `main` 发布；日常开发和实验在 `dev` 进行。

## 许可证

本项目使用 MIT-0 License，见 `LICENSE`。
