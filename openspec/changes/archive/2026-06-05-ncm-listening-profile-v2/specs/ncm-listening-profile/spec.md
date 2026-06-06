## ADDED Requirements

### Requirement: Skill Markdown is Chinese-first
The Skill SHALL use Chinese as the primary language for every Markdown file inside the Skill folder, while preserving commands, paths, field names, JSON keys, and code identifiers in English.

#### Scenario: Agent reads Skill instructions
- **WHEN** an agent opens `SKILL.md` or a Markdown reference file inside the Skill
- **THEN** the procedural instructions are primarily written in Chinese

#### Scenario: Agent copies technical literals
- **WHEN** a command, path, JSON key, or result field is documented
- **THEN** the literal technical text remains in English exactly as used by the scripts and output files

### Requirement: Skill remains collection-only
The Skill SHALL collect and prepare NetEase Cloud Music listening data, but SHALL NOT perform the final listening-profile/personality analysis inside the same Skill run.

#### Scenario: Collection succeeds
- **WHEN** the Skill finishes a collection run
- **THEN** it reports collection status, output paths, CSV field meanings, and reusable prompts without analyzing what kind of person the user is

#### Scenario: User asks for analysis during collection
- **WHEN** the user asks the Skill to analyze the collected data in the same session
- **THEN** the Skill tells the user to start a fresh analysis session with the provided prompt and result paths

### Requirement: Existing NetEase Cloud Music process requires a user choice
The Skill SHALL stop when NetEase Cloud Music is already running before Skill launch and SHALL ask the user whether to recollect or use an existing output run.

#### Scenario: User chooses recollect
- **WHEN** an existing `cloudmusic.exe` process is detected and the user chooses to recollect
- **THEN** the Skill asks the user to close NetEase Cloud Music manually before running collection again

#### Scenario: User chooses old data
- **WHEN** an existing `cloudmusic.exe` process is detected and the user chooses to use old data
- **THEN** the Skill does not launch or attach to the existing client and instead reports available prior output runs or asks the user which prior run to use

#### Scenario: No choice has been made
- **WHEN** an existing `cloudmusic.exe` process is detected and the user has not chosen recollect or old data
- **THEN** the Skill MUST NOT analyze existing outputs or start a new collection

### Requirement: Skill lists user-created playlists before collection
The Skill SHALL list user-created playlists and ask the user to choose exactly one primary playlist before collecting primary playlist data.

#### Scenario: Playlists are listed
- **WHEN** playlist listing succeeds
- **THEN** the Skill shows the user a numbered list of user-created playlists with enough identifying information to choose one

#### Scenario: User provides a known playlist name
- **WHEN** the user already mentions a playlist name
- **THEN** the Skill still lists user-created playlists and asks for explicit confirmation of exactly one primary playlist

#### Scenario: User selects multiple playlists
- **WHEN** the user selects more than one playlist
- **THEN** the Skill rejects the selection and asks the user to choose one and only one primary playlist

### Requirement: Result primary playlist schema is slim and analysis-ready
The Skill SHALL emit primary playlist result JSONL and CSV with only `order`, `title`, `artistNames`, `album`, `duration`, `durationMs`, and `addedAt`.

#### Scenario: Primary playlist result is written
- **WHEN** `result/primary_playlist.jsonl` and `csv/primary_playlist.csv` are written
- **THEN** each row contains `order`, `title`, `artistNames`, `album`, `duration`, `durationMs`, and `addedAt`

#### Scenario: Removed v1 fields are excluded
- **WHEN** primary playlist result rows are written
- **THEN** they do not contain `artists`, `albumTransNames`, `trackTransNames`, or `cacheStatus`

#### Scenario: AddedAt is missing
- **WHEN** `addedAt` is unavailable for a primary playlist row
- **THEN** JSONL writes `null` and CSV writes an empty value for `addedAt`

### Requirement: Result ranking schema is slim and analysis-ready
The Skill SHALL emit recent-week and all-time ranking result JSONL and CSV with only `rank`, `title`, `artistNames`, and `playCount`.

#### Scenario: Ranking result is written
- **WHEN** a ranking result JSONL file and its CSV counterpart are written
- **THEN** each row contains `rank`, `title`, `artistNames`, and `playCount`

#### Scenario: Removed v1 fields are excluded
- **WHEN** ranking result rows are written
- **THEN** they do not contain `artists`

### Requirement: DurationMs is derived from visible duration
The Skill SHALL derive result `durationMs` from the visible `duration` text when possible.

#### Scenario: Duration text is parseable
- **WHEN** a primary playlist row has a visible duration such as `03:58`
- **THEN** the result row emits the equivalent millisecond value in `durationMs`

#### Scenario: PlayingList cache row is missing
- **WHEN** a primary playlist row is missing from the local `playingList` cache but has parseable visible `duration`
- **THEN** the result row still emits `durationMs` derived from `duration`

#### Scenario: Duration text is not parseable
- **WHEN** a primary playlist row has an unsupported or missing duration format
- **THEN** the result row emits `durationMs=null` and diagnostics record the duration parse gap

### Requirement: Special song titles are preserved
The Skill SHALL preserve song rows whose titles or albums contain special or invisible Unicode characters.

#### Scenario: Title appears visually empty
- **WHEN** a collected song title contains special or invisible Unicode characters
- **THEN** the Skill writes the row to raw, result, and CSV outputs without dropping it as an empty-title row

### Requirement: Raw files preserve debugging data
The Skill SHALL keep source and debugging data in raw JSONL files instead of result files.

#### Scenario: Primary playlist raw row is written
- **WHEN** a primary playlist raw row is written
- **THEN** it includes the CDP row, playlist detail row, optional `playingList` row, and cache join status

#### Scenario: Ranking raw row is written
- **WHEN** a ranking raw row is written
- **THEN** it includes the CDP ranking row for that rank

#### Scenario: Cache status exists only in raw
- **WHEN** cache join status such as `matched` or `missing_from_playingList` is produced
- **THEN** the status is preserved in raw output and excluded from result files and final collection summaries

### Requirement: Output directories include data and diagnostics groups
The Skill SHALL write successful collection outputs under `outputs/YYYYMMDD-HHMMSS/` with `raw`, `result`, `csv`, and `log` subdirectories.

#### Scenario: Successful run completes
- **WHEN** primary playlist, recent-week ranking, and all-time ranking collection complete successfully
- **THEN** the run directory contains `raw/`, `result/`, `csv/`, and `log/`

#### Scenario: Successful run writes data files
- **WHEN** a successful run completes
- **THEN** it writes primary playlist, recent-week ranking, and all-time ranking files in each of `raw/`, `result/`, and `csv/`

#### Scenario: Successful run writes diagnostics
- **WHEN** a successful run completes
- **THEN** it writes `log/collection_diagnostics.json`

### Requirement: Failed attempts write diagnostics
The Skill SHALL write `log/collection_diagnostics.json` for failed collection attempts and MAY leave the failed timestamp directory without `raw`, `result`, or `csv`.

#### Scenario: Collection fails after run directory creation
- **WHEN** a collection attempt fails before data files can be completed
- **THEN** the attempt directory contains `log/collection_diagnostics.json`

#### Scenario: Failed attempt has no result files
- **WHEN** a collection attempt fails before result shaping
- **THEN** the attempt directory may contain only `log/collection_diagnostics.json`

### Requirement: Diagnostics are privacy-preserving and machine-readable
The Skill SHALL write diagnostics as structured JSON and SHALL NOT record full DOM, HTML, raw row text, usernames, full playlist contents, or full song lists in `collection_diagnostics.json`.

#### Scenario: Diagnostics are written
- **WHEN** `log/collection_diagnostics.json` is written
- **THEN** it is valid JSON with a schema version, run metadata, environment facts, phase statuses, quality counters, and repair hints when applicable

#### Scenario: Sensitive page data exists during collection
- **WHEN** the collector has access to DOM text, raw row text, usernames, playlists, or song lists
- **THEN** diagnostics record only structural counts, statuses, strategy names, and error summaries instead of sensitive content

### Requirement: Diagnostics identify failed phases
The Skill SHALL record enough phase information for an agent to locate collection or compatibility failures.

#### Scenario: Playlist listing fails
- **WHEN** user-created playlist extraction fails
- **THEN** diagnostics identify the playlist-listing phase, include an error code, include relevant selector or strategy names, and point to likely repair files or functions

#### Scenario: Ranking collection fails
- **WHEN** opening or extracting recent-week or all-time rankings fails
- **THEN** diagnostics identify the ranking phase, include an error code, include relevant selector or strategy names, and point to likely repair files or functions

#### Scenario: Output quality is suspicious
- **WHEN** result row counts, field completeness, or duration parsing are below expected thresholds
- **THEN** diagnostics record quality warnings without adding sensitive row contents

### Requirement: Agents use diagnostics for Skill-instance repair
The Skill SHALL instruct agents to use `collection_diagnostics.json` to repair compatibility in the Skill instance that was invoked before escalating to the user.

#### Scenario: Project-local Skill was invoked
- **WHEN** diagnostics point to repairable extraction or compatibility failure and the invoked Skill is project-local
- **THEN** the agent uses the project-local Skill directory as the repair root

#### Scenario: Global Skill was invoked
- **WHEN** diagnostics point to repairable extraction or compatibility failure and the invoked Skill is global
- **THEN** the agent uses the global Skill directory as the repair root

#### Scenario: Agent cannot repair reliably
- **WHEN** the agent cannot repair the failure from diagnostics and available context
- **THEN** the agent reports the failed phase, attempted repair path, and remaining blocker to the user instead of claiming unsupported compatibility

### Requirement: Analysis prompts are stored in Skill instructions
The Skill SHALL keep both reusable analysis prompts in `SKILL.md` and SHALL NOT write prompt files during collection.

#### Scenario: Collection succeeds
- **WHEN** the collector finishes writing outputs
- **THEN** no `analysis_prompt.txt` or other prompt file is written in the run output directory

#### Scenario: Minimal prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a minimal prompt that references `result/primary_playlist.jsonl`, `result/ranking_all_time.jsonl`, and `result/ranking_recent_week.jsonl`

#### Scenario: Guided prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a guided prompt that asks the model or agent to compute statistics from result JSONL before making profile inferences

### Requirement: Output usage and CSV fields are documented
The Skill SHALL document how to use `raw`, `result`, and `csv` outputs and SHALL explain CSV fields in `SKILL.md`.

#### Scenario: User wants to inspect files manually
- **WHEN** the user reads `SKILL.md`
- **THEN** it explains that `result/*.jsonl` is preferred for AI/agent analysis, `csv/*.csv` is for human preview and manual inspection, and `raw/*.jsonl` is for troubleshooting

#### Scenario: User reads primary playlist CSV
- **WHEN** the user reads the CSV field documentation
- **THEN** it explains `order`, `title`, `artistNames`, `album`, `duration`, `durationMs`, and `addedAt`

#### Scenario: User reads ranking CSV
- **WHEN** the user reads the CSV field documentation
- **THEN** it explains `rank`, `title`, `artistNames`, and `playCount`

### Requirement: V2 validation target is local NetEase Cloud Music 3.0.0 Beta
The Skill SHALL validate v2 against the current local NetEase Cloud Music desktop client version and SHALL NOT claim validation against other versions.

#### Scenario: Real-client validation is documented
- **WHEN** v2 validation is completed
- **THEN** the validation notes identify NetEase Cloud Music 3.0.0 Beta 64-bit, Build 201967, Patch dd70f35 as the verified client

#### Scenario: Other client versions are discussed
- **WHEN** newer or different NetEase Cloud Music versions are mentioned
- **THEN** the Skill treats them as unverified unless a future validation run proves support
