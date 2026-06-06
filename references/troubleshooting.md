# 故障排查

采集失败或数据可疑时，先读本次 run 的：

```text
log/collection_diagnostics.json
```

不要先要求用户提交 issue。先根据 `failedPhase`、`errorCode`、`repairHints` 判断是否能在当前被调用的 Skill 实例中完成兼容性修复。

## 修复边界

在哪个 Skill 实例被调用，就修复哪个 Skill 实例：

- 项目内 Skill：修当前仓库或项目中的 Skill 根目录
- 全局 Skill：修全局 Skill 目录

不要把修复路径写死成某台机器上的项目路径。

## 隐私边界

`collection_diagnostics.json` 不保存：

```text
完整 API response
用户名
歌单全文
歌曲全文列表
cookies/token/header/post data
```

如果后续排查确实需要更多敏感材料，由用户和 agent 在当次会话中明确决定是否分享。不要把这些材料写回 diagnostics。

## NetEase Cloud Music 已经运行

如果发现 `cloudmusic.exe` 已经运行：

1. 停止流程。
2. 不要 kill 进程。
3. 不要自动用旧数据分析。
4. 询问用户：重新采集，还是使用旧数据。

重新采集：让用户手动关闭网易云音乐，再运行列表/采集流程。

使用旧数据：

```powershell
python scripts/collect_ncm_profile.py --list-runs
```

然后只输出旧 run 的 result/csv/aggregate/log 路径和两版 prompt。

## Port 9222 被占用

此 Skill 固定使用 `9222`。让用户关闭占用程序。不要换端口。

## 当前用户 API 失败

看 diagnostics：

```text
failedPhase=current_user_api
```

优先检查：

```text
scripts/ncm_api.py
get_current_user
fetch_api_json
```

常见原因：

```text
用户未登录
页面上下文不可用
返回 code 不是 200
profile.userId 缺失
```

## 歌单列表 API 失败

看 diagnostics：

```text
failedPhase=playlist_listing_api
```

优先检查：

```text
scripts/ncm_api.py
list_created_playlists
fetch_api_json
```

确认筛选条件仍然正确：

```text
str(item.userId) == str(current userId)
item.subscribed == false
```

不要按 `specialType` 过滤用户创建歌单。

## 选择匹配多个歌单

让用户从 `--list-playlists` 的编号列表中选择一个且只能选择一个。不要采集多个主歌单。

## 主歌单 API 失败

看 diagnostics：

```text
failedPhase=primary_playlist_api
failedPhase=result_shaping
```

优先检查：

```text
fetch_primary_playlist
shape_primary_rows
```

要求 API 返回：

```text
playlist.tracks[]
playlist.trackIds[]
track.id
track.name
track.dt
```

不要过滤特殊或不可见字符标题。

## 听歌排行 API 失败

看 diagnostics：

```text
failedPhase=ranking_recent_week_api
failedPhase=ranking_all_time_api
failedPhase=result_shaping
```

优先检查：

```text
fetch_listening_record
shape_ranking_rows
```

要求 API 返回：

```text
type=1 -> weekData[]，允许空数组
type=0 -> allData[]，必须非空
row.song
row.playCount
```

## Aggregate 失败

看 diagnostics：

```text
failedPhase=aggregate
```

优先检查：

```text
scripts/ncm_aggregate.py
build_aggregate
```

aggregate 只能做统计和索引。如果新增字段，字段名要写清数量和排序口径。

## 输出质量可疑

如果 diagnostics 里出现质量 warning 或计数异常，例如：

```text
durationMsMissingRows > 0
allTimeRows = 0
```

`recentWeekRows = 0` 本身不是质量异常，只表示最近一周没有听歌记录。其他计数异常先判断是 API 返回结构变化、字段整形问题，还是账号权限/登录状态问题。修复后运行测试并重新采集。

## 修复后验证

至少运行：

```powershell
python scripts/test_ncm_profile.py
python scripts/collect_ncm_profile.py --check
```

如涉及真实客户端兼容性，再重新执行列表和采集命令。

当前 v3 已验证：

```text
NetEase Cloud Music 3.0.0 Beta 64-bit
Build 201967
Patch dd70f35
```
