## Context

当前 Skill 已经具备稳定的 API-only 采集链路，并输出 `result`、`csv`、`raw`、`aggregate` 和 diagnostics。v4 之后用户可见流程更清晰，但 README 第一屏仍有两处偏生硬：把项目描述成“整理成适合 AI 阅读的数据”，以及用否定式说明“不替你下结论”。本次希望保留具体功能说明，同时让开场更有吸引力。

`aggregate/aggregate.json` 当前已经包含播放集中度、重合数量和 only-in 样本，但这些更像静态事实索引。用户已经明确取消歌单整理、收藏批次和连续段落类指标，转而只补充“近期状态和长期核心有没有偏移”。因此 v5 只新增一组近期/长期排行偏移指标，不扩展为人格标签或类型学推断。

当前 `fetch_listening_record()` 把空列表当作失败：`weekData=[]` 会触发 `NcmApiError`。但如果用户最近一周确实没有听歌，空 `weekData[]` 是真实状态，不是接口错误。这个边界需要在 v5 一并修正，否则这类用户无法得到主歌单和所有时间排行数据。

## Goals / Non-Goals

**Goals:**

- 用新的 README 开场三段替换当前开场，在具体说明采集对象和输出产物的同时保留更自然的表达。
- 调整两版分析 prompt 的路径顺序，让三份完整 `result/*.jsonl` 在前，`aggregate/aggregate.json` 在后。
- 明确 `aggregate/aggregate.json` 是从 result 数据预先算出的统计和索引，用于定位趋势、极端值、重合项和样本，完整事实仍以三份 result 为准。
- 新增 `recentLongTermShiftStats`，只描述最近一周排行与所有时间排行之间的核心重合和排名变化。
- 允许最近一周排行为空，并让输出、diagnostics 和 aggregate 用 0、`null`、空数组自然表达这个状态。
- 保持所有新增字段中性、可验证，不包含 MBTI、人格结论、证据强弱或解释模板。

**Non-Goals:**

- 不新增 README 竞品对比内容。
- 不新增歌单重新编排、收藏批次、连续同专辑/同艺人段落指标。
- 不修改采集 API、输出目录结构、`result` 字段、`csv` 字段或 raw/diagnostics 隐私边界。
- 不把所有时间排行为空视为合法状态；`allData=[]` 仍然表示采集失败或账号无有效听歌记录。
- 不用 prompt 引导 AI 猜测特定 MBTI 类型。

## Decisions

### README 开场使用“自我备忘录”框架

README 开场改为三段：第一段用“自我备忘录”说明主歌单、最近一周排行和所有时间排行共同构成长期听歌痕迹；第二段具体说明采集三类数据、生成本地数据文件和分析 prompt；第三段用“解释权留给你”表达边界。

替代方案：继续使用“整理成适合 AI 阅读的数据”和“不在采集过程中替你下结论”。拒绝原因是这两句虽然准确，但像工具说明和防御性边界声明，不够打动普通用户。

### Prompt 路径顺序以完整事实优先

两版 prompt 都按以下顺序列路径：

```text
<run_dir>\result\primary_playlist.jsonl
<run_dir>\result\ranking_all_time.jsonl
<run_dir>\result\ranking_recent_week.jsonl
<run_dir>\aggregate\aggregate.json
```

`aggregate` 放在最后，并说明它是统计和索引。这样不会降低 aggregate 的价值，但能减少下游 AI 只看聚合摘要就开始画像的风险。

替代方案：继续把 `aggregate` 放在第一位。拒绝原因是大模型会优先受到路径列表和文件说明顺序影响，容易把 aggregate 当作主要解释框架，而不是快捷索引。

### 近期与长期偏移只看排行关系

新增指标组命名为 `recentLongTermShiftStats`，字段名沿用现有口径显式风格：

```text
recentWeekTop20TracksInAllTimeTop100Count
recentWeekTop20TracksInAllTimeTop100Share
allTimeTop20TracksInRecentWeekTop100Count
allTimeTop20TracksInRecentWeekTop100Share
recentWeekAllTimeOverlapMedianAbsoluteRankDelta
top10RecentWeekAllTimeOverlapByRankRise
top10RecentWeekAllTimeOverlapByRankDrop
```

`RankRise` 使用 `allTimeRank - recentWeekRank`，数值越大表示最近一周相对长期越明显上升。`RankDrop` 使用 `recentWeekRank - allTimeRank`，数值越大表示长期核心最近退得越明显。两个 Top10 样本保留 `title`、`artistNames`、`recentWeekRank`、`allTimeRank`、`rankDelta`、`recentWeekPlayCount`、`allTimePlayCount`。

替代方案：加入歌单顺序、收藏批次、连续段落指标。拒绝原因是用户当前数据大多不重新整理歌单，相关指标只能证明“未整理”，对本轮画像数据质量提升有限。

### 不把偏移指标解释成人格指标

`recentLongTermShiftStats` 只提供事实，帮助 AI 看见近期状态和长期核心之间的关系。它不输出 `INTJ`、`T/F`、`Ni`、`Te` 等类型学字段，也不写“证据强弱”。

替代方案：新增类型学导向字段或提示词。拒绝原因是用户明确希望保留分析惊喜，不希望通过 prompt 或字段名诱导 AI。

### 最近一周空排行是合法状态

`/api/v1/play/record?type=1` 返回 `weekData=[]` 时，采集应继续：`ranking_recent_week` 的 raw/result JSONL 写为空文件，CSV 写表头，diagnostics 记录 `recentWeekRows=0` 和最近一周播放计数字段完整率为 0，`aggregate` 中最近一周相关 Top/Bottom 样本为空。

`/api/v1/play/record?type=0` 返回 `allData=[]` 时仍然失败。所有时间排行是长期画像的核心事实来源，如果它为空，更可能是账号权限、接口结构或账号没有有效听歌记录的问题，不应伪装成成功画像数据。

替代方案：所有排行空列表都视为失败。拒绝原因是最近一周没有听歌很常见，失败会阻断仍然有价值的主歌单和所有时间排行采集。

## Risks / Trade-offs

- 新增 aggregate 字段可能增加文件体积 -> 只增加 7 个字段，其中样本索引限制为 Top10。
- 最近一周数据波动较强 -> 指标仅表达相对长期排行的偏移，不作为人格结论。
- 如果 recent/all-time 重合很少，中位排名差异和升降样本可能信息不足 -> 字段仍输出空列表或 `null`，让下游知道证据有限。
- 最近一周为空可能导致除 0 风险 -> 所有 share 字段在分母为空时输出 `0`，中位数在无重合样本时输出 `null`，Top10 升降样本输出空数组。
- README 文案更有情绪色彩 -> 第二段仍明确采集对象和输出产物，保证用户知道工具会做什么。
