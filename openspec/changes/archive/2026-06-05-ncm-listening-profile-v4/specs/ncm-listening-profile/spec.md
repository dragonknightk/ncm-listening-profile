## ADDED Requirements

### Requirement: Skill starts with a concise collection introduction
The Skill SHALL begin its first user-visible response with the agreed concise introduction before running commands or reporting environment state.

#### Scenario: Skill is invoked for collection
- **WHEN** the Skill is invoked to collect NetEase Cloud Music listening-profile data
- **THEN** the first user-visible response begins with `我会帮你采集供 AI 做听歌画像分析的数据：包括你创建的歌单列表、你确认的主歌单、最近一周和所有时间听歌排行，并整理成数据文件和分析 prompt；本轮先不直接做画像结论。`

#### Scenario: Later workflow steps continue
- **WHEN** the Skill later reports an existing process, port conflict, path ambiguity, playlist choice, or collection success
- **THEN** it does not repeat the Skill purpose introduction and proceeds with the relevant step-specific message

### Requirement: Python environment is checked before Skill operations
The Skill SHALL check the Python runtime and required packages before collecting data, listing playlists, or reading existing runs.

#### Scenario: Any operation starts
- **WHEN** the Skill is about to collect data, list playlists, or list existing output runs
- **THEN** it first runs `python scripts/collect_ncm_profile.py --check` from the Skill root

#### Scenario: Dependency check fails
- **WHEN** the dependency check reports missing Python packages
- **THEN** the Skill tells the user to run `python -m pip install -r scripts/requirements.txt` before continuing

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

## MODIFIED Requirements

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

### Requirement: Analysis prompts are stored in Skill instructions
The Skill SHALL keep both reusable analysis prompts and their user-facing suitability descriptions in `SKILL.md` and SHALL NOT write prompt files during collection.

#### Scenario: Collection succeeds
- **WHEN** the collector finishes writing outputs
- **THEN** no `analysis_prompt.txt` or other prompt file is written in the run output directory

#### Scenario: Minimal prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a minimal prompt that references `aggregate/aggregate.json`, `result/primary_playlist.jsonl`, `result/ranking_all_time.jsonl`, and `result/ranking_recent_week.jsonl`

#### Scenario: Minimal prompt suitability is shown
- **WHEN** the minimal prompt is shown
- **THEN** it is followed by the exact suitability text `适合已经很熟悉和 AI 对话的人，也适合你想保留一点未知感和神秘感的时候。它不给AI太多方向，只把数据交出去，让对方自己靠近、观察和理解你。适合期待更自由、更意外、更像一次重新相识的分析。`

#### Scenario: Guided prompt is shown
- **WHEN** the Skill reports final collection output
- **THEN** it includes a guided prompt that asks AI to use long-term preference, recent state, aesthetic imagery, life rhythm, and small anomalies to build an evidenced, detailed, and warm profile

#### Scenario: Guided prompt suitability is shown
- **WHEN** the guided prompt is shown
- **THEN** it is followed by the exact suitability text `适合你希望被认真看见的时候。它会引导AI慢下来，从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解你，而不是只给出一份音乐品味总结。适合想要更稳定、更细腻、更有温度回答的场景。`

## REMOVED Requirements

### Requirement: Playlist ID is a user-facing selection interface
**Reason**: `playlistId` is an internal platform identifier that adds decision noise and has already caused user-facing output to expose implementation details.
**Migration**: Use `--playlist-index` for public numbered selection and keep `--playlist-name` for explicit name matching. The collector may still resolve the internal API ID after the public selection is made.
