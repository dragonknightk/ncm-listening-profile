# API 采集参考

当 NetEase Cloud Music 采集失败时，先读本次 run 的 `log/collection_diagnostics.json`，根据 `failedPhase`、`apiPath`、`status`、`responseShape` 和 `repairHints` 定位函数。客户端或系统版本通常不是主要风险；真正需要重点排查的是 CDP 是否可用、页面上下文是否有登录态、网易云服务端 API 返回结构是否仍兼容。

## 启动参数

Windows 启动 NetEase Cloud Music：

```powershell
cloudmusic.exe --force-renderer-accessibility=complete --remote-debugging-port=9222
```

macOS 启动 NetEase Cloud Music：

```bash
open -na /Applications/NeteaseMusic.app --args --force-renderer-accessibility=complete --remote-debugging-port=9222
```

预期本机 CDP endpoints：

```text
http://127.0.0.1:9222/json/version
http://127.0.0.1:9222/json
```

历史目标 URL：

```text
orpheus://orpheus/pub/app.html
orpheus://orpheus/app.html
```

Python 只访问上面的本机 CDP endpoints。网易云业务数据必须由页面上下文发起：

```javascript
fetch("https://music.163.com/api/...", {
  credentials: "include",
  method: "GET"
})
```

不要用 Python `requests` 直接请求 `music.163.com` 业务接口。

## 允许的业务 API

主动调用的业务 API 只有：

```text
/api/nuser/account/get
/api/user/playlist
/api/v6/playlist/detail
/api/v1/play/record
```

对应用途：

```text
current_user_api          /api/nuser/account/get
playlist_listing_api      /api/user/playlist?uid=<uid>&limit=1000&offset=0
primary_playlist_api      /api/v6/playlist/detail?id=<playlistId>&n=100000&s=0
ranking_recent_week_api   /api/v1/play/record?uid=<uid>&type=1
ranking_all_time_api      /api/v1/play/record?uid=<uid>&type=0
```

如需新增接口，先更新 OpenSpec 和本参考，再改 `scripts/ncm_api.py` 的白名单。

## 当前用户

`/api/nuser/account/get` 必须返回：

```text
code = 200
profile.userId
```

`profile.userId` 是后续歌单列表和听歌排行的 `uid`。如果缺失，阶段 `current_user_api` 失败。

## 用户创建歌单

`/api/user/playlist` 返回的 `playlist[]` 需要筛选：

```text
str(item.userId) == str(current userId)
item.subscribed == false
```

不要按 `specialType` 过滤。特殊类型歌单仍交给用户选择。

对外展示的选择列表只保留足够选择的信息：

```text
index
name
trackCount
```

不要向用户展示 `playlistId`、`playCount`、`specialType`、`privacy`、`updateTime`、`source` 或脚本原始 JSON。`playlistId` 只作为内部采集 `/api/v6/playlist/detail` 的参数使用。

这份列表不写入 raw。

## 主歌单

`/api/v6/playlist/detail` 是主歌单事实来源。要求返回：

```text
playlist.tracks[]
playlist.trackIds[]
```

主歌单 result 字段映射：

```text
order        tracks[] 顺序，从 1 开始
title        track.name
artistNames  track.ar[].name 用 / 连接
album        track.al.name
durationMs   track.dt
duration     由 durationMs 格式化
addedAt      playlist.trackIds[].at 格式化
```

`track.name` 可以是特殊字符或不可见 Unicode 字符。只要 API 字段存在，就不要按空白视觉效果删除。

## 听歌排行

`/api/v1/play/record` 是排行事实来源：

```text
type=1  -> weekData[]  -> ranking_recent_week
type=0  -> allData[]   -> ranking_all_time
```

排行 result 字段映射：

```text
rank         API 数组顺序，从 1 开始
title        row.song.name
artistNames  row.song.ar[].name 用 / 连接
playCount    row.playCount
```

`score` 不进入 result/csv；如果 API 返回，可以保留在 raw。

`type=1` 的 `weekData=[]` 是合法状态，表示最近一周没有听歌记录；继续写出 0 行 `ranking_recent_week` 输出。`type=0` 的 `allData=[]` 仍视为失败。

## 失败策略

以下情况均视为本次采集失败，并写 diagnostics：

```text
HTTP status 为 401/403/429
HTTP status 不是 200
响应无法解析为 JSON
JSON 顶层不是对象
code 不是 200
必要字段缺失
关键数据集为空，合法的 weekData=[] 除外
```

修复时优先检查：

```text
scripts/ncm_api.py
scripts/ncm_outputs.py
scripts/ncm_aggregate.py
scripts/collect_ncm_profile.py
scripts/test_ncm_profile.py
```
