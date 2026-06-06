## ADDED Requirements

### Requirement: Skill collects a single primary playlist
The Skill SHALL collect data for exactly one user-created NetEase Cloud Music playlist selected by the user.

#### Scenario: User selects one playlist
- **WHEN** the Skill lists user-created playlists and the user selects one playlist by name or number
- **THEN** the Skill proceeds with that playlist as the primary playlist

#### Scenario: User selects multiple playlists
- **WHEN** the user provides multiple playlist selections
- **THEN** the Skill rejects the selection and asks the user to choose exactly one primary playlist

### Requirement: Existing NetEase Cloud Music process blocks launch
The Skill SHALL check whether NetEase Cloud Music is already running before launching the client for CDP collection.

#### Scenario: NetEase Cloud Music is already running
- **WHEN** a NetEase Cloud Music process is detected before Skill launch
- **THEN** the Skill stops and tells the user to close NetEase Cloud Music manually

#### Scenario: NetEase Cloud Music is not running
- **WHEN** no NetEase Cloud Music process is detected
- **THEN** the Skill discovers the NetEase Cloud Music executable path before launching the client

### Requirement: Executable discovery requires a unique path
The Skill SHALL use a unique NetEase Cloud Music executable path before launching the client.

#### Scenario: One executable path is found
- **WHEN** executable discovery finds exactly one `cloudmusic.exe` candidate
- **THEN** the Skill uses that executable path

#### Scenario: No executable path is found
- **WHEN** executable discovery finds no `cloudmusic.exe` candidate
- **THEN** the Skill asks the user to provide the NetEase Cloud Music executable path

#### Scenario: Multiple executable paths are found
- **WHEN** executable discovery finds multiple `cloudmusic.exe` candidates
- **THEN** the Skill asks the user to choose which executable path to use

### Requirement: CDP uses fixed port 9222
The Skill SHALL use CDP port `9222` and SHALL NOT automatically choose another CDP port.

#### Scenario: Port 9222 is available
- **WHEN** port `9222` is available and the NetEase Cloud Music client is launched by the Skill
- **THEN** the Skill connects to the NetEase Cloud Music CDP target on port `9222`

#### Scenario: Port 9222 is occupied by another program
- **WHEN** port `9222` is occupied by a program that is not the Skill-launched NetEase Cloud Music CDP target
- **THEN** the Skill stops and tells the user that port `9222` is required and the occupying program should be closed

### Requirement: CDP provides visible playlist and ranking facts
The Skill SHALL use CDP page extraction as the source of visible playlist rows, playlist order, listening ranking rows, and ranking play counts.

#### Scenario: Primary playlist rows are collected
- **WHEN** the Skill opens the selected primary playlist through CDP
- **THEN** it collects visible playlist row fields including order, title, artists, artist text, album, and duration

#### Scenario: Listening rankings are collected
- **WHEN** the Skill opens the recent-week and all-time listening ranking views through CDP
- **THEN** it collects rank, title, artists, artist text, and numeric play count for each ranking row

### Requirement: Playlist detail fetch provides joined-at timestamps
The Skill SHALL fetch playlist detail from inside the NetEase Cloud Music CDP page context and use `trackIds[].at` as the `addedAt` source.

#### Scenario: Playlist detail fetch succeeds
- **WHEN** CDP page-context `fetch` returns playlist detail for the selected playlist
- **THEN** the Skill joins `trackIds[].at` to primary playlist rows by track ID and emits `addedAt`

#### Scenario: Playlist detail fetch fails
- **WHEN** CDP page-context `fetch` cannot return playlist detail for the selected playlist
- **THEN** the Skill fails clearly because `addedAt` is part of the result contract

### Requirement: PlayingList cache is supplemental
The Skill SHALL treat the local `playingList` cache as supplemental data and SHALL NOT use it as the source of playlist order or completeness.

#### Scenario: Cache row matches the playlist row
- **WHEN** a CDP playlist row can be matched to a `playingList` item by track ID
- **THEN** the Skill supplements the result with cache-derived fields and sets `cacheStatus` to `matched`

#### Scenario: Cache row is missing
- **WHEN** a CDP playlist row has no matching `playingList` item
- **THEN** the Skill still emits the result row and sets `cacheStatus` to `missing_from_playingList`

#### Scenario: Cache row title differs
- **WHEN** a CDP playlist row matches a `playingList` item by track ID but the cache title differs from the CDP title
- **THEN** the Skill emits the result row and sets `cacheStatus` to `cache_title_mismatch`

### Requirement: Run outputs use timestamp directory
The Skill SHALL write each successful run under `outputs/YYYYMMDD-HHMMSS/` inside the Skill install directory.

#### Scenario: Timestamp directory is new
- **WHEN** the timestamp output directory does not exist
- **THEN** the Skill writes the run outputs into that directory

#### Scenario: Timestamp directory already exists
- **WHEN** the timestamp output directory already exists
- **THEN** the Skill fails instead of adding a suffix or overwriting existing data

### Requirement: Run outputs contain exactly three data groups
The Skill SHALL write `raw`, `result`, and `csv` subdirectories for each successful run.

#### Scenario: Successful run completes
- **WHEN** primary playlist, recent-week ranking, and all-time ranking collection complete successfully
- **THEN** the run directory contains `raw/`, `result/`, and `csv/` subdirectories

### Requirement: Run outputs contain nine data files
The Skill SHALL write exactly one file per dataset in each data group for primary playlist, recent-week ranking, and all-time ranking.

#### Scenario: Successful run writes raw files
- **WHEN** a successful run completes
- **THEN** `raw/primary_playlist.jsonl`, `raw/ranking_recent_week.jsonl`, and `raw/ranking_all_time.jsonl` exist

#### Scenario: Successful run writes result files
- **WHEN** a successful run completes
- **THEN** `result/primary_playlist.jsonl`, `result/ranking_recent_week.jsonl`, and `result/ranking_all_time.jsonl` exist

#### Scenario: Successful run writes CSV files
- **WHEN** a successful run completes
- **THEN** `csv/primary_playlist.csv`, `csv/ranking_recent_week.csv`, and `csv/ranking_all_time.csv` exist

### Requirement: Primary playlist result schema is stable
The Skill SHALL emit primary playlist result JSONL and CSV with the same field set.

#### Scenario: Primary playlist result is written
- **WHEN** `result/primary_playlist.jsonl` and `csv/primary_playlist.csv` are written
- **THEN** each row contains `order`, `title`, `artists`, `artistNames`, `album`, `duration`, `addedAt`, `durationMs`, `albumTransNames`, `trackTransNames`, and `cacheStatus`

#### Scenario: AddedAt is missing
- **WHEN** `addedAt` is missing for a primary playlist row
- **THEN** JSONL writes `null` and CSV writes an empty value for `addedAt`

### Requirement: Ranking result schema is stable
The Skill SHALL emit recent-week and all-time ranking result JSONL and CSV with the same field set.

#### Scenario: Ranking result is written
- **WHEN** a ranking result JSONL file and its CSV counterpart are written
- **THEN** each row contains `rank`, `title`, `artists`, `artistNames`, and `playCount`

### Requirement: Raw files preserve source rows
The Skill SHALL write raw JSONL files that preserve the source data used to produce result rows.

#### Scenario: Primary playlist raw row is written
- **WHEN** a primary playlist raw row is written
- **THEN** it includes the CDP row, playlist detail row, optional `playingList` row, and `cacheStatus`

#### Scenario: Ranking raw row is written
- **WHEN** a ranking raw row is written
- **THEN** it includes the CDP ranking row for that rank

### Requirement: Analysis prompt remains in Skill instructions
The Skill SHALL keep the final LLM analysis prompt template in `SKILL.md` and SHALL NOT write an analysis prompt file during collection.

#### Scenario: Successful run completes
- **WHEN** the collector finishes writing data files
- **THEN** no `analysis_prompt.txt` file is written in the run output directory
