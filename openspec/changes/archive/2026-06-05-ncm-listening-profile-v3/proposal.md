## Why

v2 仍以 DOM 抽取为核心，虽然已有诊断和自修复机制，但不同网易云音乐客户端版本的 DOM 结构差异会持续制造兼容性负担。实测表明，在已登录桌面客户端页面上下文中，网易云 `/api` 接口可以完整获取用户创建歌单、主歌单详情、最近一周排行和所有时间排行，因此 v3 应改为更干净的 API-only 采集链路。

同时，当前分析 prompt 需要下游 AI 临场计算大量统计，容易把输出篇幅挤成数据报告。v3 需要新增纯计算聚合层，把常用统计和中性索引提前算好，但不替 AI 固定画像口径。

## What Changes

- **BREAKING**: 删除 DOM 采集路径、DOM fallback、DOM 适配/自修复相关契约和文档，不再把 DOM 作为事实来源。
- **BREAKING**: 采集失败策略改为 API 失败即本次采集失败并写出 diagnostics，不再尝试 DOM 修补。
- 将当前登录用户识别改为通过页面上下文 `fetch` 调用 `/api/nuser/account/get` 获取。
- 将用户创建歌单列表改为通过页面上下文 `fetch` 调用 `/api/user/playlist` 获取，并筛选当前登录用户创建的歌单。
- 将主歌单采集改为通过页面上下文 `fetch` 调用 `/api/v6/playlist/detail` 获取 `tracks[]` 和 `trackIds[]`。
- 将最近一周和所有时间听歌排行改为通过页面上下文 `fetch` 调用 `/api/v1/play/record` 获取。
- 保持 `result/*.jsonl` 和 `csv/*.csv` 字段不变，避免把 `score`、歌曲 ID、专辑 ID、艺人 ID 等字段加入正式画像输入表。
- 保留 `raw/primary_playlist.jsonl`、`raw/ranking_recent_week.jsonl`、`raw/ranking_all_time.jsonl`，但只写精简 API 源字段，不写完整 API response，也不写歌单列表 raw。
- 明确 raw 禁止保存 `creator`、`subscribers`、`privileges`、`coverImgUrl`、`recommendInfo`、完整 API response、`cookies`、`token`、请求头和请求体。
- 新增 `aggregate/aggregate.json`，作为纯计算统计和中性索引输出，不写画像结论、不标注证据强弱。
- 更新 `SKILL.md`、schema 说明、诊断说明和两版分析 prompt，使其解释 result、raw、aggregate 的用途和边界。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `ncm-listening-profile`: 将采集契约从 DOM-first/CDP extractor 改为 API-only；调整 raw、diagnostics、输出目录和分析 prompt 契约；新增 `aggregate/aggregate.json` 聚合输出。

## Impact

- 影响 Skill 说明文档、OpenSpec spec、schema/troubleshooting/environment 参考文档。
- 影响采集脚本的核心流程、CDP 页面上下文 fetch 工具、输出整形、raw 写出、diagnostics、测试。
- 需要删除旧 DOM 抽取函数、DOM selector 参考、DOM repair hints 和与 DOM fallback 相关的测试。
- 不新增 Python 对网易云业务接口的直接请求；API 请求必须在已登录客户端页面上下文内执行。
