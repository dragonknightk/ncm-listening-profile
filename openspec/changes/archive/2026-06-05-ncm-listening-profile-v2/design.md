## Context

The v1 Skill already launches the Windows NetEase Cloud Music desktop client through CDP, asks for one primary playlist, collects playlist/ranking data, and writes raw JSONL, result JSONL, and CSV files. Real usage exposed three issues that need a v2 design pass:

- The Skill instructions are English-first and not strict enough about when to stop, ask the user, or avoid analysis in the collection session.
- Result files include fields that are useful for debugging but noisy or duplicated for profile analysis.
- Compatibility failures in newer or different NetEase Cloud Music clients are hard to diagnose because failed runs do not leave a machine-readable repair map.

The current local validation target for v2 is NetEase Cloud Music 3.0.0 Beta 64-bit, Build 201967, Patch dd70f35. v2 does not claim validation against newer client versions.

## Goals / Non-Goals

**Goals:**

- Make the Skill Markdown files Chinese-first while keeping commands, paths, field names, and JSON keys literal.
- Make the runtime workflow collection-only: collect data, report paths and prompts, and do not perform profile analysis in the same session.
- Require explicit user choice when NetEase Cloud Music is already running: recollect after closing the client, or use an old run.
- Require explicit selection of exactly one user-created playlist after listing available user-created playlists.
- Slim result JSONL/CSV schemas to analysis-useful fields.
- Preserve `durationMs` for later statistics, deriving it from visible `duration` text instead of relying on `playingList`.
- Preserve special or invisible-character song titles as valid data.
- Emit a privacy-preserving `log/collection_diagnostics.json` for every collection attempt.
- Make diagnostics useful to later agents for repairing compatibility in whichever Skill instance was invoked.
- Keep raw JSONL as the troubleshooting source and result JSONL as the preferred AI/agent analysis source.

**Non-Goals:**

- Do not add in-session listening-profile/personality analysis to the Skill.
- Do not validate or claim support for NetEase Cloud Music versions other than the current local 3.0.0 Beta validation target.
- Do not write prompt files, run indexes, latest pointers, or manifests.
- Do not add a debug snapshot mode that writes full DOM, HTML, raw row text, usernames, full playlist contents, or full song lists to diagnostics.
- Do not prevent a user from voluntarily sharing additional sensitive data with an agent during a later repair conversation; the restriction applies to what the Skill writes to `collection_diagnostics.json`.
- Do not hardcode the project-local Skill path as the only repair target.

## Decisions

### Chinese-first Skill docs

All Markdown files inside the Skill folder will use Chinese as the main language. Literal command lines, file names, JSON keys, schema fields, and error codes remain in English so agents can copy commands and match code symbols exactly.

Alternative considered: keep English references and only translate `SKILL.md`. This was rejected because failure handling and schema interpretation live in references too; mixed-language Skill docs make later agents more likely to miss key workflow rules.

### Collection-only workflow with two prompts

The Skill will stop after collection status, output paths, CSV field explanations, and two prompts:

- A minimal prompt that gives the result JSONL paths and asks for a detailed profile.
- A guided prompt that asks the model/agent to compute statistics before drawing conclusions.

Alternative considered: run profile analysis inside the Skill. This was rejected because collection consumes a large turn budget and lowers analysis quality; the analysis should happen in a fresh session with result data paths.

### Always ask before using old data

If NetEase Cloud Music is already running before launch, the Skill will not silently reuse old output. It will ask whether the user wants to recollect after closing the client or use an existing output run.

Alternative considered: automatically use the newest old run. This was rejected because old data may be stale and should be an explicit user choice.

### Always list playlists before selection

The Skill will list user-created playlists and show them to the user before collecting, even when the user mentions a playlist name. The user must choose exactly one primary playlist.

Alternative considered: skip listing when a playlist name is known. This was rejected because visible playlist listing is the clearest confirmation of which account and playlist set are being collected.

### Slim result schemas

Primary playlist result JSONL/CSV will contain:

```text
order
title
artistNames
album
duration
durationMs
addedAt
```

Ranking result JSONL/CSV will contain:

```text
rank
title
artistNames
playCount
```

`artists` is removed because existing collected runs show it duplicates `artistNames` as an array form. `albumTransNames` and `trackTransNames` are removed because they are sparse cache-derived translation fields and add little to analysis. `cacheStatus` is removed from result files because it is a debugging signal, not a profile-analysis field.

Alternative considered: keep all v1 fields and rely on prompts to ignore noisy fields. This was rejected because repeated JSON keys and sparse fields consume attention and token budget.

### Derive durationMs from duration text

`durationMs` will be derived from visible `duration` text such as `03:58`. This keeps duration statistics available even when a song is missing from `playingList`.

Alternative considered: continue taking `durationMs` from `playingList`. This was rejected because `playingList` is supplemental and may miss songs that still have visible duration in the playlist.

### Keep special titles

The result shaping will not drop rows only because `title` or `album` appears visually empty or consists of special/invisible Unicode characters. These rows can represent intentional special songs and must remain in result files.

Alternative considered: filter visually empty titles as extraction noise. This was rejected because the current real dataset contains a meaningful special-title song.

### Result JSONL for AI/agent analysis, CSV for human preview

`result/*.jsonl` is the preferred source for AI/agent analysis because it preserves numeric types and is stable for programmatic preprocessing. `csv/*.csv` remains for human preview, manual checking, and cases where the user wants to paste tabular data into another tool.

Alternative considered: make CSV the default prompt input because it is smaller. This was rejected for the guided prompt because later agents may compute average duration, duration buckets, time distributions, and overlap statistics more reliably from JSONL.

### Per-attempt diagnostics log

Each collection attempt will create a timestamp run directory with `log/collection_diagnostics.json`. Successful runs also contain `raw/`, `result/`, and `csv/`. Failed attempts may contain only `log/`.

The diagnostics file will include:

- schema version and run metadata
- environment facts such as OS, CDP port, executable path if available, client version/build/patch if available, and CDP target URL type
- phase status for launch, CDP, playlist listing, primary playlist collection, playlist detail fetch, ranking collection, cache discovery, output writing, and validation
- quality counters such as result row counts, field completeness, and duration source
- failed phase, error code, error summary, and repair hints when a phase fails

Alternative considered: provide a separate manual `--diagnose` command only. This was rejected because users may not know to run diagnostics; every attempt should leave a repairable trace.

### Privacy-preserving diagnostics

`collection_diagnostics.json` will not record full DOM, HTML, raw row text, usernames, full playlist contents, or full song lists. Diagnostics record structure, counts, statuses, strategy names, and error summaries.

Alternative considered: write debug snapshots for easier repair. This was rejected because the Skill should protect user listening data by default and avoid creating sensitive artifacts.

### Repair the invoked Skill instance

Repair guidance will be relative to the current Skill root. If a project-local Skill is invoked, agents repair that project-local Skill. If a global Skill is invoked, agents repair that global Skill. Diagnostics must not hardcode any developer-local repository path as the repair root.

Alternative considered: always repair the project-local copy. This was rejected because the same Skill may later be installed or invoked globally.

## Risks / Trade-offs

- Result schema change breaks consumers expecting v1 fields → Mark the result field change as breaking and update tests, schemas, prompts, and CSV field documentation together.
- Failed attempts now create output directories → Document that timestamp directories can represent failed attempts and may contain only `log/`.
- Diagnostics may be too sparse for some future compatibility failures → Include phase-specific repair hints and function/file pointers while avoiding sensitive payloads.
- `duration` parsing may fail for unexpected formats → Preserve `duration` text, emit `durationMs=null` when parsing fails, and record duration parse completeness in diagnostics.
- Removing translation fields loses sparse human-readable translations → Accept because non-Chinese names are generally understandable to analysis models and translation fields are mostly empty.
- Self-repair can still fail → Agents should report the failed phase, attempted repair path, and remaining blocker to the user instead of inventing unsupported compatibility claims.
