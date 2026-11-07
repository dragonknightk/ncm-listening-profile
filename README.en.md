# ncm-listening-profile

<p align="right">
  <a href="README.md">简体中文</a> · <strong>English</strong>
</p>

<p>
  <a href="https://github.com/dragonknightk/ncm-listening-profile/releases"><img src="https://img.shields.io/badge/version-1.0.2-334155" alt="Version 1.0.2"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-475569" alt="Platform Windows | macOS">
  <img src="https://img.shields.io/badge/python-3.10%2B-475569" alt="Python 3.10+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT--0-64748b" alt="License MIT-0"></a>
  <a href="https://www.skills.sh/dragonknightk/ncm-listening-profile/ncm-listening-profile"><img src="https://img.shields.io/badge/skills.sh-ncm--listening--profile-0f172a" alt="skills.sh"></a>
</p>

Inside your NetEase Cloud Music account, there is a long, quiet memo to yourself: the songs you left in your main playlist, the songs you kept returning to over the past week, and the songs that never quite left the stage across all time.

`ncm-listening-profile` collects the main playlist you confirm, your recent-week listening ranking, and your all-time listening ranking. It then generates local data files and analysis prompts that you can copy to an AI. You can hand them to an AI you trust and let it follow your long-term preferences, recent state, aesthetic imagery, and small anomalies toward a more specific picture of you.

It puts the material in your hands, and leaves the right to interpret it with you. Whether to analyze it, who to give it to, and which files to share are all your decisions.

## Profile Snippet Example

The snippets below are compressed examples generated from fictional data. They show the analysis style and do not come from real user data.

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

## What It Does

- Starts or connects to the Windows `cloudmusic.exe` or macOS `NeteaseMusic.app` desktop client.
- Calls NetEase Cloud Music `/api` endpoints from the context of the logged-in desktop client page.
- Lists the playlists you created and asks you to choose one main playlist.
- Collects the main playlist, recent-week listening ranking, and all-time listening ranking.
- Writes local data files and provides two AI analysis prompts you can copy.

## Why Go Beyond Screenshots

Sending long screenshots of your Top 100 to an LLM can produce quick impressions, but it usually stays on the surface of song titles and artist names. This skill turns scattered listening traces into a verifiable, multi-layered archive:

- **Full Timeline Instead of a Single Screen**: Beyond the recent-week and all-time rankings, it collects your complete main playlist along with **exact timestamps of when each track was added (`addedAt`)** and **millisecond track durations (`durationMs`)**. Whether a song has stayed with you for three years or was added late one night last week, the timeline preserves it.
- **Precomputed 82 Metrics Across 10 Themes (`aggregate.json`)**: Before you hand the data to an AI, the local script precomputes cross-ranking overlaps, rank shifts between recent and all-time lists, duration distributions, year/month/hour addition patterns, playback concentration (Top 1 / Top 3 / Top 10 shares), recurring lexical tokens, and singleton artist/album samples. This frees the model from counting rows or guessing ratios on the fly, significantly reducing hallucinations.
- **Collection Decoupled from Interpretation**: The skill writes clean local fact tables (`result/*.jsonl`) and neutral indexes without locking you into rigid scoring templates or a single model. You can take the same dataset to any AI you trust and explore different angles over time.

## Environment

Requires Windows or macOS, Python 3.10+, an Agent Skills-capable client, and the NetEase Cloud Music desktop client.

Verified environments:

- Windows: verified through real collection runs on Windows 10 with `NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35`, and on higher Windows systems with newer NetEase Cloud Music desktop clients.
- macOS: verified through a real collection run on `macOS 26.3.1 arm64` with `NeteaseMusicDesktop/3.1.7.3283`.

Collection depends on the local desktop client providing a logged-in page context and `9222` CDP. Data compatibility mainly depends on the NetEase server API response shape; the operating system and client version are usually not the main risk unless they affect client launch, CDP exposure, login state, or page-context execution. If collection fails, check `log/collection_diagnostics.json` first.

## Download And Install

### skills.sh

If you use an Agent client that supports `skills.sh`, install it directly with the CLI:

```powershell
npx skills add dragonknightk/ncm-listening-profile
```

You can also open the [skills.sh page](https://www.skills.sh/dragonknightk/ncm-listening-profile/ncm-listening-profile) to inspect the current listing.

### ClawHub

OpenClaw users can install it with the native command:

```powershell
openclaw skills install ncm-listening-profile
```

You can also use the ClawHub CLI to install it into the current workspace's `skills/` directory:

```powershell
clawhub install ncm-listening-profile
```

### LobeHub

Install it with LobeHub Market CLI. This example installs it into Codex's global skills directory:

```powershell
npx -y @lobehub/market-cli skills install ncm-listening-profile --agent codex -g
```

If you use another client, replace `--agent codex` with the right target, such as `open-claw`, `claude-code`, or `cursor`.

These installation commands install the Skill files only. Before the first run, you still need to install the Python dependencies below.

### GitHub

If you do not use a marketplace CLI, clone the `main` branch directly:

```powershell
git clone --branch main --depth 1 https://github.com/dragonknightk/ncm-listening-profile.git
```

After downloading it, place the entire `ncm-listening-profile/` directory into the skills directory scanned by your Agent client. Different clients may use different skills directories, so follow the documentation for the client you are using.

Install Python dependencies:

```powershell
cd <skills-dir>\ncm-listening-profile
python -m pip install -r scripts/requirements.txt
```

Check the environment:

```powershell
python scripts/collect_ncm_profile.py --check
```

On macOS, if `python` does not point to `Python 3.10+`, use `python3` in the commands above.

## Usage

Invoke this skill in your Agent client, for example:

```text
使用 $ncm-listening-profile 采集我的网易云音乐听歌画像数据。
```

### 3-Step Workflow Preview

1. **Check Environment & Choose Main Playlist**  
   The skill checks your local environment, launches or connects to the NetEase Cloud Music desktop client, and lists the playlists you created so you can pick one as your baseline main playlist:
   ```text
   下面是你创建的歌单。主歌单会作为这次画像数据的对照基准(只能选一个喔www)。你可以回复编号或歌单名。

   编号  歌单名              曲数
   1     我喜欢的音乐        260
   2     夜路与长途车        48
   3     2024 冬             31
   ```
2. **Local Collection & 82-Metric Aggregation**  
   Once you reply with a number or playlist name, the script collects your main playlist, recent-week ranking, and all-time ranking within seconds, writing cleaned fact tables and precomputed metrics to `outputs/YYYYMMDD-HHMMSS/`.
3. **Get Run Path & Two Analysis Prompts**  
   After collection finishes, the skill outputs the local run directory path along with two ready-to-copy prompts (**Minimal Prompt** and **Guided Prompt**). Copy your preferred version to any AI you trust to start the analysis.

<details>
<summary><strong>Preview: Minimal Prompt</strong> (Leaves more room for open-ended discovery and surprise)</summary>

<br>

> Best for users already comfortable conversing with AI, or when you want to keep a sense of mystery. It gives minimal direction and simply hands over the data, letting the model approach, observe, and interpret you freely.

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
<summary><strong>Preview: Guided Prompt</strong> (Slow, multi-layered reading across long-term taste, recent shifts, and quiet anomalies)</summary>

<br>

> Best when you want to be carefully seen. It guides the AI to slow down and read you through long-term preferences, recent emotional shifts, recurring imagery, life rhythms, and small edge-case details rather than producing a generic music taste summary.

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

## Output Files

Collection results are written to `outputs/YYYYMMDD-HHMMSS/`. For AI analysis, you will usually use `aggregate/aggregate.json` and `result/*.jsonl`; `csv/` is convenient for manual inspection, while `raw/` and `log/` are mainly for troubleshooting.

Treat `outputs/` as private data. Do not commit it to a public repository, and do not share it casually.

## Privacy And Boundaries

This project is designed around local collection, local file output, and user-controlled sharing.

By design, the scripts:

- Do not ask you to paste cookies, tokens, passwords, request headers, or request bodies.
- Do not include logic for uploading collected results to a remote server.
- Have the Python process connect only to a local CDP endpoint, such as `127.0.0.1:9222`.
- Make NetEase Cloud Music business API requests inside the logged-in client page context.
- Keep diagnostics from recording full API responses, usernames, complete playlists, complete song lists, cookies, tokens, headers, or post data.

This project is not an official NetEase Cloud Music project and is not affiliated with NetEase Cloud Music. It is intended for personal, local data organization and AI-assisted analysis. It should not be used for bulk collection, bypassing permissions, sharing data from someone else's account, or anything that violates terms of service.

## Origin: *Clair de Lune*

This project started with a small coincidence.

While testing desktop computer-use capabilities with an AI, I asked it to open NetEase Cloud Music and play its favorite piece of music. It said it loved Debussy's *Clair de Lune* (《月光》). Unable to locate the global search bar, it ended up looking at my playlist instead. I asked it to scroll through the playlist more carefully—and halfway down, it discovered *Clair de Lune* sitting right there in my collection. The joy of stumbling upon a kindred spirit spilled straight out of its reply.

That moment sparked the idea: music taste is deeply personal and unguarded. Unlike social profiles, we rarely pretend to be someone else inside our own playlists—what we love and what we outgrow are quietly recorded in the data. Moving from fragile UI automation to local CDP and in-page client APIs across six iterations, I built this skill with cross-platform support, 82 precomputed metrics across 10 themes, and two analysis prompts to turn those traces into a portrait.

Fittingly, after all the code was finished, I asked the AI to blindly pick one favorite track from my playlist again. It chose *Clair de Lune* a second time.

## Development And Release Branches

- `main` is the release branch. It keeps only the files needed for user installation and marketplace publication.
- `dev` is the development branch. It keeps complete development materials such as `openspec/` and `development_diary.md`.
- Publish marketplace releases to ClawHub/LobeHub from `main`; use `dev` for daily development and experiments.

## License

This project uses the MIT-0 License. See `LICENSE`.
