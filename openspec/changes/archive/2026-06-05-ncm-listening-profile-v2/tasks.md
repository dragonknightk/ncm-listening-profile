## 1. Skill Documentation And Workflow

- [x] 1.1 Rewrite `.codex/skills/ncm-listening-profile/SKILL.md` in Chinese-first language with the v2 collection-only workflow.
- [x] 1.2 Rewrite all Skill reference Markdown files in Chinese-first language while preserving literal commands, paths, JSON keys, and schema field names.
- [x] 1.3 Update `SKILL.md` so an already-running NetEase Cloud Music process asks the user to choose recollection or an existing run before any collection or analysis action.
- [x] 1.4 Update `SKILL.md` so playlist listing is mandatory and the user must choose exactly one primary user-created playlist.
- [x] 1.5 Add the minimal analysis prompt and guided analysis prompt to `SKILL.md`, both pointing at `result/*.jsonl`.
- [x] 1.6 Add output usage and CSV field explanations to `SKILL.md` for `raw`, `result`, `csv`, and `log`.
- [x] 1.7 Update Skill self-repair instructions so agents repair the invoked Skill instance root instead of a hardcoded project path.
- [x] 1.8 Review and update `agents/openai.yaml` if the display name, short description, or default prompt is stale after the v2 documentation rewrite.

## 2. Existing Run Selection

- [x] 2.1 Add a script-level way to list existing output runs with their timestamp, success/failure shape, and available result/log paths.
- [x] 2.2 Update the agent workflow to use existing-run listing when the user chooses old data.
- [x] 2.3 Ensure using an old run reports paths and prompts without launching or attaching to NetEase Cloud Music.

## 3. Result Schema And Data Shaping

- [x] 3.1 Update primary playlist result fields to `order`, `title`, `artistNames`, `album`, `duration`, `durationMs`, and `addedAt`.
- [x] 3.2 Update ranking result fields to `rank`, `title`, `artistNames`, and `playCount`.
- [x] 3.3 Remove `artists`, `albumTransNames`, `trackTransNames`, and `cacheStatus` from result JSONL and CSV output.
- [x] 3.4 Keep cache join status and cache-derived debugging details in raw JSONL.
- [x] 3.5 Implement `duration` text parsing for `durationMs`, including `MM:SS` and longer hour-style formats if present.
- [x] 3.6 Use parsed `durationMs` for result rows even when `playingList` cache rows are missing.
- [x] 3.7 Preserve rows with special or invisible-character titles instead of filtering them as empty titles.
- [x] 3.8 Update CSV writer/tests to match the slim field lists and empty-value behavior.

## 4. Diagnostics Log

- [x] 4.1 Add a diagnostics data model and writer for `log/collection_diagnostics.json`.
- [x] 4.2 Create `log/` for every collection attempt before fragile CDP extraction phases begin.
- [x] 4.3 Record schema version, run metadata, Skill root, client version/build/patch when discoverable, executable path when available, CDP port, and target URL type.
- [x] 4.4 Record phase statuses for launch, CDP connection, playlist listing, primary playlist extraction, playlist detail fetch, ranking extraction, cache discovery, result shaping, output writing, and validation.
- [x] 4.5 Record quality counters for primary rows, recent-week rows, all-time rows, duration parse completeness, addedAt completeness, and result field completeness.
- [x] 4.6 Record failed phase, error code, error summary, and repair hints with likely files/functions when collection fails.
- [x] 4.7 Ensure diagnostics do not write full DOM, HTML, raw row text, usernames, full playlist contents, or full song lists.
- [x] 4.8 Update successful-run output validation to allow `raw/`, `result/`, `csv/`, and `log/`.
- [x] 4.9 Add failed-attempt behavior so a timestamp directory may contain only `log/collection_diagnostics.json`.

## 5. Compatibility And Self-Repair Guidance

- [x] 5.1 Add stable phase names and error codes for common compatibility failures such as playlist listing, playlist click, playlist detail fetch, ranking entry, ranking tab, ranking rows, cache discovery, and duration parsing.
- [x] 5.2 Add repair hints that point agents to relevant Skill files and functions without hardcoding the project-local root.
- [x] 5.3 Update troubleshooting reference so agents first inspect `log/collection_diagnostics.json` and attempt compatibility repair in the invoked Skill instance.
- [x] 5.4 Ensure troubleshooting guidance allows user-agent cooperation for additional sensitive materials outside diagnostics when the user explicitly chooses to share them.
- [x] 5.5 Ensure the Skill does not claim validation for NetEase Cloud Music versions beyond the local v2 validation target.

## 6. Tests

- [x] 6.1 Update output-shaping tests for the slim primary playlist and ranking schemas.
- [x] 6.2 Add tests that `durationMs` is parsed from visible `duration` and remains populated when cache rows are missing.
- [x] 6.3 Add tests that special or invisible-character titles are preserved.
- [x] 6.4 Add tests that removed v1 fields are absent from result JSONL and CSV.
- [x] 6.5 Add tests that raw JSONL still preserves cache join status.
- [x] 6.6 Add tests for diagnostics JSON structure on successful runs.
- [x] 6.7 Add tests for diagnostics JSON structure on failed attempts.
- [x] 6.8 Add tests that diagnostics do not contain forbidden sensitive payload fields.
- [x] 6.9 Add tests for listing existing output runs and reporting old-run paths.

## 7. Validation

- [x] 7.1 Run the Python unit/fixture test suite.
- [x] 7.2 Validate the Skill folder with the Skill Creator validation tool.
- [x] 7.3 Run a real-client smoke test against NetEase Cloud Music 3.0.0 Beta 64-bit, Build 201967, Patch dd70f35.
- [x] 7.4 Verify the smoke-test output contains `raw/`, `result/`, `csv/`, and `log/collection_diagnostics.json`.
- [x] 7.5 Verify smoke-test result schemas match v2 fields and prompts reference `result/*.jsonl`.
- [x] 7.6 Verify the final user-facing report includes no profile analysis and no cache-status summary.
