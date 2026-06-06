## Why

当前 README 开场白已经说明了 Skill 用途，但部分措辞偏工具化，缺少足够自然的吸引力。与此同时，现有 `aggregate/aggregate.json` 能展示排行重合关系，却不能直接表达“最近一周状态”和“所有时间长期核心”之间的偏移幅度，导致 AI 分析时容易只停留在静态偏好总结。另一个边界问题是：如果用户最近一周没有听歌，网易云可能返回空的 `weekData[]`，这应当是合法状态，而不是采集失败。

## What Changes

- 优化 README 开场三段文案，让它在保留具体功能说明的同时，更自然地表达“网易云听歌痕迹可以成为 AI 理解用户的材料”。
- 调整两版分析 prompt 中的数据路径顺序：先列三份 `result/*.jsonl` 完整事实表，再列 `aggregate/aggregate.json`。
- 更新 prompt 中 `aggregate/aggregate.json` 的说明，明确它是从 result 数据预先算出的统计和索引，用于快速定位趋势、极端值、重合项和样本，完整事实仍以三份 result 为准。
- 在 `aggregate/aggregate.json` 中新增 `recentLongTermShiftStats` 指标组，专门描述最近一周排行与所有时间排行之间的核心重合、活跃延续和排名升降。
- 允许 `/api/v1/play/record?type=1` 返回空 `weekData[]`，并把它视为“最近一周无听歌记录”的合法成功状态；仍要求所有时间排行 `allData[]` 非空。
- 不新增竞品对比内容；网易云官方年报、周报和其他网易云工具的差异说明留到后续变更。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `ncm-listening-profile`: 更新 README 开场文案、分析 prompt 路径顺序和 aggregate 说明，新增近期与长期排行偏移指标的输出契约，并允许最近一周排行为空。

## Impact

- 影响 `README.md`、`SKILL.md`、`scripts/ncm_api.py`、`scripts/ncm_aggregate.py`、`references/api-patterns.md`、`references/schemas.md`、`references/troubleshooting.md`、`scripts/test_ncm_profile.py`。
- 影响当前 OpenSpec 规格中关于分析 prompt、README 文档、听歌排行 API 空数据边界和 aggregate 指标的要求。
- 不改变采集 API、输出目录结构、`result/*.jsonl` 字段、`csv/*.csv` 字段或 raw/diagnostics 隐私边界。
