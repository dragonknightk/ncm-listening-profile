## Context

当前 Skill 的采集链路由两部分组成：环境层负责发现并启动网易云桌面客户端、开放本机 `9222` CDP；采集层通过 CDP 在已登录页面上下文里执行网易云 `/api` 请求并写出结果。真实验证表明，Windows 和 macOS 的核心采集链路都能工作，差异主要集中在客户端发现、进程检测和启动命令。

现有代码和文档仍以 Windows `cloudmusic.exe` 为中心：参数名、环境变量、进程规则、路径发现、README 和 troubleshooting 都把 Windows 当成唯一支持平台。继续在这些名字上叠加 macOS 会让接口变形，因此本次把环境层概念从 `cloudmusic.exe` 改成通用的“网易云桌面客户端”。

## Goals / Non-Goals

**Goals:**

- 让 macOS 用户可以按标准 Skill 流程自动启动 `NeteaseMusic.app`、列出歌单、选择主歌单并采集数据。
- 保留 Windows 自动发现和启动 `cloudmusic.exe` 的能力。
- 把平台差异限制在环境层，保持 CDP 连接、API 请求、结果 shaping、aggregate 和输出 layout 稳定。
- 用 `--client-path` 和 `NCM_CLIENT_PATH` 替代 Windows-only 的 `--cloudmusic-exe` 和 `NCM_CLOUDMUSIC_EXE`。
- 更新文档，把兼容性风险重心从“客户端版本号”改为“CDP 可用性、登录态、页面上下文执行和网易云服务端 API shape”。
- 补充 Windows 与 macOS 已真实采集通过的环境矩阵。

**Non-Goals:**

- 不新增远程 SSH 采集产品流程；SSH 只作为本次开发验收时远程执行 Mac 测试的通道。
- 不新增网页登录采集、cookie 粘贴、token 粘贴或 Python 直连网易云业务 API。
- 不改网易云 `/api` 路径、输出字段、输出目录结构或 diagnostics 隐私边界。
- 不保留 `--cloudmusic-exe` / `NCM_CLOUDMUSIC_EXE` 兼容层；本次直接替换成通用命名。
- 不把某个客户端版本写成硬性版本要求。

## Decisions

### 环境层使用跨平台客户端抽象

`ncm_env.py` 增加桌面客户端抽象，覆盖平台、路径、进程名和启动命令。Windows 分支继续发现 `cloudmusic.exe`；macOS 分支发现 `NeteaseMusic.app`。上层 `collect_ncm_profile.py` 只关心“唯一客户端路径”和“已启动 CDP”，不关心 `.exe` 或 `.app` 细节。

替代方案：保留 `cloudmusic.exe` 命名并在内部特殊处理 `.app`。拒绝原因是它会把 Windows 实现细节暴露到 macOS 文档、参数和 diagnostics 里，后续排障很别扭。

### macOS 启动使用 `open -na ... --args`

macOS 启动命令使用已真实验证的形式：

```bash
open -na <NeteaseMusic.app> --args --force-renderer-accessibility=complete --remote-debugging-port=9222
```

`-n` 确保启动新实例，`-a` 让 macOS 按 `.app` bundle 启动，`--args` 后的参数传给客户端进程。启动后继续轮询 `http://127.0.0.1:9222/json/version`，和 Windows 共用 CDP readiness 逻辑。

替代方案：直接执行 `.app/Contents/MacOS/NeteaseMusic`。拒绝原因是绕过 LaunchServices 可能改变应用容器、图形会话和登录态行为；真实验证过的路径是 `open -na`。

### 已运行客户端仍要求用户手动关闭

Windows 检测 `cloudmusic.exe`，macOS 检测 `NeteaseMusic` 和 `NeteaseMusic Helper`。如果发现已运行客户端，Skill 继续停止采集并要求用户选择重新采集或使用旧数据；重新采集时让用户手动关闭客户端，不自动 kill。

替代方案：连接已运行客户端或自动终止后重启。拒绝原因是已运行客户端通常没有按 Skill 参数开放 CDP，自动连接会混淆登录态和端口状态；自动 kill 会破坏用户正在播放或编辑的会话。

### CLI 和 diagnostics 使用通用命名

CLI 使用 `--client-path`，环境变量使用 `NCM_CLIENT_PATH`。diagnostics 环境字段使用 `clientPath`、`clientPlatform`、`clientLaunchMode` 等通用名称；不再写 `cloudmusicExe` 这类 Windows-only 字段。

替代方案：保留旧参数作为 alias。拒绝原因是这会让文档和测试长期背着旧命名，后续平台扩展继续被历史参数牵制。本仓库迭代策略偏向一次性改干净。

### API 层保持不变

`ncm_cdp.py`、`ncm_api.py`、`ncm_outputs.py`、`ncm_aggregate.py` 不做结构性改动。macOS 成功样本已经证明当前 CDP target 选择和页面上下文 API 请求可以工作：`targetUrl` 为 `orpheus://orpheus/app.html`，主歌单、最近一周排行和所有时间排行均成功采集。

替代方案：为 macOS 新增单独 API 路径或采集器。拒绝原因是数据兼容性主要取决于网易云服务端 API shape，当前 Windows/macOS 共用页面上下文 API 模型更简单，也更容易诊断。

### 文档改成已验证环境矩阵

README、Skill 和 reference 文档不再写“其他版本未验证”。新的口径是：已在 Windows 10 + 旧验证版本、更高 Windows 系统和更新网易云桌面客户端、macOS 26.3.1 arm64 + `NeteaseMusicDesktop/3.1.7.3283` 上真实采集通过。其他环境失败时优先读 diagnostics，判断是 CDP、登录态还是 API shape 问题。

替代方案：继续按客户端版本号声明兼容范围。拒绝原因是当前采集方式不强绑定客户端版本，版本号不是主要风险来源。

## Risks / Trade-offs

- macOS `open -na` 依赖图形登录会话 -> troubleshooting 明确要求在已登录桌面会话中运行，并把 CDP 超时指向环境层排查。
- macOS 进程检测可能看到 helper 进程残留 -> 检测规则把主进程和 helper 都列出，让用户知道需要完整退出客户端。
- `--client-path` 替换旧参数会影响手动脚本用户 -> README、SKILL 和错误提示统一改为新参数，减少长期混乱。
- 服务端 API shape 未来可能变化 -> 保持 diagnostics 的 phase、status、response shape 和 repair hints，让 agent 优先修 API 兼容。
- Windows 现有路径发现可能因重构回归 -> 增加单测覆盖 Windows registry/env/common path 分支和启动参数。

## Migration Plan

1. 修改 spec delta，确立 Windows + macOS 桌面客户端合同和新 CLI 命名。
2. 重构 `ncm_env.py` 的路径发现、进程检测和启动函数。
3. 更新 `collect_ncm_profile.py` 参数和 diagnostics 写入点。
4. 更新测试，覆盖 Windows 与 macOS 环境层行为。
5. 更新 Skill、README 和 references 文档。
6. 在 Windows 跑单测和现有采集检查。
7. 通过 SSH 在 Mac 上同步代码，执行真实 macOS 自动启动、列歌单和采集验收。

## Open Questions

- Windows “更高系统和更新客户端”是否需要补精确版本号。如果用户后续提供版本号，应写进已验证环境矩阵；本次先按用户确认的真实通过事实记录。
