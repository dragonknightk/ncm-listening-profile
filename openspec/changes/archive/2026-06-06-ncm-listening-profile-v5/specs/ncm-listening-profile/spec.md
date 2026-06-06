## ADDED Requirements

### Requirement: README opens with concrete user-owned framing
The Skill SHALL open `README.md` with user-facing copy that describes the NetEase Cloud Music listening traces, the concrete data collected, the local outputs, the reusable AI prompt, and the user's control over interpretation and sharing.

#### Scenario: User reads README opening
- **WHEN** a user opens `README.md`
- **THEN** the opening copy includes the exact text `你的网易云里藏着一份很长的自我备忘录：主歌单里留下的歌，最近一周反复回来的歌，所有时间里一直没有退场的歌。`
- **AND** it explains that `ncm-listening-profile` collects the confirmed primary playlist, recent-week listening ranking, and all-time listening ranking
- **AND** it explains that the Skill generates local data files and a copyable AI analysis prompt
- **AND** it includes the exact text `它把材料放到你手里，也把解释权留给你。最终要不要分析、交给谁分析、分享哪些文件，都由你决定。`

## MODIFIED Requirements

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
