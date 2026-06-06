# ncm-listening-profile

<p align="right">
  <a href="README.md">简体中文</a> · <strong>English</strong>
</p>

Inside your NetEase Cloud Music account, there is a long, quiet memo to yourself: the songs you left in your main playlist, the songs you kept returning to over the past week, and the songs that never quite left the stage across all time.

`ncm-listening-profile` collects the main playlist you confirm, your recent-week listening ranking, and your all-time listening ranking. It then generates local data files and analysis prompts that you can copy to an AI. You can hand them to an AI you trust and let it follow your long-term preferences, recent state, aesthetic imagery, and small anomalies toward a more specific picture of you.

It puts the material in your hands, and leaves the right to interpret it with you. Whether to analyze it, who to give it to, and which files to share are all your decisions.

## What It Does

- Starts or connects to the Windows Win32 version of `cloudmusic.exe`.
- Calls NetEase Cloud Music `/api` endpoints from the context of the logged-in desktop client page.
- Lists the playlists you created and asks you to choose one main playlist.
- Collects the main playlist, recent-week listening ranking, and all-time listening ranking.
- Writes local data files and provides two AI analysis prompts you can copy.

## Environment

Requires Windows, Python 3.10+, an Agent Skills-capable client, and the NetEase Cloud Music Win32 desktop executable `cloudmusic.exe`.

The currently verified NetEase Cloud Music version is `NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35`. Other versions are not guaranteed; if collection fails, check `log/collection_diagnostics.json` first.

## Download And Install

It is recommended to download the packaged `ncm-listening-profile.zip` from GitHub Releases.

Prefer the `ncm-listening-profile.zip` file on the release page, rather than GitHub's automatically generated Source code archives. The Source code archives include development specs and archived change files that ordinary users do not need.

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

## License

This repository uses the MIT License. See `LICENSE`.
