# ncm-listening-profile Specification

## Purpose
Define the current collection-only contract for the NetEase Cloud Music listening-profile Skill: collect one user-created playlist and listening rankings through CDP, write raw/result/csv/log outputs, and hand final profile analysis to a separate session.
## Requirements
### Requirement: Skill Markdown is Chinese-first
The Skill SHALL use Chinese as the primary language for every Markdown file inside the Skill folder, while preserving commands, paths, field names, JSON keys, and code identifiers in English.

#### Scenario: Agent reads Skill instructions
- **WHEN** an agent opens `SKILL.md` or a Markdown reference file inside the Skill
- **THEN** the procedural instructions are primarily written in Chinese

#### Scenario: Agent copies technical literals
- **WHEN** a command, path, JSON key, or result field is documented
- **THEN** the literal technical text remains in English exactly as used by the scripts and output files

### Requirement: Skill starts with a concise collection introduction
The Skill SHALL begin its first user-visible response with the agreed concise introduction before running commands or reporting environment state.

#### Scenario: Skill is invoked for collection
- **WHEN** the Skill is invoked to collect NetEase Cloud Music listening-profile data
- **THEN** the first user-visible response begins with `我会帮你采集供 AI 做听歌画像分析的数据：包括你创建的歌单列表、你确认的主歌单、最近一周和所有时间听歌排行，并整理成数据文件和分析 prompt；本轮先不直接做画像结论。`

#### Scenario: Later workflow steps continue
- **WHEN** the Skill later reports an existing process, port conflict, path ambiguity, playlist choice, or collection success
- **THEN** it does not repeat the Skill purpose introduction and proceeds with the relevant step-specific message

### Requirement: Python environment is checked before Skill operations
The Skill SHALL check the active Python runtime and required packages before collecting data, listing playlists, or reading existing runs.

#### Scenario: Any operation starts
- **WHEN** the Skill is about to collect data, list playlists, or list existing output runs
- **THEN** it first runs `scripts/collect_ncm_profile.py --check` with the active `Python 3.10+` interpreter from the Skill root

#### Scenario: Dependency check fails
- **WHEN** the dependency check reports missing Python packages
- **THEN** the Skill tells the user to install dependencies with the same active Python interpreter, using `python -m pip install -r scripts/requirements.txt` or `python3 -m pip install -r scripts/requirements.txt` as appropriate for the platform

#### Scenario: Python requirements are documented
- **WHEN** an agent reads `SKILL.md`
- **THEN** it documents that the scripts require `Python 3.10+`, `psutil`, `requests`, and `websocket-client`

### Requirement: Reference routing is stage-specific
The Skill SHALL document which reference file to read for each major workflow concern.

#### Scenario: Environment details are needed
- **WHEN** an agent needs rules for process detection, executable discovery, CDP port usage, or client launch
- **THEN** `SKILL.md` routes the agent to `references/environment.md`

#### Scenario: API details are needed
- **WHEN** an agent needs API paths, response shapes, user-created playlist filtering, or API failure rules
- **THEN** `SKILL.md` routes the agent to `references/api-patterns.md`

#### Scenario: Schema details are needed
- **WHEN** an agent changes result, raw, CSV, aggregate, output layout, or diagnostics fields
- **THEN** `SKILL.md` routes the agent to `references/schemas.md`

#### Scenario: Failure repair is needed
- **WHEN** a collection attempt fails or output quality is suspicious
- **THEN** `SKILL.md` routes the agent to `references/troubleshooting.md`

### Requirement: Skill remains collection-only
The Skill SHALL collect and prepare NetEase Cloud Music listening data, but SHALL NOT perform the final listening-profile/personality analysis inside the same Skill run.

#### Scenario: Collection succeeds
- **WHEN** the Skill finishes a collection run
- **THEN** it reports collection status, the single run directory, a concise folder-purpose summary, and reusable prompts without analyzing what kind of person the user is

#### Scenario: Successful output summarizes file groups
- **WHEN** the Skill reports final collection output
- **THEN** it explains that `aggregate/aggregate.json` is precomputed statistics and indexes, `result/*.jsonl` is the complete fact table for AI analysis, `csv/*.csv` is table preview for user inspection, `raw/*.jsonl` is troubleshooting source data, and `log/collection_diagnostics.json` is the collection diagnostics log

#### Scenario: Successful output avoids path clutter
- **WHEN** the Skill reports final collection output
- **THEN** it does not list every result, CSV, aggregate, or log file path separately before the prompts

#### Scenario: CSV field meanings are omitted from final response
- **WHEN** the Skill reports final collection output
- **THEN** it does not expand CSV field meanings and instead tells the user they can ask AI if any CSV field is unclear

#### Scenario: User asks for analysis during collection
- **WHEN** the user asks the Skill to analyze the collected data in the same session
- **THEN** the Skill tells the user to start a fresh analysis session with the provided prompt and result paths

### Requirement: Existing NetEase Cloud Music process requires a user choice
The Skill SHALL stop when a NetEase Cloud Music desktop client is already running before Skill launch and SHALL ask the user whether to recollect or use an existing output run.

#### Scenario: User chooses recollect
- **WHEN** an existing NetEase Cloud Music desktop client process is detected and the user chooses to recollect
- **THEN** the Skill asks the user to close NetEase Cloud Music manually before running collection again

#### Scenario: User chooses old data
- **WHEN** an existing NetEase Cloud Music desktop client process is detected and the user chooses to use old data
- **THEN** the Skill does not launch or attach to the existing client and instead reports available prior output runs or asks the user which prior run to use

#### Scenario: No choice has been made
- **WHEN** an existing NetEase Cloud Music desktop client process is detected and the user has not chosen recollect or old data
- **THEN** the Skill MUST NOT analyze existing outputs or start a new collection

#### Scenario: Windows client process is detected
- **WHEN** the Skill runs on Windows and detects `cloudmusic.exe`
- **THEN** it treats NetEase Cloud Music as already running and reports the detected PID and executable path when available

#### Scenario: macOS client process is detected
- **WHEN** the Skill runs on macOS and detects `NeteaseMusic` or `NeteaseMusic Helper`
- **THEN** it treats NetEase Cloud Music as already running and reports the detected PID and executable path when available

### Requirement: Existing output runs are selectable without client access
The Skill SHALL support using an existing output run without launching or attaching to NetEase Cloud Music.

#### Scenario: Existing runs are listed
- **WHEN** the user chooses to use old data
- **THEN** the Skill lists existing output runs with timestamp, success or failure shape, and available result or log paths

#### Scenario: Existing run is selected
- **WHEN** the user selects an existing output run
- **THEN** the Skill reports paths and reusable prompts without launching or attaching to NetEase Cloud Music

### Requirement: Executable discovery requires a unique path
The Skill SHALL use a unique NetEase Cloud Music desktop client path before launching the client.

#### Scenario: One Windows executable path is found
- **WHEN** the Skill runs on Windows and discovery finds exactly one `cloudmusic.exe` candidate
- **THEN** the Skill uses that executable path

#### Scenario: One macOS app path is found
- **WHEN** the Skill runs on macOS and discovery finds exactly one `NeteaseMusic.app` candidate
- **THEN** the Skill uses that app path

#### Scenario: Explicit client path is provided
- **WHEN** the user or agent provides `--client-path` or `NCM_CLIENT_PATH`
- **THEN** the Skill validates that path as the platform's NetEase Cloud Music desktop client path before launching

#### Scenario: No client path is found
- **WHEN** executable discovery finds no NetEase Cloud Music desktop client candidate
- **THEN** the Skill asks the user to provide the NetEase Cloud Music desktop client path with `--client-path`

#### Scenario: Multiple client paths are found
- **WHEN** executable discovery finds multiple NetEase Cloud Music desktop client candidates
- **THEN** the Skill asks the user to choose which client path to use and pass it with `--client-path`

### Requirement: CDP uses fixed port 9222
The Skill SHALL use CDP port `9222` and SHALL NOT automatically choose another CDP port.

#### Scenario: Port 9222 is available
- **WHEN** port `9222` is available and the NetEase Cloud Music client is launched by the Skill
- **THEN** the Skill connects to the NetEase Cloud Music CDP target on port `9222`

#### Scenario: Port 9222 is occupied by another program
- **WHEN** port `9222` is occupied by a program that is not the Skill-launched NetEase Cloud Music CDP target
- **THEN** the Skill stops and tells the user that port `9222` is required and the occupying program should be closed

### Requirement: Skill lists user-created playlists before collection
The Skill SHALL list user-created playlists through API and ask the user to choose exactly one primary playlist by public list number or playlist name before collecting primary playlist data.

#### Scenario: Public playlist list is shown
- **WHEN** playlist listing succeeds
- **THEN** the Skill shows the user a table with only `编号`, `歌单名`, and `曲数`

#### Scenario: Playlist choice introduction is shown
- **WHEN** playlist listing succeeds and the Skill asks the user to confirm a primary playlist
- **THEN** it uses the exact wording `下面是你创建的歌单。主歌单会作为这次画像数据的对照基准(只能选一个喔www)。你可以回复编号或歌单名。`

#### Scenario: Internal playlist fields exist
- **WHEN** playlist listing data contains `playlistId`, `playCount`, `specialType`, `privacy`, `updateTime`, or `source`
- **THEN** the Skill uses those fields only internally and MUST NOT show them in the user-facing playlist choice table

#### Scenario: User provides a known playlist name
- **WHEN** the user already mentions a playlist name
- **THEN** the Skill still lists user-created playlists and asks for explicit confirmation of exactly one primary playlist

#### Scenario: User selects one playlist by number
- **WHEN** the user selects one listed playlist by its public number
- **THEN** the Skill proceeds with that playlist as the primary playlist

#### Scenario: User selects one playlist by name
- **WHEN** the user selects one playlist by an exact or unambiguous name match
- **THEN** the Skill proceeds with that playlist as the primary playlist

#### Scenario: User attempts to select by playlistId
- **WHEN** the user tries to select a playlist by `playlistId` instead of public number or name
- **THEN** the Skill asks the user to choose by `编号` or `歌单名`

#### Scenario: User selects multiple playlists
- **WHEN** the user selects more than one playlist
- **THEN** the Skill rejects the selection and asks the user to choose one and only one primary playlist

### Requirement: Run outputs use timestamp directory
The Skill SHALL write each collection attempt under `outputs/YYYYMMDD-HHMMSS/` inside the Skill install directory.

#### Scenario: Timestamp directory is new
- **WHEN** the timestamp output directory does not exist
- **THEN** the Skill writes the run outputs into that directory

#### Scenario: Timestamp directory already exists
- **WHEN** the timestamp output directory already exists
- **THEN** the Skill fails instead of adding a suffix or overwriting existing data

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

### Requirement: Special song titles are preserved
The Skill SHALL preserve song rows whose titles or albums contain special or invisible Unicode characters.

#### Scenario: Title appears visually empty
- **WHEN** a collected song title contains special or invisible Unicode characters
- **THEN** the Skill writes the row to raw, result, and CSV outputs without dropping it as an empty-title row

### Requirement: Raw files preserve debugging data
The Skill SHALL keep source and debugging data in raw JSONL files instead of result files, while storing only the agreed raw API fields.

#### Scenario: Primary playlist raw row is written
- **WHEN** a primary playlist raw row is written
- **THEN** it includes source `api`, order, track identity, track fields, artist fields, album fields, duration fields, and joined-at source fields needed to explain result shaping

#### Scenario: Ranking raw row is written
- **WHEN** a ranking raw row is written
- **THEN** it includes source `api`, rank, play count, optional API score, and song, artist, album, and duration fields needed to explain result shaping

#### Scenario: Forbidden raw fields exist in API response
- **WHEN** API responses contain `creator`, `subscribers`, `privileges`, `coverImgUrl`, `recommendInfo`, complete response payloads, cookies, tokens, headers, or request bodies
- **THEN** those values are excluded from raw outputs

#### Scenario: User playlist list is fetched
- **WHEN** the Skill fetches playlists for user selection
- **THEN** it does not write a `raw/user_playlists.jsonl` file or any other raw copy of the playlist list

### Requirement: Output directories include data and diagnostics groups
The Skill SHALL write successful collection outputs under `outputs/YYYYMMDD-HHMMSS/` with `raw`, `result`, `csv`, `aggregate`, and `log` subdirectories.

#### Scenario: Successful run creates output groups
- **WHEN** primary playlist, recent-week ranking, and all-time ranking collection complete successfully
- **THEN** the run directory contains `raw/`, `result/`, `csv/`, `aggregate/`, and `log/`

#### Scenario: Successful run writes raw files
- **WHEN** a successful run completes
- **THEN** `raw/primary_playlist.jsonl`, `raw/ranking_recent_week.jsonl`, and `raw/ranking_all_time.jsonl` exist

#### Scenario: Successful run writes result files
- **WHEN** a successful run completes
- **THEN** `result/primary_playlist.jsonl`, `result/ranking_recent_week.jsonl`, and `result/ranking_all_time.jsonl` exist

#### Scenario: Successful run writes CSV files
- **WHEN** a successful run completes
- **THEN** `csv/primary_playlist.csv`, `csv/ranking_recent_week.csv`, and `csv/ranking_all_time.csv` exist

#### Scenario: Successful run writes aggregate
- **WHEN** a successful run completes
- **THEN** `aggregate/aggregate.json` exists

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
The Skill SHALL write diagnostics as structured JSON and SHALL NOT record full API responses, full playlist contents, full song lists, DOM, HTML, usernames, cookies, tokens, headers, or request bodies in `collection_diagnostics.json`.

#### Scenario: Diagnostics are written
- **WHEN** `log/collection_diagnostics.json` is written
- **THEN** it is valid JSON with a schema version, run metadata, environment facts, API phase statuses, quality counters, and repair hints when applicable

#### Scenario: Sensitive page or API data exists during collection
- **WHEN** the collector has access to API responses, DOM text, usernames, playlists, song lists, credentials, or request metadata
- **THEN** diagnostics record only paths, statuses, response shapes, counts, field completeness, and error summaries instead of sensitive payloads

### Requirement: Diagnostics identify failed phases
The Skill SHALL record enough phase information for an agent to locate API collection, output, aggregate, or compatibility failures.

#### Scenario: Current user API fails
- **WHEN** current user extraction fails
- **THEN** diagnostics identify the current-user API phase and include an error code, sanitized error summary, and likely repair files or functions

#### Scenario: Playlist listing API fails
- **WHEN** user-created playlist API extraction fails
- **THEN** diagnostics identify the playlist-listing API phase and include the API path, status when available, response shape when available, and likely repair files or functions

#### Scenario: Primary playlist API fails
- **WHEN** primary playlist API collection fails
- **THEN** diagnostics identify the primary playlist API phase and include the API path, status when available, response shape when available, and likely repair files or functions

#### Scenario: Ranking API fails
- **WHEN** recent-week or all-time ranking API collection fails
- **THEN** diagnostics identify the ranking API phase and include the API path, status when available, response shape when available, and likely repair files or functions

#### Scenario: Aggregate output fails
- **WHEN** aggregate calculation or writing fails
- **THEN** diagnostics identify the aggregate phase and include a sanitized error summary and repair hints

### Requirement: Agents use diagnostics for Skill-instance repair
The Skill SHALL instruct agents to use `collection_diagnostics.json` to repair API compatibility, shaping, aggregate, or output failures in the Skill instance that was invoked before escalating to the user.

#### Scenario: Project-local Skill was invoked
- **WHEN** diagnostics point to repairable API, shaping, aggregate, or output failure and the invoked Skill is project-local
- **THEN** the agent uses the project-local Skill directory as the repair root

#### Scenario: Global Skill was invoked
- **WHEN** diagnostics point to repairable API, shaping, aggregate, or output failure and the invoked Skill is global
- **THEN** the agent uses the global Skill directory as the repair root

#### Scenario: Agent cannot repair reliably
- **WHEN** the agent cannot repair the failure from diagnostics and available context
- **THEN** the agent reports the failed phase, attempted repair path, and remaining blocker to the user instead of claiming unsupported compatibility

### Requirement: Analysis prompts are stored in Skill instructions
The Skill SHALL keep both reusable analysis prompts and their user-facing suitability descriptions in `SKILL.md` and SHALL NOT write prompt files during collection.

#### Scenario: Collection succeeds
- **WHEN** the collector finishes writing outputs
- **THEN** no `analysis_prompt.txt` or other prompt file is written in the run output directory

#### Scenario: Minimal prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a minimal prompt that references `result/primary_playlist.jsonl`, `result/ranking_all_time.jsonl`, `result/ranking_recent_week.jsonl`, and then `aggregate/aggregate.json` in that order
- **AND** the `aggregate/aggregate.json` line says it is computed from the preceding data as precomputed statistics and indexes for locating trends, extremes, overlaps, and samples, while complete facts remain in the three result files

#### Scenario: Minimal prompt suitability is shown
- **WHEN** the minimal prompt is shown
- **THEN** it is followed by the exact suitability text `适合已经很熟悉和 AI 对话的人，也适合你想保留一点未知感和神秘感的时候。它不给AI太多方向，只把数据交出去，让对方自己靠近、观察和理解你。适合期待更自由、更意外、更像一次重新相识的分析。`

#### Scenario: Guided prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a guided prompt that references `result/primary_playlist.jsonl`, `result/ranking_all_time.jsonl`, `result/ranking_recent_week.jsonl`, and then `aggregate/aggregate.json` in that order
- **AND** the `aggregate/aggregate.json` line says it is computed from the preceding data as precomputed statistics and indexes for locating trends, extremes, overlaps, and samples, while complete facts remain in the three result files
- **AND** it asks AI to use long-term preference, recent state, aesthetic imagery, life rhythm, and small anomalies to build an evidenced, detailed, and warm profile

#### Scenario: Guided prompt suitability is shown
- **WHEN** the guided prompt is shown
- **THEN** it is followed by the exact suitability text `适合你希望被认真看见的时候。它会引导AI慢下来，从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解你，而不是只给出一份音乐品味总结。适合想要更稳定、更细腻、更有温度回答的场景。`

### Requirement: Output usage and CSV fields are documented
The Skill SHALL document how to use `raw`, `result`, `csv`, and `aggregate` outputs and SHALL explain CSV fields and aggregate boundaries in `SKILL.md`.

#### Scenario: User wants to inspect files manually
- **WHEN** the user reads `SKILL.md`
- **THEN** it explains that `result/*.jsonl` is the complete fact source for AI/agent analysis, `aggregate/aggregate.json` is precomputed statistics and neutral indexes, `csv/*.csv` is for human preview and manual inspection, and `raw/*.jsonl` is for troubleshooting

#### Scenario: User reads aggregate documentation
- **WHEN** the user reads `SKILL.md`
- **THEN** it explains that aggregate fields with top, bottom, earliest, latest, overlap, or sample wording are truncated indexes named by their count and ordering rule, not analysis conclusions or complete facts

#### Scenario: User reads primary playlist CSV
- **WHEN** the user reads the CSV field documentation
- **THEN** it explains `order`, `title`, `artistNames`, `album`, `duration`, `durationMs`, and `addedAt`

#### Scenario: User reads ranking CSV
- **WHEN** the user reads the CSV field documentation
- **THEN** it explains `rank`, `title`, `artistNames`, and `playCount`

### Requirement: API-only collection uses page-context fetch
The Skill SHALL collect NetEase Cloud Music business data only through `fetch` calls executed inside the authenticated NetEase Cloud Music CDP page context.

#### Scenario: Business API is requested
- **WHEN** the Skill needs current user, playlist, primary playlist, or listening ranking data
- **THEN** it executes the request in the client page context with `credentials: "include"`

#### Scenario: Python runtime handles collection
- **WHEN** the Python process runs the collector
- **THEN** it connects to local CDP endpoints only and MUST NOT directly request NetEase Cloud Music business API endpoints

#### Scenario: API collection fails
- **WHEN** an allowed API request fails, returns an unsafe status, cannot parse JSON, or lacks required fields
- **THEN** the Skill writes diagnostics and fails the collection attempt without using DOM fallback

### Requirement: Current user is identified through API
The Skill SHALL identify the current authenticated user through the page-context `/api/nuser/account/get` API before listing playlists or collecting listening records.

#### Scenario: Current user API succeeds
- **WHEN** `/api/nuser/account/get` returns `code=200` with `profile.userId`
- **THEN** the Skill uses that user ID for playlist listing and listening record requests

#### Scenario: Current user API fails
- **WHEN** the current user API cannot provide a user ID
- **THEN** the Skill fails clearly and records the current-user phase in diagnostics

### Requirement: API lists user-created playlists before collection
The Skill SHALL list user-created playlists through `/api/user/playlist`, expose only public selection fields for user choice, and resolve the internal `playlistId` only after a public number or name is selected.

#### Scenario: User-created playlists are listed
- **WHEN** `/api/user/playlist` returns playlists for the current user
- **THEN** the Skill lists playlists where `userId` equals the current user ID and `subscribed` is `false`

#### Scenario: Special playlist types exist
- **WHEN** user-created playlists include nonzero `specialType` values
- **THEN** the Skill still lists them for user choice instead of filtering by `specialType`

#### Scenario: User selects one playlist by public selector
- **WHEN** the user selects one listed playlist by public number or exact or unambiguous name
- **THEN** the Skill proceeds with that playlist as the primary playlist

#### Scenario: User attempts to select by playlistId
- **WHEN** the user tries to select a playlist by `playlistId`
- **THEN** the Skill asks the user to choose by public number or playlist name

#### Scenario: User selects multiple playlists
- **WHEN** the user selects more than one playlist
- **THEN** the Skill rejects the selection and asks the user to choose one and only one primary playlist

### Requirement: API playlist detail provides primary playlist facts
The Skill SHALL use `/api/v6/playlist/detail` as the source of primary playlist order, title, artist names, album, duration, and joined-at timestamps.

#### Scenario: Primary playlist API succeeds
- **WHEN** playlist detail returns `playlist.tracks[]` and `playlist.trackIds[]`
- **THEN** the Skill emits primary playlist result rows from those API arrays

#### Scenario: Joined-at timestamp exists
- **WHEN** `playlist.trackIds[].at` is present for a primary playlist item
- **THEN** the Skill emits the corresponding `addedAt` value

#### Scenario: Primary playlist API shape is invalid
- **WHEN** playlist detail lacks required arrays or required track fields
- **THEN** the Skill fails the primary playlist phase and writes diagnostics

### Requirement: API listening records provide ranking facts
The Skill SHALL use `/api/v1/play/record` as the source of recent-week and all-time listening ranking rows, and SHALL treat an empty recent-week ranking as a valid no-recent-listening state.

#### Scenario: Recent-week ranking API succeeds
- **WHEN** `/api/v1/play/record?type=1` returns non-empty `weekData[]`
- **THEN** the Skill emits `ranking_recent_week` result rows from that array

#### Scenario: Recent-week ranking is empty
- **WHEN** `/api/v1/play/record?type=1` returns `weekData=[]`
- **THEN** the Skill treats the recent-week ranking as a successful dataset with 0 rows
- **AND** it continues collecting all-time ranking, shaping outputs, building aggregate, and writing the run
- **AND** diagnostics record `recentWeekRows=0`

#### Scenario: All-time ranking API succeeds
- **WHEN** `/api/v1/play/record?type=0` returns non-empty `allData[]`
- **THEN** the Skill emits `ranking_all_time` result rows from that array

#### Scenario: All-time ranking is empty
- **WHEN** `/api/v1/play/record?type=0` returns `allData=[]`
- **THEN** the Skill fails the all-time ranking phase and writes diagnostics

#### Scenario: Ranking API shape is invalid
- **WHEN** a listening record response lacks the required ranking array or required song fields
- **THEN** the Skill fails the corresponding ranking phase and writes diagnostics

### Requirement: DurationMs is derived from API duration
The Skill SHALL derive primary playlist `durationMs` from the API song duration field and derive human-readable `duration` from that millisecond value.

#### Scenario: API duration exists
- **WHEN** a primary playlist API track has a positive millisecond duration
- **THEN** the result row emits that value in `durationMs` and a formatted `duration`

#### Scenario: API duration is missing
- **WHEN** a primary playlist API track lacks a usable duration
- **THEN** the Skill treats the primary playlist API shape as invalid and fails the collection attempt

### Requirement: Aggregate output provides precomputed neutral indexes
The Skill SHALL write `aggregate/aggregate.json` for successful runs with precomputed statistics and neutral indexes only.

#### Scenario: Successful run writes aggregate
- **WHEN** primary playlist, recent-week ranking, and all-time ranking collection complete successfully
- **THEN** the run directory contains `aggregate/aggregate.json`

#### Scenario: Aggregate is generated
- **WHEN** `aggregate/aggregate.json` is written
- **THEN** it contains computed statistics, distributions, overlaps, and named indexes without profile-analysis conclusions or evidence-strength labels

#### Scenario: Aggregate contains truncated indexes
- **WHEN** aggregate fields contain top, bottom, earliest, latest, or overlap slices
- **THEN** field names include the count and ordering rule, such as `top30ArtistsByPrimaryTrackCount`

#### Scenario: Full facts are needed
- **WHEN** complete row-level facts are needed
- **THEN** `result/*.jsonl` remains the complete analysis fact source instead of `aggregate/aggregate.json`

### Requirement: Aggregate calculation covers agreed metrics
The Skill SHALL compute the agreed v5 aggregate metric groups from result data and required raw identifiers.

#### Scenario: Counts are computed
- **WHEN** aggregate is built
- **THEN** it records source file paths and row counts for primary playlist, recent-week ranking, and all-time ranking

#### Scenario: Duration metrics are computed
- **WHEN** aggregate is built
- **THEN** it records average, median, minimum, maximum, short/medium/long buckets, longest tracks, and shortest tracks for the primary playlist

#### Scenario: Added-at metrics are computed
- **WHEN** aggregate is built
- **THEN** it records earliest/latest added time, year, year-month, month, hour, weekday distributions, and earliest/latest added track indexes

#### Scenario: Ranking metrics are computed
- **WHEN** aggregate is built
- **THEN** it records total play counts, Top1/Top3/Top10 play-count shares, and top/bottom track indexes for recent-week and all-time rankings

#### Scenario: Overlap metrics are computed
- **WHEN** aggregate is built
- **THEN** it records pairwise and three-way overlap counts plus named overlap and only-in indexes

#### Scenario: Artist and album metrics are computed
- **WHEN** aggregate is built
- **THEN** it records top artist and album indexes by primary count and ranking play count plus singleton counts and samples

#### Scenario: Text metrics are computed
- **WHEN** aggregate is built
- **THEN** it records title, album, and artist term frequencies plus title and album character-type statistics

#### Scenario: Recent-long-term shift metrics are computed
- **WHEN** aggregate is built
- **THEN** it records `recentLongTermShiftStats.recentWeekTop20TracksInAllTimeTop100Count`
- **AND** it records `recentLongTermShiftStats.recentWeekTop20TracksInAllTimeTop100Share`
- **AND** it records `recentLongTermShiftStats.allTimeTop20TracksInRecentWeekTop100Count`
- **AND** it records `recentLongTermShiftStats.allTimeTop20TracksInRecentWeekTop100Share`
- **AND** it records `recentLongTermShiftStats.recentWeekAllTimeOverlapMedianAbsoluteRankDelta`
- **AND** it records `recentLongTermShiftStats.top10RecentWeekAllTimeOverlapByRankRise`
- **AND** it records `recentLongTermShiftStats.top10RecentWeekAllTimeOverlapByRankDrop`

#### Scenario: Recent-week ranking is empty during aggregate
- **WHEN** aggregate is built with 0 recent-week ranking rows and non-empty all-time ranking rows
- **THEN** `rankingStats.recentWeekTotalPlayCount` is `0`
- **AND** `rankingStats.recentWeekTop1PlayCountShare`, `rankingStats.recentWeekTop3PlayCountShare`, and `rankingStats.recentWeekTop10PlayCountShare` are `0`
- **AND** `recentLongTermShiftStats.recentWeekTop20TracksInAllTimeTop100Count` is `0`
- **AND** `recentLongTermShiftStats.recentWeekTop20TracksInAllTimeTop100Share` is `0`
- **AND** `recentLongTermShiftStats.allTimeTop20TracksInRecentWeekTop100Count` is `0`
- **AND** `recentLongTermShiftStats.allTimeTop20TracksInRecentWeekTop100Share` is `0`
- **AND** `recentLongTermShiftStats.recentWeekAllTimeOverlapMedianAbsoluteRankDelta` is `null`
- **AND** the recent-week Top/Bottom indexes and rank-rise/rank-drop indexes are empty arrays

#### Scenario: Rank shift samples are shaped
- **WHEN** `top10RecentWeekAllTimeOverlapByRankRise` or `top10RecentWeekAllTimeOverlapByRankDrop` is written
- **THEN** each sample row includes `title`, `artistNames`, `recentWeekRank`, `allTimeRank`, `rankDelta`, `recentWeekPlayCount`, and `allTimePlayCount`
- **AND** `rankDelta` for rank-rise rows is `allTimeRank - recentWeekRank`
- **AND** `rankDelta` for rank-drop rows is `recentWeekRank - allTimeRank`

### Requirement: README opens with concrete user-owned framing
The Skill SHALL open `README.md` with user-facing copy that describes the NetEase Cloud Music listening traces, the concrete data collected, the local outputs, the reusable AI prompt, and the user's control over interpretation and sharing.

#### Scenario: User reads README opening
- **WHEN** a user opens `README.md`
- **THEN** the opening copy includes the exact text `你的网易云里藏着一份很长的自我备忘录：主歌单里留下的歌，最近一周反复回来的歌，所有时间里一直没有退场的歌。`
- **AND** it explains that `ncm-listening-profile` collects the confirmed primary playlist, recent-week listening ranking, and all-time listening ranking
- **AND** it explains that the Skill generates local data files and a copyable AI analysis prompt
- **AND** it includes the exact text `它把材料放到你手里，也把解释权留给你。最终要不要分析、交给谁分析、分享哪些文件，都由你决定。`

### Requirement: Desktop client support covers Windows and macOS
The Skill SHALL support local NetEase Cloud Music desktop client collection on Windows and macOS by launching the platform-native client with CDP port `9222`.

#### Scenario: Windows desktop client is supported
- **WHEN** the Skill runs on Windows and finds a unique NetEase Cloud Music desktop executable
- **THEN** it launches that `cloudmusic.exe` with `--force-renderer-accessibility=complete` and `--remote-debugging-port=9222`

#### Scenario: macOS desktop client is supported
- **WHEN** the Skill runs on macOS and finds a unique `NeteaseMusic.app`
- **THEN** it launches that app with `open -na <NeteaseMusic.app> --args --force-renderer-accessibility=complete --remote-debugging-port=9222`

#### Scenario: Unsupported platform is used
- **WHEN** the Skill runs on a platform other than Windows or macOS
- **THEN** it fails before client launch with a clear unsupported-platform message

#### Scenario: Shared API collection is used after launch
- **WHEN** either Windows or macOS client launch exposes CDP on `127.0.0.1:9222`
- **THEN** the Skill uses the same CDP target selection, page-context API fetches, result shaping, aggregate generation, and output writing behavior

### Requirement: Verified environments are documented
The Skill SHALL document verified environments as a matrix of real collection successes instead of treating one client version as the only supported environment.

#### Scenario: Windows verified environments are documented
- **WHEN** a user reads the Skill or README environment section
- **THEN** it states that Windows has been verified on Windows 10 with `NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35`, and on higher Windows systems with newer NetEase Cloud Music desktop clients through real collection runs

#### Scenario: macOS verified environment is documented
- **WHEN** a user reads the Skill or README environment section
- **THEN** it states that macOS has been verified on `macOS 26.3.1 arm64` with `NeteaseMusicDesktop/3.1.7.3283` through a real collection run

#### Scenario: Compatibility explanation is documented
- **WHEN** a user reads environment or troubleshooting documentation
- **THEN** it explains that data compatibility primarily depends on the NetEase server API response shape, while operating system and client versions mainly affect client launch, CDP exposure, login state, and page-context execution

