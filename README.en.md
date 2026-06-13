# ncm-listening-profile

<p align="right">
  <a href="README.md">简体中文</a> · <strong>English</strong>
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

### GitHub Release

If you only want the smaller package without development specs and archived change files, download the packaged `ncm-listening-profile.zip` from [GitHub Releases](https://github.com/dragonknightk/ncm-listening-profile/releases/latest).

Do not download GitHub's automatically generated Source code archives. They include development specs and archived change files that ordinary users do not need.

After extracting it, place the entire `ncm-listening-profile/` directory into the skills directory scanned by your Agent client. Different clients may use different skills directories, so follow the documentation for the client you are using.

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

During a typical run, it checks the environment, starts NetEase Cloud Music, lists the playlists you created, asks you to choose one main playlist, then collects the main playlist, recent-week ranking, and all-time ranking. After collection, it outputs the run path and two analysis prompts.

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

## Development And Release Branches

- `main` is the release branch. It keeps only the files needed for user installation and marketplace publication.
- `dev` is the development branch. It keeps complete development materials such as `openspec/` and `development_diary.md`.
- Publish packages and marketplace releases to ClawHub/LobeHub from `main`; use `dev` for daily development and experiments.

## License

This repository uses the MIT License. See `LICENSE`.
