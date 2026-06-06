## Why

Users need a repeatable Codex Skill that collects NetEase Cloud Music listening data into analysis-ready files for personal listening profile/persona analysis. The current verified workflow is useful but machine-specific and ad hoc; this change turns it into a distributable Windows Skill with stable outputs and explicit compatibility rules.

## What Changes

- Add a `ncm-listening-profile` Skill for Windows NetEase Cloud Music data collection.
- Collect one and only one user-selected primary playlist.
- Use NetEase Cloud Music CDP control as the source of page order, visible playlist fields, and listening rankings.
- Use CDP page-context `fetch` to collect playlist detail `trackIds[].at` as the joined-at timestamp source.
- Use local `playingList` cache only as a left-joined supplemental source for fields such as `durationMs`, `albumTransNames`, and `trackTransNames`.
- Output each run under the Skill install directory at `outputs/YYYYMMDD-HHMMSS/`.
- Produce exactly three data groups per run: `raw/`, `result/`, and `csv/`, each containing primary playlist, recent-week ranking, and all-time ranking data.
- Do not create run indexes, latest pointers, manifests, or prompt files.
- Store the final analysis prompt template in `SKILL.md`.
- Fail clearly when NetEase Cloud Music is already running without CDP, port `9222` is occupied by another program, the NetEase Cloud Music executable cannot be uniquely found, or the timestamp output directory already exists.

## Capabilities

### New Capabilities
- `ncm-listening-profile`: Collect NetEase Cloud Music primary playlist and listening ranking data through CDP and local cache sources, then write raw, result, and CSV output files suitable for listening profile analysis.

### Modified Capabilities

None.

## Impact

- Adds a new Codex Skill directory, expected under the user's Codex skills directory during local installation, such as `<CODEX_HOME>\skills\ncm-listening-profile`.
- Adds Python scripts for CDP control, environment discovery, playlist detail collection, cache parsing, result shaping, and CSV/JSONL writing.
- Adds Skill references documenting environment discovery, CDP patterns, data schemas, and troubleshooting.
- Requires Windows, NetEase Cloud Music desktop client, Python, and third-party Python packages for process inspection, HTTP, and WebSocket/CDP communication.
