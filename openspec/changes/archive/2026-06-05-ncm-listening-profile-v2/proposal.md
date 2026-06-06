## Why

The v1 Skill can collect NetEase Cloud Music data, but real use exposed UX, analysis-data, and compatibility gaps: agents may reuse old data without asking, may analyze inside the collection session, and have little machine-readable evidence when a NetEase Cloud Music version changes DOM behavior. This change tightens the Skill into a Chinese-first, collection-only workflow with cleaner result fields and per-run diagnostics that help downstream agents repair compatibility in the Skill instance being used.

## What Changes

- Make all Skill Markdown instructions and references Chinese-first, while preserving command names, field names, paths, and JSON keys in English.
- Change the collection workflow so an already-running NetEase Cloud Music client stops the flow and asks whether to recollect or use an old run.
- Always list user-created playlists and ask the user to choose exactly one primary playlist; do not silently skip playlist listing just because a name is known.
- Keep collection and profile analysis separate: the Skill reports collection status, result paths, CSV field meanings, and two reusable prompts, but does not perform the listening-profile analysis itself.
- Provide two analysis prompts in `SKILL.md`: a minimal prompt with little model guidance and a guided prompt that asks the model/agent to compute statistics before drawing profile conclusions.
- **BREAKING**: Slim result schemas by removing duplicate/noisy analysis fields:
  - Primary playlist result keeps `order`, `title`, `artistNames`, `album`, `duration`, `durationMs`, and `addedAt`.
  - Ranking results keep `rank`, `title`, `artistNames`, and `playCount`.
  - `artists`, `albumTransNames`, `trackTransNames`, and `cacheStatus` are removed from result JSONL/CSV.
- Derive `durationMs` from the visible `duration` text for result rows so missing `playingList` cache rows do not prevent duration statistics.
- Keep raw JSONL as the debugging source, including cache join information such as `cacheStatus`; do not surface cache status in result files or final collection summaries.
- Keep special or invisible-character song titles as valid song data; do not drop them as empty titles.
- Clarify output usage: `result/*.jsonl` is the preferred input for AI/agent analysis and calculation, `csv/*.csv` is for human preview and manual inspection, and `raw/*.jsonl` is for troubleshooting.
- Add `log/collection_diagnostics.json` to every collection attempt, successful or failed, with privacy-preserving, machine-readable environment, phase, quality, and repair-hint diagnostics.
- Allow failed attempts to create a timestamp run directory containing only `log/collection_diagnostics.json`.
- Teach agents to use diagnostics to repair compatibility in the current Skill instance being used, whether project-local or global, before escalating to the user.
- Do not record full DOM, HTML, raw row text, usernames, full playlist contents, or full song lists in diagnostics by default.
- Validate v2 against the current local NetEase Cloud Music client only: 3.0.0 Beta 64-bit, Build 201967, Patch dd70f35.

## Capabilities

### New Capabilities
- `ncm-listening-profile`: Collect NetEase Cloud Music primary playlist and listening ranking data with Chinese-first Skill instructions, slim analysis-ready results, dual analysis prompts, and privacy-preserving per-attempt diagnostics for compatibility repair.

### Modified Capabilities

None.

## Impact

- Updates the project-local `ncm-listening-profile` Skill under `.codex/skills/ncm-listening-profile/`.
- Updates `SKILL.md` and reference Markdown files to Chinese-first instructions and revised workflow rules.
- Updates Python output shaping to use slim result fields and parse `durationMs` from `duration`.
- Updates output writing to include `log/collection_diagnostics.json` and to support failed-attempt log-only run directories.
- Updates tests for schema changes, duration parsing, diagnostic log writing, failed-attempt output behavior, and preservation of special/invisible-character titles.
- Updates Skill UI metadata if the Chinese-first workflow or prompts make the current `agents/openai.yaml` stale.
