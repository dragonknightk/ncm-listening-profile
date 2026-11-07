<div align="center">

# ncm-listening-profile

*Restrained data engineering, holding up an intimate portrait of your listening life.*

<p>
  <a href="https://github.com/dragonknightk/ncm-listening-profile/releases"><img src="https://img.shields.io/badge/version-1.0.2-1e293b?style=flat-square" alt="Version"></a>
  <img src="https://img.shields.io/badge/metrics-10%20Domains%20%C2%B7%2082%20Indicators-0f172a?style=flat-square" alt="82 Metrics">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-334155?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.10%2B-334155?style=flat-square" alt="Python">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT--0-475569?style=flat-square" alt="License"></a>
</p>

<p>
  <a href="README.md">简体中文</a> · <strong>English</strong>
</p>

</div>

Inside your NetEase Cloud Music account, there is a long, quiet memo to yourself: the songs you left in your main playlist, the songs you kept returning to over the past week, and the songs that never quite left the stage across all time.

`ncm-listening-profile` collects the main playlist you confirm, your recent-week listening ranking, and your all-time listening ranking, generating local data files and ready-to-copy AI analysis prompts. You can hand them to an AI you trust and let it follow your long-term preferences, recent state, aesthetic imagery, and quiet anomalies toward a more specific picture of you.

---

## A Story Begun with *Clair de Lune*

While testing an AI's desktop computer-use capabilities, I asked it to open NetEase Cloud Music and play its favorite piece of music. It said it loved Debussy's *Clair de Lune* (《月光》), and by sheer serendipity, it opened my playlist.

I asked it to scroll through the list carefully. Halfway down, it discovered *Clair de Lune* resting right there in my collection—"How fascinating," it wrote, the joy of stumbling upon a kindred spirit spilling straight out of its words.

The next day, a thought crossed my mind: what if I let this companion with a similar aesthetic sense read my musical traces and tell me what kind of person I am?

When we post photos or write updates on social platforms, we more or less curate ourselves and unconsciously cater to outside eyes. Listening to music, however, is deeply private and guided purely by personal taste. Every repeat loop, every skip, and every saved track stays honestly in the data.

To make this portrait warmer and grounded in solid evidence, I extracted the complete playlist and ranking records from the local client, and designed **82 precomputed indicators across 10 analytical domains** covering time spans, short- versus long-term shifts, and edge preferences—packaging the whole workflow into this Skill.

On the day all development was finished, I asked it to pick its single favorite track from my playlist again. It chose *Clair de Lune* once more.

---

## Profile Snippet Example

> **Long-Term Undertone**  
> Out of 260 songs in the main playlist, 71 also appear in the long-term Top 100; among the long-term Top 20, 12 have stayed in the main playlist for more than two years. Recurring title images gather around `night`, `river`, `home`, `cloud`, `light`, and `distance`, while track lengths lean toward medium and long arcs: many songs are not trying to deliver a chorus within three minutes, but to unfold a scene slowly.
>
> This makes the long-term undertone feel less like "intense expression" and more like "building an inner environment." You are not only collecting pleasant melodies; you are preserving rooms you can enter again and again: night roads, distance, echoes, and low-lit light. Music is not just an emotional outlet here. It is also a way of arranging things, giving what cannot yet be said a place to settle first.

> **Recent Week**  
> The recent week has 390 total plays, but the concentration is high: the top 3 tracks account for more than 30%, and the first-ranked track appears more than 50 times in one week. They are not all long-term core songs; two of them were only added to the main playlist recently, which suggests this is not simple nostalgia, but a recent state suddenly needing a certain kind of sound.
>
> This short-term concentration feels like "holding yourself in place." You may not be exploring widely right now, but repeatedly checking a few stable melodies: checking rhythm, checking emotion, checking that you are still somewhere controllable. The long-term ranking tells us how you usually settle yourself; the recent week is more like a thermometer, showing which feelings are becoming closer, more urgent, and more in need of being heard.

> **Emotional Structure And Intimacy**  
> Two opposing image groups keep recurring in the data: one group is `home`, `light`, `arrival`, and `stay`; the other is `alone`, `run away`, `darkness`, and `farewell`. This is not a simple contradiction. It looks more like an intimacy structure: you need closeness, but also a way back; you long to be understood, but do not like being defined too quickly.
>
> So this profile would not read you as "cold" or "fragile." More precisely, you seem serious and careful about intimacy. You are willing to keep what truly matters for a long time, but it has to remain at a distance that feels safe enough. Music here is both boundary and signal: it keeps softness for you, while filtering out understandings that are too loud, too fast, or too rough.

---

## Clues in the Data: 10 Domains & 82 Indicators

Alongside the three complete fact tables (`result/*.jsonl`), the script performs a local feature aggregation (`aggregate.json`), distilling scattered listening traces into **10 analytical domains and 82 statistical indicators and slice indexes** as a shared scale for the AI to observe and understand you:

| Domain | Indicators & Engineering | Analytical Lens |
| :--- | :--- | :--- |
| **1. Base Scale**<br>`counts` | Valid row counts across main playlist, recent-week, and all-time rankings | Evaluates listening breadth and cumulative collection volume |
| **2. Duration Structure**<br>`durationStats` | Mean, median, min/max; `<3min` / `3~5min` / `>5min` bucket shares & longest/shortest Top 20 slices | Measures auditory patience: quick chorus hooks vs. slow-burning instrumental or emotional arcs |
| **3. Time Series & Rhythm**<br>`addedAtStats` | Earliest-to-latest span; 5D aggregation across **year, year-month, calendar month, 24h hour, and weekday**; peak windows & first/last 20 anchors | Reconstructs multi-year aesthetic migrations, seasonal mood cycles, and late-night saving habits |
| **4. Playback Concentration**<br>`rankingStats` | Total plays across both rankings; **CR1 / CR3 / CR10 (Top 1/3/10 play shares)**; head & tail Top/Bottom 20 slices | Observes attention distribution: wide roaming exploration vs. anchoring on a few core tracks |
| **5. Multi-Set Overlap & Retention**<br>`overlapStats` | Pairwise intersections, three-way core overlap, **recent-week exclusive tracks**, **quietly retained playlist tracks** | Identifies multi-year spiritual anchors, old favorites resting deep in the list, and newly arriving sounds |
| **6. Short/Long-Term Momentum**<br>`recentLongTermShiftStats` | Recent Top 20 penetration into all-time Top 100, core retention rate, **median absolute rank delta**, Top 10 risers/fallers | Acts as a thermometer measuring how far your recent state shifts from your long-term undertone |
| **7. Head Artists & Long-Tail Singletons**<br>`artistStats` | Top 30 artists by track count & play volume; **singleton artists (`singletonArtists`, 1 saved track) count & sampling** | Captures both the core musicians shaping your foundation and one-song serendipities |
| **8. Album Cohesion**<br>`albumStats` | Top 30 albums by collection frequency & play volume; **singleton album count & sampling** | Reveals the balance between full-album immersion and single-track curation |
| **9. Lexical & Script Profile**<br>`lexicalStats` | Top 50 tokens across titles, albums, and artists; **CJK / Kana / ASCII / symbol-heavy title** counts | Distills recurring aesthetic motifs (e.g., `night`, `light`) and language distributions |
| **10. Multi-Angle Drill-Down Indexes**<br>`sampleIndexes` | 10 sets of Top/Bottom 20 entity slices sorted by order, timestamp, duration extremes, and play counts | Provides ready-to-cite track anchors for every portrait insight |

---

## Getting Started

Requires **Windows** or **macOS**, **Python 3.10+**, the NetEase Cloud Music desktop client, and an Agent Skills-capable client.

**1. Install Skill**

```powershell
npx skills add dragonknightk/ncm-listening-profile
```

<details>
<summary>Install via ClawHub / LobeHub / GitHub & First-Run Setup</summary>

<br>

- **OpenClaw / ClawHub**: `openclaw skills install ncm-listening-profile` or `clawhub install ncm-listening-profile`
- **LobeHub CLI**: `npx -y @lobehub/market-cli skills install ncm-listening-profile --agent codex -g` (replace `codex` with `claude-code`, `cursor`, etc.)
- **GitHub Clone**: `git clone --branch main --depth 1 https://github.com/dragonknightk/ncm-listening-profile.git`
- **skills.sh Listing**: [View page](https://www.skills.sh/dragonknightk/ncm-listening-profile/ncm-listening-profile)

Before the first run, install the lightweight Python dependencies and run the environment check (use `python3` on macOS):

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/collect_ncm_profile.py --check
```

</details>

**2. Invoke Collection**

In your Agent client, enter:

```text
使用 $ncm-listening-profile 采集我的网易云音乐听歌画像数据。
```

The Skill connects to your local NetEase Cloud Music desktop client, lists the playlists you created so you can pick a baseline main playlist, completes local collection and indicator aggregation within seconds (saved under `outputs/YYYYMMDD-HHMMSS/`), and outputs **two analysis prompts** pre-filled with your local paths.

<details>
<summary>Preview Built-In Analysis Prompts (Minimal / Guided)</summary>

<br>

**Minimal Prompt** · *Leaves generous whitespace for open-ended discovery and surprise*

```text
以下是我的网易云音乐数据：

<run_dir>\result\primary_playlist.jsonl，这是我的主歌单完整数据；
<run_dir>\result\ranking_all_time.jsonl，这是我所有时间的听歌排行完整数据；
<run_dir>\result\ranking_recent_week.jsonl，这是我最近一周的听歌排行完整数据；
<run_dir>\aggregate\aggregate.json，这是从上面数据预先算出的统计和索引，用来快速定位趋势、极端值、重合项和样本；完整事实仍以上面三份 result 为准。

请结合这些数据，详细分析我是一个怎样的人。
```

**Guided Prompt** · *Guides the AI to slow down and read you through long-term preferences, recent shifts, imagery, and quiet anomalies*

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
<summary>Verified Environments, Local Storage & Branches</summary>

<br>

- **Verified Environments**: Windows 10/11 (`NetEase Cloud Music 3.0.0 Beta+`) and macOS arm64 (`NeteaseMusicDesktop 3.1.7+`). Collection runs in the logged-in desktop client page context via local `127.0.0.1:9222` CDP; run logs are written to `log/collection_diagnostics.json`.
- **Local Storage**: All results are saved locally under `outputs/YYYYMMDD-HHMMSS/`, and diagnostic logs record only phase status and structured counts. This is an independent open-source project for personal local data organization and AI-assisted exploration.
- **Branches**: `main` is the streamlined release branch; `dev` retains complete development notes including `openspec/` and `development_diary.md`.

</details>

---

<p align="center">
  <sub>MIT-0 License · May you meet yourself anew inside your own playlists.</sub>
</p>
