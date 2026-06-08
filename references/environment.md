# 环境参考

当启动、路径发现、端口或依赖出问题时，读这份文件。

## Python 依赖

在 Skill 根目录安装依赖。Windows 通常使用：

```powershell
python -m pip install -r scripts/requirements.txt
```

macOS 如果 `python` 不是 `Python 3.10+`，使用：

```bash
python3 -m pip install -r scripts/requirements.txt
```

必需包：

- `psutil`：进程检测和端口占用提示
- `requests`：本机 CDP HTTP discovery endpoints
- `websocket-client`：Chrome DevTools Protocol WebSocket transport

依赖检查：

```powershell
python scripts/collect_ncm_profile.py --check
```

或在 macOS 上使用：

```bash
python3 scripts/collect_ncm_profile.py --check
```

## 已验证环境

已真实采集通过的环境：

```text
Windows：Windows 10 + NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35；以及更高 Windows 系统和更新网易云桌面客户端。
macOS：macOS 26.3.1 arm64 + NeteaseMusicDesktop/3.1.7.3283。
```

采集链路主要依赖网易云桌面客户端提供的已登录页面上下文和本机 CDP。数据结构兼容性主要取决于网易云服务端 API；客户端或系统版本通常不是主要风险，除非它影响客户端启动、CDP 暴露、登录态或页面上下文执行。

## NetEase Cloud Music 进程规则

启动前先检测网易云音乐桌面客户端是否已经运行：

- Windows：`cloudmusic.exe`
- macOS：`NeteaseMusic`、`NeteaseMusic Helper`

如果已经运行：

1. 立即停止采集流程。
2. 不要 kill 进程。
3. 不要自动分析旧结果。
4. 询问用户：重新采集，还是使用旧数据。

用户选择重新采集时，让用户手动关闭网易云音乐，再继续。

用户选择旧数据时，运行：

```powershell
python scripts/collect_ncm_profile.py --list-runs
```

然后让用户选择一个已有 run，只输出路径和 prompt，不启动或连接网易云音乐。

第 4 步 `--list-playlists` 成功后，本 Skill 已经启动了带 `9222` 调试端口的客户端。用户选择主歌单后，采集命令使用 `--connect-existing-cdp` 连接同一次会话。

## 客户端路径发现顺序

使用：

1. `--client-path`
2. `NCM_CLIENT_PATH`
3. 平台默认发现路径

Windows 默认发现：

- Windows registry App Paths 和 uninstall entries
- 固定磁盘上的常见安装路径，例如 `Netease\CloudMusic\cloudmusic.exe`、`NetEase\CloudMusic\cloudmusic.exe`、`CloudMusic\cloudmusic.exe`

macOS 默认发现：

- `/Applications/NeteaseMusic.app`
- `~/Applications/NeteaseMusic.app`

结果必须唯一指向一个平台对应的网易云音乐桌面客户端：

- Windows：`cloudmusic.exe`
- macOS：`NeteaseMusic.app`

没有找到时，询问用户准确路径。

Windows 示例：

```powershell
python scripts/collect_ncm_profile.py --client-path "D:\CloudMusic\cloudmusic.exe" --list-playlists
```

macOS 示例：

```bash
python3 scripts/collect_ncm_profile.py --client-path "/Applications/NeteaseMusic.app" --list-playlists
```

找到多个候选时，也询问用户选择哪一个，并传入 `--client-path`。

## 启动命令

Windows 启动：

```powershell
cloudmusic.exe --force-renderer-accessibility=complete --remote-debugging-port=9222
```

macOS 启动：

```bash
open -na /Applications/NeteaseMusic.app --args --force-renderer-accessibility=complete --remote-debugging-port=9222
```

macOS 启动需要用户已处于图形登录会话。通过 SSH 验证时，可以远程执行命令，但网易云首次登录、授权或弹窗处理通常仍需要用户在 Mac 桌面会话中完成。

## CDP 端口

固定使用端口 `9222`。如果端口被占用，告诉用户：

```text
Port 9222 is required by this Skill. Close the occupying program and run again.
```

不要探测 `9223` 或其他端口。

## 网络边界

Python 进程只访问：

```text
http://127.0.0.1:9222/json/version
http://127.0.0.1:9222/json
ws://127.0.0.1:9222/...
```

网易云业务 API 请求由已登录客户端页面上下文发起，保留客户端自己的登录态和风控上下文。不要在 Python 里直接请求网易云业务 API。
