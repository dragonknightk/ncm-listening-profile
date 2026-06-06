## ADDED Requirements

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
The Skill SHALL list user-created playlists through `/api/user/playlist` and ask the user to choose exactly one primary playlist before collecting primary playlist data.

#### Scenario: User-created playlists are listed
- **WHEN** `/api/user/playlist` returns playlists for the current user
- **THEN** the Skill lists playlists where `userId` equals the current user ID and `subscribed` is `false`

#### Scenario: Special playlist types exist
- **WHEN** user-created playlists include nonzero `specialType` values
- **THEN** the Skill still lists them for user choice instead of filtering by `specialType`

#### Scenario: User selects one playlist
- **WHEN** the user selects one listed playlist by number, name, or ID
- **THEN** the Skill proceeds with that playlist as the primary playlist

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
The Skill SHALL use `/api/v1/play/record` as the source of recent-week and all-time listening ranking rows.

#### Scenario: Recent-week ranking API succeeds
- **WHEN** `/api/v1/play/record?type=1` returns `weekData[]`
- **THEN** the Skill emits `ranking_recent_week` result rows from that array

#### Scenario: All-time ranking API succeeds
- **WHEN** `/api/v1/play/record?type=0` returns `allData[]`
- **THEN** the Skill emits `ranking_all_time` result rows from that array

#### Scenario: Ranking API shape is invalid
- **WHEN** a listening record response lacks required ranking data or required song fields
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
The Skill SHALL compute the agreed v3 aggregate metric groups from result data and required raw identifiers.

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

## MODIFIED Requirements

### Requirement: Skill lists user-created playlists before collection
The Skill SHALL list user-created playlists through API and ask the user to choose exactly one primary playlist before collecting primary playlist data.

#### Scenario: Playlists are listed
- **WHEN** playlist listing succeeds
- **THEN** the Skill shows the user a numbered list of user-created playlists with enough identifying information to choose one

#### Scenario: User provides a known playlist name
- **WHEN** the user already mentions a playlist name
- **THEN** the Skill still lists user-created playlists and asks for explicit confirmation of exactly one primary playlist

#### Scenario: User selects one playlist
- **WHEN** the user selects one playlist by name, number, or ID
- **THEN** the Skill proceeds with that playlist as the primary playlist

#### Scenario: User selects multiple playlists
- **WHEN** the user selects more than one playlist
- **THEN** the Skill rejects the selection and asks the user to choose one and only one primary playlist

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
The Skill SHALL keep both reusable analysis prompts and their short user-facing suitability descriptions in `SKILL.md` and SHALL NOT write prompt files during collection.

#### Scenario: Collection succeeds
- **WHEN** the collector finishes writing outputs
- **THEN** no `analysis_prompt.txt` or other prompt file is written in the run output directory

#### Scenario: Minimal prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a minimal prompt that references `aggregate/aggregate.json`, `result/primary_playlist.jsonl`, `result/ranking_all_time.jsonl`, and `result/ranking_recent_week.jsonl`

#### Scenario: Minimal prompt suitability is shown
- **WHEN** the minimal prompt is shown
- **THEN** it is followed by the agreed suitability text about being familiar with AI conversation, preserving unknownness and mystery, and allowing AI to approach the data freely

#### Scenario: Guided prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a guided prompt that warmly invites AI to use the music data to build an evidenced, detailed, and emotionally warm profile

#### Scenario: Guided prompt suitability is shown
- **WHEN** the guided prompt is shown
- **THEN** it is followed by the agreed suitability text about being seriously seen, slowing down, and understanding long-term preference, recent state, aesthetic imagery, life rhythm, and small anomalies

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

## REMOVED Requirements

### Requirement: CDP provides visible playlist and ranking facts
**Reason**: v3 replaces DOM-visible playlist and ranking extraction with API-only collection.
**Migration**: Use page-context `/api/v6/playlist/detail` for primary playlist facts and `/api/v1/play/record` for ranking facts.

### Requirement: Playlist detail fetch provides joined-at timestamps
**Reason**: playlist detail is no longer a supplemental joined-at fetch; it is the primary source for the whole primary playlist.
**Migration**: Use the new API playlist detail requirement, which covers both `playlist.tracks[]` facts and `playlist.trackIds[].at`.

### Requirement: PlayingList cache is supplemental debugging data
**Reason**: v3 API-only collection no longer uses local `playingList` cache for shaping, debugging, or result completeness.
**Migration**: Use API raw rows and diagnostics for source tracing and troubleshooting.

### Requirement: DurationMs is derived from visible duration
**Reason**: v3 no longer extracts visible DOM duration text.
**Migration**: Use API millisecond duration and format `duration` from `durationMs`.

### Requirement: V2 validation target is local NetEase Cloud Music 3.0.0 Beta
**Reason**: v3 changes the collection contract and requires new validation notes.
**Migration**: Document v3 validation against the local client version after API-only implementation is verified.
