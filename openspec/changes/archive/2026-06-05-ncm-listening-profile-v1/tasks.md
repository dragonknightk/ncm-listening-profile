## 1. Skill Structure

- [x] 1.1 Initialize the `ncm-listening-profile` Skill folder under the Codex skills directory.
- [x] 1.2 Create `SKILL.md` with trigger description, one-primary-playlist workflow, fixed output contract, and the reusable LLM analysis prompt template.
- [x] 1.3 Create `agents/openai.yaml` metadata for the Skill UI entry.
- [x] 1.4 Create reference files for environment discovery, CDP patterns, data schemas, and troubleshooting.
- [x] 1.5 Add Python dependency documentation or helper checks for required third-party packages.

## 2. Environment And Launch

- [x] 2.1 Implement detection for already running NetEase Cloud Music processes and stop with a user-facing close-client instruction.
- [x] 2.2 Implement `cloudmusic.exe` discovery with unique-path enforcement and user clarification when none or multiple candidates are found.
- [x] 2.3 Implement fixed port `9222` availability checks and fail when the port is occupied by another program.
- [x] 2.4 Implement NetEase Cloud Music launch with CDP arguments on port `9222`.
- [x] 2.5 Implement local `playingList` path discovery from the Windows user environment without hardcoding a username.

## 3. CDP Collection

- [x] 3.1 Implement CDP target discovery and connection for the NetEase Cloud Music CEF page.
- [x] 3.2 Implement page evaluation, DOM click, keyboard, wait, and virtual-scroll helpers.
- [x] 3.3 Implement collection of user-created playlists from the NetEase Cloud Music sidebar.
- [x] 3.4 Implement primary playlist navigation, playback-list preparation, and full visible-row extraction.
- [x] 3.5 Implement CDP page-context `fetch` for playlist detail and extraction of `trackIds[].id` and `trackIds[].at`.
- [x] 3.6 Implement recent-week listening ranking navigation and row extraction.
- [x] 3.7 Implement all-time listening ranking navigation and row extraction.

## 4. Data Joining And Shaping

- [x] 4.1 Implement raw JSONL shaping for primary playlist rows with CDP row, playlist detail row, optional `playingList` row, and `cacheStatus`.
- [x] 4.2 Implement raw JSONL shaping for recent-week and all-time ranking rows with CDP ranking source rows.
- [x] 4.3 Implement primary playlist result shaping with `order`, `title`, `artists`, `artistNames`, `album`, `duration`, `addedAt`, `durationMs`, `albumTransNames`, `trackTransNames`, and `cacheStatus`.
- [x] 4.4 Implement ranking result shaping with `rank`, `title`, `artists`, `artistNames`, and `playCount`.
- [x] 4.5 Implement `addedAt` formatting so JSONL writes `null` when missing and CSV writes an empty value.
- [x] 4.6 Implement array-to-CSV formatting with `|` separators.

## 5. Output Writing

- [x] 5.1 Implement run directory creation at `outputs/YYYYMMDD-HHMMSS/` inside the Skill install directory.
- [x] 5.2 Implement timestamp collision failure without suffixing or overwriting.
- [x] 5.3 Write `raw/primary_playlist.jsonl`, `raw/ranking_recent_week.jsonl`, and `raw/ranking_all_time.jsonl`.
- [x] 5.4 Write `result/primary_playlist.jsonl`, `result/ranking_recent_week.jsonl`, and `result/ranking_all_time.jsonl`.
- [x] 5.5 Write `csv/primary_playlist.csv`, `csv/ranking_recent_week.csv`, and `csv/ranking_all_time.csv`.
- [x] 5.6 Ensure no `index.jsonl`, `latest_run.txt`, manifest, collection report, or `analysis_prompt.txt` file is created.

## 6. Validation

- [x] 6.1 Add unit tests or fixture tests for result shaping, cache left join, `addedAt` handling, and CSV formatting.
- [x] 6.2 Add fixture tests that verify the run output contains exactly the expected nine files.
- [x] 6.3 Validate the Skill folder with the Skill Creator validation script.
- [x] 6.4 Run a real-client smoke test with NetEase Cloud Music closed before launch.
- [x] 6.5 Verify the smoke-test output schemas match the primary playlist and ranking result contracts.
