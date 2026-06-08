## Why

`ncm-listening-profile` 已经通过 Windows 和 macOS 的真实采集验证，但当前仓库仍把 Skill 描述为 Windows-only，并把客户端兼容性表达成过窄的单版本假设。现在需要把已验证的跨平台事实落到 Skill 合同里，让 macOS 用户也能按标准流程自动启动客户端、列出歌单并采集数据。

## What Changes

- 支持 macOS 桌面版 `NeteaseMusic.app` 的自动发现、已运行进程检测和 `9222` CDP 启动。
- **BREAKING**: 把手动指定客户端路径的 CLI 参数和环境变量从 `--cloudmusic-exe` / `NCM_CLOUDMUSIC_EXE` 替换为 `--client-path` / `NCM_CLIENT_PATH`。
- 保留 Windows `cloudmusic.exe` 的现有采集能力，并把 diagnostics 字段泛化为跨平台命名。
- 维持本机 `127.0.0.1:9222` CDP、页面上下文 `fetch(..., { credentials: "include" })`、现有网易云 `/api` 路径和输出 schema 不变。
- 更新 Skill、README 和参考文档，把“只支持 Windows / 只验证旧版本”改为 Windows + macOS 已验证环境矩阵。
- 明确兼容性口径：数据采集主要依赖网易云服务端 API 返回结构；客户端和系统版本主要影响本机客户端启动、CDP 暴露、登录态和页面上下文执行。
- 不新增远程 SSH 采集产品流程；SSH 只作为开发和验收时远程执行 Mac 测试的通道。

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `ncm-listening-profile`: 扩展桌面客户端环境要求、进程检测、客户端发现、启动规则和已验证环境说明，覆盖 Windows 与 macOS。

## Impact

- `scripts/ncm_env.py`: 平台识别、客户端路径发现、进程检测、启动命令和错误提示。
- `scripts/collect_ncm_profile.py`: CLI 参数、connect runtime 环境字段和向后兼容处理。
- `scripts/ncm_diagnostics.py`: diagnostics 环境字段命名和已验证环境说明。
- `scripts/test_ncm_profile.py`: Windows/macOS 客户端发现、进程识别、启动命令和 diagnostics 测试。
- `SKILL.md`, `README.md`, `README.en.md`, `references/*.md`: 平台支持、已验证环境矩阵、兼容性边界和排障说明。
- `openspec/specs/ncm-listening-profile/spec.md`: 采集 Skill 的平台契约和环境要求。
