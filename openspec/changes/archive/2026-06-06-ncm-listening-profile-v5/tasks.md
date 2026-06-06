## 1. README 和 Prompt 文案

- [x] 1.1 用已确认的三段开场替换 `README.md` 当前开场白。
- [x] 1.2 调整 `SKILL.md` 极简版 prompt 的路径顺序，使三份 `result/*.jsonl` 在前、`aggregate/aggregate.json` 在后。
- [x] 1.3 调整 `SKILL.md` 引导版 prompt 的路径顺序，使三份 `result/*.jsonl` 在前、`aggregate/aggregate.json` 在后。
- [x] 1.4 更新两版 prompt 中 `aggregate/aggregate.json` 的说明为已确认文案，并保持两段 prompt 适用场景说明原文不变。

## 2. Aggregate 指标实现

- [x] 2.1 在 `scripts/ncm_aggregate.py` 中新增最近一周排行与所有时间排行的 rank/playCount 合并样本构造逻辑。
- [x] 2.2 实现 `recentLongTermShiftStats.recentWeekTop20TracksInAllTimeTop100Count` 和对应 share。
- [x] 2.3 实现 `recentLongTermShiftStats.allTimeTop20TracksInRecentWeekTop100Count` 和对应 share。
- [x] 2.4 实现 `recentLongTermShiftStats.recentWeekAllTimeOverlapMedianAbsoluteRankDelta`。
- [x] 2.5 实现 `top10RecentWeekAllTimeOverlapByRankRise`，样本包含 `title`、`artistNames`、`recentWeekRank`、`allTimeRank`、`rankDelta`、`recentWeekPlayCount`、`allTimePlayCount`。
- [x] 2.6 实现 `top10RecentWeekAllTimeOverlapByRankDrop`，样本包含 `title`、`artistNames`、`recentWeekRank`、`allTimeRank`、`rankDelta`、`recentWeekPlayCount`、`allTimePlayCount`。

## 3. 文档和规格同步

- [x] 3.1 更新 `references/schemas.md` 的 aggregate 字段列表和代表性字段，加入 `recentLongTermShiftStats`。
- [x] 3.2 检查 `SKILL.md` 中 aggregate 边界说明，确保新增指标仍被描述为统计和索引，不写人格画像或证据强弱。

## 4. 测试和验证

- [x] 4.1 更新 `scripts/test_ncm_profile.py`，覆盖新增 `recentLongTermShiftStats` 字段、share 口径、中位绝对排名差和 Top10 升降样本形状。
- [x] 4.2 更新 `scripts/test_ncm_profile.py`，验证 `SKILL.md` 两版 prompt 的路径顺序和 aggregate 说明。
- [x] 4.3 运行 Python 单元测试。
- [x] 4.4 运行 `openspec validate` 或等价命令验证 v5 变更。

## 5. 最近一周空排行合法状态

- [x] 5.1 更新 `scripts/ncm_api.py`，允许 `fetch_listening_record(..., "recent_week")` 在 `weekData=[]` 时返回空列表，并继续要求 `fetch_listening_record(..., "all_time")` 的 `allData[]` 非空。
- [x] 5.2 确认空最近一周排行会写出空 `raw/ranking_recent_week.jsonl`、空 `result/ranking_recent_week.jsonl` 和只有表头的 `csv/ranking_recent_week.csv`。
- [x] 5.3 更新 diagnostics 和质量计数期望，确保合法空最近一周成功 run 记录 `recentWeekRows=0`，不会写 `failedPhase=ranking_recent_week_api`。
- [x] 5.4 更新 `SKILL.md`、`references/api-patterns.md` 和 `references/troubleshooting.md` 中关于“数据集为空即失败”的说明，标明最近一周空排行是合法例外。
- [x] 5.5 增加单元测试，覆盖 `weekData=[]` 合法、`allData=[]` 失败、空最近一周成功写出输出文件，以及 aggregate 在空最近一周下输出 0、`null` 和空数组且不发生除 0。
- [x] 5.6 运行 Python 单元测试。
- [x] 5.7 运行 `openspec validate --changes "ncm-listening-profile-v5"`。
