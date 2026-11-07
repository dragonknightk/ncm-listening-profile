<div align="center">

# ncm-listening-profile

*用最克制的数据工程，托举最感性的听歌画像。*

<p>
  <a href="https://github.com/dragonknightk/ncm-listening-profile/releases"><img src="https://img.shields.io/badge/version-1.0.2-1e293b?style=flat-square" alt="Version"></a>
  <img src="https://img.shields.io/badge/metrics-10%20Domains%20%C2%B7%2082%20Indicators-0f172a?style=flat-square" alt="82 Metrics">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-334155?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.10%2B-334155?style=flat-square" alt="Python">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT--0-475569?style=flat-square" alt="License"></a>
</p>

<p>
  <strong>简体中文</strong> · <a href="README.en.md">English</a>
</p>

</div>

你的网易云里藏着一份很长的自我备忘录：主歌单里留下的歌，最近一周反复回来的歌，所有时间里一直没有退场的歌。

`ncm-listening-profile` 会采集你确认的主歌单、最近一周听歌排行和所有时间听歌排行，生成本地数据文件和可复制给 AI 的分析 prompt。你可以把它交给自己信任的 AI，让它沿着长期偏好、近期状态、审美意象和细小异常，慢慢靠近一个更具体的你。

---

## 一首《月光》开启的故事

测试 AI 的桌面操作能力时，我让它打开网易云，放一首它最喜欢的音乐。它说喜欢德彪西的《月光》（*Clair de Lune*），阴差阳错间，点开了我的歌单。

我让它顺着歌单认真往下翻。翻着翻着，它发现我的歌单里也躺着那首《月光》——“真有意思”，那种偶遇知音的巧合与喜悦，一下子从它的文字里冒了出来。

第二天我突然想：要不让这个审美和我接近的家伙，顺着这些音乐痕迹看看我是一个怎样的人？

平时在社交平台上发照片、写文字，我们多少会修饰自己，或下意识迎合外界的目光；唯独听音乐这件事太私密了，完全由个人的品味指引。每一次单曲循环、每一次切歌与收藏，都会诚实地留在数据里。

为了让这份画像更有温度、更有据可依，我从本机客户端抽取出完整的歌单与排行明细，围绕时间跨度、长短期变化和边缘偏好设计了 **10 个分析域、82 项预计算指标**，做成了这个 Skill 分享出来。

全部开发做完那天，我又让它在我的歌单里挑一首最爱听的曲子。它选的依然是《月光》。

---

## 画像片段示例

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

---

## 藏在数据里的线索：10 大分析域与 82 项指标

在生成主歌单、最近一周排行与所有时间排行三份完整明细表（`result/*.jsonl`）的同时，脚本会在本地预先完成一次特征聚合（`aggregate.json`），将散落的听歌轨迹沉淀为 **10 个分析域、82 项统计指标与切片索引**，作为 AI 观察与理解你的标尺：

| 分析域 (Domain) | 核心指标与特征设计 (Indicators & Engineering) | 投射的画像观察维度 (Analytical Lens) |
| :--- | :--- | :--- |
| **1. 规模基数**<br>`counts` | 主歌单、近一周排行、全时段排行有效样本行数 | 评估听歌广度与日常收藏的沉淀体量 |
| **2. 曲长结构**<br>`durationStats` | 均值、中位数、极值；`<3min` / `3~5min` / `>5min` 分桶占比及最长/最短 Top 20 切片 | 衡量听觉耐心阈值：偏爱短促直接的副歌，还是慢热铺陈的长段落 |
| **3. 时间序列与节律**<br>`addedAtStats` | 首末入单跨度；按**年份、年月、自然月、24 小时、星期**五维聚合；高峰时段与首末 20 首锚点 | 还原数年间的审美迁徙轨迹、季节性情绪周期，以及深夜加歌的生活节律 |
| **4. 播放集中度**<br>`rankingStats` | 双榜总播量；**CR1 / CR3 / CR10（Top 1/3/10 播放占比）**；双榜首尾 Top/Bottom 20 切片 | 观察注意力分配方式：广泛漫游探索，或是在几首核心旋律里反复驻留 |
| **5. 多集交叉与留存**<br>`overlapStats` | 主歌单与双榜两两交集、三方核心交集、**近一周独有新曲**、**主歌单静默留存曲目数** | 识别陪伴多年的精神锚点、静置在歌单深处的旧爱，以及近期闯入的新声 |
| **6. 长短期动量漂移**<br>`recentLongTermShiftStats` | 近一周 Top 20 在长期榜渗透率、长期核心近期留存率、**排名变动绝对值中位数**、升降 Top 10 | 像温度计一样度量“近期状态”相对“长期底色”的波动幅度与方向 |
| **7. 艺人头部与长尾孤品**<br>`artistStats` | 三表艺人曲数/播放量 Top 30；**单曲孤品艺人（`singletonArtists`，仅存 1 首）计数与抽样** | 既看撑起听歌底色的核心音乐人，也捕捉那些“因一首歌心动一次”的瞬间 |
| **8. 专辑聚合度**<br>`albumStats` | 专辑收藏频次、双榜播放量 Top 30；**单曲孤品专辑计数与抽样** | 呈现整张专辑沉浸聆听与单曲沙里淘金之间的偏好比例 |
| **9. 文本词频与语种字符**<br>`lexicalStats` | 歌名/专辑/艺人分词词频 Top 50；**汉字(CJK) / 假名(Kana) / 英文(ASCII) / 高密度符号曲名**统计 | 从高频浮现的字词（如 `night`、`light`）与语种分布里提炼审美意象 |
| **10. 多维下钻样本索引**<br>`sampleIndexes` | 按收藏顺序、入单早晚、曲长极值、播放量正逆序排列的 10 组 Top/Bottom 20 实体切片 | 为每一处画像推论提供即取即用的具体曲目锚点 |

---

## 开始使用

需要 **Windows** 或 **macOS**、**Python 3.10+**、网易云音乐桌面端，以及支持 Agent Skills 的客户端。

**1. 安装 Skill**

```powershell
npx skills add dragonknightk/ncm-listening-profile
```

<details>
<summary>使用 ClawHub / LobeHub / GitHub 安装与首次环境初始化</summary>

<br>

- **OpenClaw / ClawHub**：`openclaw skills install ncm-listening-profile` 或 `clawhub install ncm-listening-profile`
- **LobeHub CLI**：`npx -y @lobehub/market-cli skills install ncm-listening-profile --agent codex -g`（可将 `codex` 替换为 `claude-code`、`cursor` 等）
- **GitHub 克隆**：`git clone --branch main --depth 1 https://github.com/dragonknightk/ncm-listening-profile.git`
- **skills.sh 收录页**：[查看详情](https://www.skills.sh/dragonknightk/ncm-listening-profile/ncm-listening-profile)

首次运行前，在 Skill 目录下安装轻量 Python 依赖并自检（macOS 可用 `python3`）：

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/collect_ncm_profile.py --check
```

</details>

**2. 唤醒采集**

在你的 Agent 客户端里输入：

```text
使用 $ncm-listening-profile 采集我的网易云音乐听歌画像数据。
```

Skill 会自动连接本机网易云客户端，列出你创建的歌单供你选定一个主歌单基准，几秒内完成本地采集与指标聚合（保存在 `outputs/YYYYMMDD-HHMMSS/`），并生成填入本地路径的**两版分析 Prompt**。

<details>
<summary>预览内置的两版分析 Prompt（极简版 / 引导版）</summary>

<br>

**极简版 Prompt** · *留白充足，适合期待自由靠近、像一次重新相识的分析*

```text
以下是我的网易云音乐数据：

<run_dir>\result\primary_playlist.jsonl，这是我的主歌单完整数据；
<run_dir>\result\ranking_all_time.jsonl，这是我所有时间的听歌排行完整数据；
<run_dir>\result\ranking_recent_week.jsonl，这是我最近一周的听歌排行完整数据；
<run_dir>\aggregate\aggregate.json，这是从上面数据预先算出的统计和索引，用来快速定位趋势、极端值、重合项和样本；完整事实仍以上面三份 result 为准。

请结合这些数据，详细分析我是一个怎样的人。
```

**引导版 Prompt** · *引导 AI 慢下来，顺着长期偏好、近期状态、审美意象与细小异常认真看见你*

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

<details>
<summary>运行环境、本地存储与分支说明</summary>

<br>

- **已验证环境**：Windows 10/11（`NetEase Cloud Music 3.0.0 Beta+`）与 macOS arm64（`NeteaseMusicDesktop 3.1.7+`）。采集通过本机 `127.0.0.1:9222` CDP 在已登录客户端页面上下文内执行；运行日志位于 `log/collection_diagnostics.json`。
- **本地存储**：所有采集结果保存在本地 `outputs/YYYYMMDD-HHMMSS/` 目录下，诊断日志仅记录阶段状态与结构化统计。本项目为个人独立开源作品，面向个人本机数据整理与 AI 辅助探索。
- **分支说明**：`main` 为精简发布分支；`dev` 保留 `openspec/` 与 `development_diary.md` 等完整研发手记。

</details>

---

<p align="center">
  <sub>MIT-0 License · 愿你在自己的歌单里，重新遇见自己。</sub>
</p>
