## Context

当前 v2 Skill 通过 CDP 启动或连接 Windows 桌面版网易云音乐，并以 DOM 抽取为主：侧边栏 DOM 列歌单、歌单页面 DOM 抽主歌单行、排行页 DOM 抽最近一周和所有时间排行，再用页面上下文 playlist detail fetch 补 `addedAt`。这种设计已经能工作，但 DOM selector、滚动抽取和排行页打开逻辑会随客户端 UI 改版持续变动。

v3 探索验证了已登录客户端页面上下文中的 `/api` 读取接口：

```text
/api/nuser/account/get
/api/user/playlist
/api/v6/playlist/detail
/api/v1/play/record
```

这些接口可以覆盖当前 result 所需字段。v3 因此改成 API-only：CDP 只提供已登录页面上下文和本地调试通道，不再承担 DOM 抽取职责。

## Goals / Non-Goals

**Goals:**

- 用页面上下文 API 重写当前用户、歌单列表、主歌单、最近一周排行和所有时间排行采集。
- 删除 DOM 采集器、DOM fallback、DOM selector 文档和 DOM repair hints。
- 保持 result/csv 字段不变，让既有分析输入不因 v3 增加 API 字段而变嘈杂。
- 保留 raw，但 raw 只作为精简源字段追溯，不写完整 API response。
- 新增 `aggregate/aggregate.json`，只做纯计算统计和中性索引。
- 保持 Skill collection-only，不在采集会话内进行人格画像分析。

**Non-Goals:**

- 不从 Python 直接请求网易云业务接口。
- 不主动调用或解密 `/eapi` POST。
- 不保存歌单列表 raw。
- 不在 result 中新增 `songId`、`artistId`、`albumId`、`score` 等字段。
- 不让 aggregate 输出画像结论、证据强弱或固定分析模板。
- 不保留任何 DOM 采集路径作为兼容 fallback。

## Decisions

### API-only 采集链路

采集流程改为：

```text
connect_runtime
  -> api_get_current_user
  -> api_list_created_playlists
  -> resolve selected playlist
  -> api_collect_primary_playlist
  -> api_collect_recent_week_record
  -> api_collect_all_time_record
  -> shape raw/result/csv
  -> build aggregate
  -> write diagnostics
```

所有网易云业务数据请求都必须通过 CDP `Runtime.evaluate` 在客户端页面上下文中执行 `fetch(..., { credentials: "include" })`。Python 只连接本地 CDP endpoint，不直接请求 `music.163.com` 业务接口。

替代方案：保留 DOM fallback。拒绝原因是 v3 的目标是清理兼容性债务；保留 DOM 旧路径会继续要求维护旧 selector、滚动抽取、可见文本解析和 repair hints，不符合本次迁移标准。

### API 白名单

v3 允许的主动业务 API 只有：

```text
GET /api/nuser/account/get
GET /api/user/playlist?uid=<uid>&limit=1000&offset=0
GET /api/v6/playlist/detail?id=<playlistId>&n=100000&s=0
GET /api/v1/play/record?uid=<uid>&type=1
GET /api/v1/play/record?uid=<uid>&type=0
```

如果任一 API 返回 `401`、`403`、`429`、非 `200` code、无法解析 JSON、缺少必要字段或行数为 0，相关阶段失败并写 diagnostics。本次采集不再尝试 DOM fallback。

替代方案：观察客户端自然 `/eapi` 请求并解密响应。拒绝原因是 `/eapi` 响应在 fetch hook 和 CDP response body 层表现为加密/封装文本，解密会把实现绑到客户端内部加密 SDK 和打包模块上，复杂且脆弱。

### Result schema 保持 v2 不变

主歌单 result 继续写：

```text
order
title
artistNames
album
duration
durationMs
addedAt
```

排行 result 继续写：

```text
rank
title
artistNames
playCount
```

API 中的 `song.id`、`ar[].id`、`al.id`、`score` 等字段只允许进入 raw 或 aggregate 的中性索引，不进入 result/csv。

替代方案：把更多 API 字段加入 result。拒绝原因是 result 是正式分析事实表，字段越多越会诱导下游 AI 把篇幅花在平台元数据上；用户已明确认为额外字段对人格画像价值不大。

### Raw 保留精简 API 源字段

继续写：

```text
raw/primary_playlist.jsonl
raw/ranking_recent_week.jsonl
raw/ranking_all_time.jsonl
```

raw 可以保留歌曲、艺人、专辑、排行和歌单条目本身的源字段，例如歌曲 ID、艺人 ID、专辑 ID、API 原始歌长、加入时间、播放次数和 `score`。raw 不保存：

```text
creator
subscribers
privileges
coverImgUrl
recommendInfo
完整 API response
cookies/token/header/post data
```

`/api/user/playlist` 只用于用户选择主歌单，不写 `raw/user_playlists.jsonl`。

替代方案：完整保存 API response 以方便排错。拒绝原因是完整响应过大，包含账号、社交、权限、推荐和图片链接等大量非画像字段，会扩大隐私面并降低排错聚焦度。

### Aggregate 是纯计算索引

成功 run 新增：

```text
aggregate/aggregate.json
```

aggregate 从 result 和必要 raw 标识字段计算，只包含统计、分布、重合、Top/Bottom/Earliest/Latest 等中性索引，不包含画像结论、不标注证据强弱。截断字段必须在字段名里写清数量和排序口径，例如 `top30ArtistsByPrimaryTrackCount`、`bottom20RecentWeekTracksByPlayCount`。

替代方案：拆成多个 JSON 或 JSONL。拒绝原因是聚合数据天然是树状统计，一份 `aggregate.json` 更容易作为预计算索引被读取；JSONL 仍保留给逐行事实表 result/raw。

### Diagnostics 改为 API 阶段诊断

diagnostics 继续保护隐私，只记录阶段、状态、接口路径、状态码、响应 shape、行数、质量计数、失败摘要和修复提示。diagnostics 不记录完整响应、歌单全文、歌曲全文列表、cookies、token、请求头或请求体。

旧 `selector`、`strategy=playlist_dom`、`strategy=ranking_dom`、DOM repair hints 都应移除，替换为 API 阶段和 API shape/field completeness 诊断。

### Prompt 保留两版并加入选择说明

两版 prompt 都引用 `aggregate/aggregate.json` 和三份 result JSONL。极简版只给数据路径和开放问题；引导版使用温柔语言引导 AI 从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解用户，避免冷冰冰的规则列表。

每版 prompt 后追加用户已确认的适用场景说明，不出现“新会话”字样。

## Risks / Trade-offs

- API endpoint 未来变更或失效 → diagnostics 记录失败接口、状态码、响应 shape 和缺失字段，后续直接修 API collector，而不是回退 DOM。
- API-only 去掉 DOM 后没有可见文本兜底 → result 以 API 数据为事实来源；如果 API 返回字段不完整，本次采集失败并写 diagnostics。
- `/api/user/playlist` 返回比侧边栏更多歌单 → 只筛选 `userId == 当前 uid` 且 `subscribed == false`，不按 `specialType` 过滤，由用户显式选择主歌单。
- aggregate 可能被误读为完整事实 → `SKILL.md` 和 schema 说明必须写清 aggregate 是预计算统计和索引，完整事实仍在 result。
- raw 保留较多 API 字段可能扩大数据体积 → 明确禁止完整 response 和账号/社交/权限/请求敏感字段，保留字段以源追溯为边界。

## Migration Plan

1. 新增 API 页面上下文 fetch helper 和 API collector。
2. 用 API collector 重写歌单列表、主歌单、最近一周排行、所有时间排行流程。
3. 重写 raw/result shaping，保持 result/csv 字段不变。
4. 新增 aggregate builder 和 `aggregate/aggregate.json` 写出。
5. 更新 diagnostics 阶段、repair hints 和 schema。
6. 删除 DOM 抽取函数、DOM selector 参考、DOM fallback 测试和 `playingList` 依赖路径。
7. 更新 `SKILL.md`、reference docs、prompt 和输出说明。
8. 用单元测试覆盖 API shaping、raw 排除字段、aggregate 计算和 diagnostics 隐私边界；用真实客户端验证 v3。

## Open Questions

无。当前讨论已明确：v3 API-only，DOM 全删，aggregate 为单文件纯计算索引，raw 不保存完整响应和指定敏感/低价值字段。
