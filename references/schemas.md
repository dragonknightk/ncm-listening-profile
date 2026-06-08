# Schema 参考

当你修改 result 字段、raw payload、aggregate、CSV 格式或诊断日志时，读这份文件。

## 输出布局

成功 run 精确写出：

```text
outputs/YYYYMMDD-HHMMSS/raw/primary_playlist.jsonl
outputs/YYYYMMDD-HHMMSS/raw/ranking_recent_week.jsonl
outputs/YYYYMMDD-HHMMSS/raw/ranking_all_time.jsonl
outputs/YYYYMMDD-HHMMSS/result/primary_playlist.jsonl
outputs/YYYYMMDD-HHMMSS/result/ranking_recent_week.jsonl
outputs/YYYYMMDD-HHMMSS/result/ranking_all_time.jsonl
outputs/YYYYMMDD-HHMMSS/csv/primary_playlist.csv
outputs/YYYYMMDD-HHMMSS/csv/ranking_recent_week.csv
outputs/YYYYMMDD-HHMMSS/csv/ranking_all_time.csv
outputs/YYYYMMDD-HHMMSS/aggregate/aggregate.json
outputs/YYYYMMDD-HHMMSS/log/collection_diagnostics.json
```

失败 run 可以只有：

```text
outputs/YYYYMMDD-HHMMSS/log/collection_diagnostics.json
```

不要创建 `index.jsonl`、`latest_run.txt`、manifest、collection report 或 `analysis_prompt.txt`。

## Primary Playlist Result

`result/primary_playlist.jsonl` 和 `csv/primary_playlist.csv` 使用同一字段集：

```text
order
title
artistNames
album
duration
durationMs
addedAt
```

规则：

- `title` 允许特殊字符和不可见 Unicode 字符，不要按视觉空白删除。
- `artistNames` 是艺人文本，多个艺人用 `/` 连接。
- `durationMs` 来自 API `track.dt`。
- `duration` 由 `durationMs` 格式化，例如 `03:58`。
- `addedAt` 来自 API `playlist.trackIds[].at`。
- JSONL 写缺失 `addedAt` 为 `null`。
- CSV 写缺失 `addedAt` 为空值。
- result/csv 不包含 `songId`、`artistId`、`albumId`、`score`。

## Ranking Result

`result/ranking_recent_week.jsonl`、`result/ranking_all_time.jsonl` 和对应 CSV 使用同一字段集：

```text
rank
title
artistNames
playCount
```

规则：

- `rank` 是 API 数组顺序，从 1 开始。
- `playCount` 是数字播放次数。
- result/csv 不包含 `songId`、`artistId`、`albumId`、`score`。

## Raw JSONL

Primary playlist raw row 示例：

```json
{
  "dataset": "primary_playlist",
  "source": "api",
  "order": 1,
  "trackId": "123",
  "apiTrack": {
    "id": "123",
    "name": "Song",
    "artistNames": "Artist A/Artist B",
    "artists": [{"id": "1", "name": "Artist A"}],
    "album": {"id": "9", "name": "Album"},
    "durationMs": 238000
  },
  "apiTrackId": {
    "id": 123,
    "at": 1716200000000
  }
}
```

Ranking raw row 示例：

```json
{
  "dataset": "ranking_recent_week",
  "source": "api",
  "rank": 1,
  "trackId": "123",
  "playCount": 32,
  "score": 98,
  "apiSong": {
    "id": "123",
    "name": "Song",
    "artistNames": "Artist A",
    "artists": [{"id": "1", "name": "Artist A"}],
    "album": {"id": "9", "name": "Album"},
    "durationMs": 238000
  }
}
```

raw 不写：

```text
creator
subscribers
privileges
coverImgUrl
recommendInfo
完整 API response
cookies/token/header/post data
```

`/api/user/playlist` 不落 raw 文件。

## Aggregate JSON

`aggregate/aggregate.json` 是单个 JSON 对象：

```text
schemaVersion
sources
counts
durationStats
addedAtStats
rankingStats
overlapStats
recentLongTermShiftStats
artistStats
albumStats
lexicalStats
sampleIndexes
```

aggregate 规则：

- 只包含统计、分布和中性索引。
- 不包含人格画像结论。
- 不包含证据强弱标签。
- 字段名里的 `top30`、`bottom20`、`top50`、`Max50` 等数量就是截断口径。
- 完整逐行事实仍在 `result/*.jsonl`。

代表性字段：

```text
top30ArtistsByPrimaryTrackCount
top30AlbumsByPrimaryTrackCount
top50PrimaryRecentWeekOverlapByRecentWeekPlayCount
recentWeekTop20TracksInAllTimeTop100Share
top10RecentWeekAllTimeOverlapByRankRise
bottom20RecentWeekTracksByPlayCount
top20EarliestAddedPrimaryTracks
singletonArtistsInPrimarySamplesMax50
```

## Diagnostics JSON

每次采集尝试都写：

```text
log/collection_diagnostics.json
```

核心结构：

```json
{
  "schemaVersion": 3,
  "skillVersion": "ncm-listening-profile-v6",
  "runId": "YYYYMMDD-HHMMSS",
  "createdAt": "2026-06-04T22:00:00+08:00",
  "updatedAt": "2026-06-04T22:00:01+08:00",
  "skillRoot": "<current skill root>",
  "verifiedEnvironments": [
    {
      "platform": "Windows",
      "status": "verified",
      "details": "Windows 10 with NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35; higher Windows systems and newer NetEase Cloud Music desktop clients have also passed real collection runs."
    },
    {
      "platform": "macOS",
      "status": "verified",
      "details": "macOS 26.3.1 arm64 with NeteaseMusicDesktop/3.1.7.3283."
    }
  ],
  "environment": {
    "os": "Windows",
    "platform": "...",
    "cdpPort": 9222,
    "clientPath": "...",
    "clientPlatform": "windows",
    "clientKind": "windows_exe",
    "cdpVersion": "...",
    "targetUrl": "orpheus://..."
  },
  "phases": {},
  "quality": {
    "primaryRows": 262,
    "recentWeekRows": 100,
    "allTimeRows": 100,
    "collectionSource": "api",
    "durationMsRows": 262,
    "durationMsMissingRows": 0,
    "addedAtRows": 262,
    "addedAtMissingRows": 0,
    "warnings": []
  },
  "failedPhase": "playlist_listing_api",
  "errorCode": "playlist_listing_api_ncmapierror",
  "errorSummary": "...",
  "repairHints": []
}
```

成功 run 可以没有 `failedPhase`、`errorCode`、`errorSummary`。

诊断日志必须保护隐私。不要写入：

```text
完整 API response
用户名
歌单全文
歌曲全文列表
cookies/token/header/post data
```

允许写入：

```text
阶段状态
接口路径
HTTP 状态码
API code
响应形状
命中数量
结果行数
字段完整率
错误类型
错误摘要
建议修复文件和函数
```
