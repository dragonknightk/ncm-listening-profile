## Why

v3 的采集内核已经稳定转向 API-only，但用户可见交互仍缺少明确契约：首次回应突兀、歌单选择列表暴露内部字段、prompt 适用场景容易被压缩。v4 需要把“采集工具”整理成更清晰、更少决策噪声的用户流程，同时保留当前开发期直接、可诊断的运行方式。

## What Changes

- 新增 Skill 首次用户可见回应契约，说明本 Skill 会采集供 AI 做听歌画像分析的数据、采集哪些数据、输出数据文件和分析 prompt，并声明本轮不直接做画像结论。
- 新增精简 Python 环境要求，要求开始采集、列歌单或读取旧 run 前先运行 `python scripts/collect_ncm_profile.py --check`。
- 将 `--list-playlists` 的公开选择视图改为只包含 `index`、`name`、`trackCount`，用户表格固定为“编号 / 歌单名 / 曲数”，并使用固定的温柔话术说明主歌单只能选一个的理由。
- 保留用户按歌单名匹配的能力，新增按编号选择主歌单的 `--playlist-index`。
- **BREAKING**: 删除 `--playlist-id` 用户接口，不再要求或允许用户通过 `playlistId` 选择主歌单。
- 输出两版分析 prompt 时，必须完整保留各自“适合场景”说明，不允许概括、压缩或改写。
- 采集成功后只展示 run 目录和文件夹用途概括，不再单独铺开所有 result/csv/log 文件路径，也不展开 CSV 字段释义；提示用户看 CSV 字段不清楚时可咨询 AI。
- 同步更新 `references/api-patterns.md`，把“对外展示字段”改为三列，避免 reference 把 agent 带回内部字段展示。
- 优化 reference 路由：在 `SKILL.md` 对应流程中说明何时读取 `environment.md`、`api-patterns.md`、`schemas.md`、`troubleshooting.md`。
- 保留检测到 `cloudmusic.exe` 已运行时展示 PID 和 exe 路径的行为，方便用户确认确实存在运行中的客户端。
- 不处理 legacy run，不迁移 `outputs/` 目录，不新增行为级 eval；当前开发期继续用人工测试和脚本单测验证。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `ncm-listening-profile`: 调整 Skill 用户沟通契约、Python 环境前置检查、歌单公开选择字段、主歌单选择接口、成功输出收口、prompt 场景说明输出契约和 reference 路由。

## Impact

- 影响 `SKILL.md`、`references/api-patterns.md`、相关 reference 路由文字和采集完成后的用户可见输出模板。
- 影响 `scripts/collect_ncm_profile.py`、`scripts/ncm_api.py` 中的 CLI 参数、歌单公开展示数据和主歌单解析逻辑。
- 影响单元测试：补充公开歌单列表不含内部字段、按编号解析歌单、prompt 适合场景原文存在的回归测试。
