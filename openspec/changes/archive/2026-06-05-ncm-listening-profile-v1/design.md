## Context

The Skill targets Windows users who have the NetEase Cloud Music desktop client installed. The useful data sources are split across three places:

- CDP-rendered NetEase Cloud Music pages provide the visible playlist order, visible song fields, and listening ranking play counts.
- CDP page-context `fetch` against the NetEase Cloud Music app environment provides playlist detail `trackIds[].at`, which is the source of the song joined-at timestamp.
- The local `playingList` cache can supplement CDP rows with cache-only fields, but it is not a reliable source for playlist completeness or order because unavailable or removed songs may be absent.

The Skill is intended for distribution, so local paths cannot be hardcoded. However, run outputs intentionally live inside the Skill install directory so users can manage the Skill and its data together.

## Goals / Non-Goals

**Goals:**

- Create a distributable `ncm-listening-profile` Codex Skill.
- Collect exactly one primary user-created playlist per run.
- Collect recent-week and all-time listening rankings, including numeric play counts.
- Write repeatable run outputs under `outputs/YYYYMMDD-HHMMSS/` inside the Skill directory.
- Produce exactly nine data files per successful run: raw JSONL, result JSONL, and human-readable CSV for each of the three datasets.
- Keep result data clean enough for LLM profile analysis while preserving raw source data for troubleshooting.
- Use CDP page-context `fetch` for playlist detail and avoid direct public web requests.

**Non-Goals:**

- Do not perform personality/profile analysis inside the collector.
- Do not create `index.jsonl`, `latest_run.txt`, manifests, collection reports, or prompt output files.
- Do not silently kill an existing NetEase Cloud Music process.
- Do not support macOS, Linux, mobile clients, or web-only NetEase Cloud Music in v1.
- Do not infer unavailable-song causes beyond marking cache join status.

## Decisions

### Launch and environment discovery

The script first checks whether NetEase Cloud Music is already running. If it is running, the script stops and tells the user to close it manually. It then discovers `cloudmusic.exe`; if no executable is found or multiple candidates are found, the agent asks the user which path to use.

Alternative considered: attach to an already running client if CDP is available. This was rejected for v1 because the desired user-facing behavior is explicit: an existing NetEase Cloud Music process means the user should close it before the Skill launches the client with known CDP arguments.

### Fixed CDP port

The Skill uses port `9222`. If the port is occupied by another program, the Skill fails with a clear message that port `9222` is required and the occupying program should be closed.

Alternative considered: probe `9223`, `9224`, and other ports. This was rejected to keep the Skill predictable and easier to troubleshoot.

### CDP as the page fact source

CDP DOM extraction is the fact source for playlist order, visible song fields, ranking rows, and ranking play counts. The collector does not treat `playingList` order or count as authoritative.

Alternative considered: use UI Automation or Computer Use to read the NetEase Cloud Music window. This was rejected because the app is CEF-based, uses virtual scrolling, and CDP has already proven more stable for table extraction.

### Playlist detail through CDP page-context fetch

The collector obtains playlist detail through `fetch` executed inside the NetEase Cloud Music CDP page context, then reads `playlist.trackIds[].id` and `playlist.trackIds[].at`. The `at` value becomes `addedAt`.

Alternative considered: direct public HTTP requests from Python. This was rejected because it introduces a second network context, login state ambiguity, and avoidable compatibility risk.

### Cache left join

The primary playlist result is based on CDP rows left-joined with playlist detail and then with `playingList` cache by track ID. Missing cache rows do not fail the run. Instead, the row receives `cacheStatus=missing_from_playingList`. Cache title mismatch is marked as `cache_title_mismatch`.

Alternative considered: fail on any cache/CDP mismatch. This was rejected because NetEase Cloud Music may omit unavailable or removed songs from `playingList` even when CDP still shows them in the playlist.

### Output layout

Each successful run writes to:

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
    └── csv/
        ├── primary_playlist.csv
        ├── ranking_recent_week.csv
        └── ranking_all_time.csv
```

The timestamp uses local time with second precision and no timezone suffix. If the timestamp directory already exists, the run fails instead of adding a suffix.

Alternative considered: include run indexes, latest pointers, and manifests. This was rejected because the desired output model is a simple timestamp folder containing only data files.

### Result schemas

`result/primary_playlist.jsonl` and `csv/primary_playlist.csv` share these fields:

```text
order
title
artists
artistNames
album
duration
addedAt
durationMs
albumTransNames
trackTransNames
cacheStatus
```

`result/ranking_recent_week.jsonl`, `result/ranking_all_time.jsonl`, and their CSV files share these fields:

```text
rank
title
artists
artistNames
playCount
```

JSONL uses arrays for array fields. CSV joins array values with `|`. If `addedAt` is absent, JSONL writes `null` and CSV writes an empty string.

## Risks / Trade-offs

- NetEase Cloud Music DOM changes → Keep selectors and extraction heuristics in references, prefer semantic structure over hashed class names, and preserve raw JSONL for diagnosis.
- Port `9222` occupied → Fail loudly with a user-facing explanation instead of silently changing runtime behavior.
- User has the client already open → Ask the user to close it manually; do not kill the process.
- `playingList` missing songs → Preserve the CDP row and mark `cacheStatus=missing_from_playingList`.
- Playlist detail fetch changes or fails in CDP context → Fail clearly because `addedAt` is part of the v1 result contract.
- Output timestamp collision → Fail instead of writing to an unexpected folder.
