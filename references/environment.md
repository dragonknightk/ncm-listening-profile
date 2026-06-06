# 环境参考

当启动、路径发现、端口或依赖出问题时，读这份文件。

## Python 依赖

在 Skill 根目录安装依赖：

```powershell
python -m pip install -r scripts/requirements.txt
```

必需包：

- `psutil`：进程检测和端口占用提示
- `requests`：本机 CDP HTTP discovery endpoints
- `websocket-client`：Chrome DevTools Protocol WebSocket transport

依赖检查：

```powershell
python scripts/collect_ncm_profile.py --check
```

## 已验证客户端

v3 已验证以下本机客户端：

```text
NetEase Cloud Music 3.0.0 Beta 64-bit
Build 201967
Patch dd70f35
```

不要声称其他版本已验证。其他版本出现问题时，先读 `outputs/YYYYMMDD-HHMMSS/log/collection_diagnostics.json`。

## NetEase Cloud Music 进程规则

启动前先检测 `cloudmusic.exe`。如果已经运行：

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

第 4 步 `--list-playlists` 成功后，本 Skill 已经启动了带 9222 调试端口的客户端。用户选择主歌单后，采集命令使用 `--connect-existing-cdp` 连接同一次会话。

## cloudmusic.exe 发现顺序

使用：

1. `--cloudmusic-exe`
2. `NCM_CLOUDMUSIC_EXE`
3. Windows registry App Paths 和 uninstall entries
4. 固定磁盘上的常见安装路径

结果必须唯一指向一个 `cloudmusic.exe`。

没有找到时，询问用户准确路径：

```powershell
python scripts/collect_ncm_profile.py --cloudmusic-exe "D:\CloudMusic\cloudmusic.exe" --list-playlists
```

找到多个候选时，也询问用户选择哪一个，并传入 `--cloudmusic-exe`。

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
