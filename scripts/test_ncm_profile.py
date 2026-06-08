from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from ncm_aggregate import build_aggregate
from ncm_api import (
    NcmApiError,
    fetch_api_json,
    fetch_listening_record,
    list_created_playlists,
    public_playlist_choices,
    resolve_playlist,
)
from ncm_env import (
    NcmClient,
    NcmProcess,
    UserActionRequired,
    assert_port_9222_available,
    client_launch_args,
    discover_client_paths,
    find_running_client_processes,
    require_unique_client,
)
from ncm_diagnostics import CollectionDiagnostics
from ncm_outputs import (
    assert_only_expected_output_files,
    create_run_dirs,
    describe_output_run,
    format_duration,
    sanitize_raw_value,
    shape_primary_rows,
    shape_ranking_rows,
    write_run,
)


class FakeCdpClient:
    def __init__(self, payloads: list[dict[str, Any]]):
        self.payloads = list(payloads)
        self.expressions: list[str] = []

    def evaluate(self, expression: str, await_promise: bool = False) -> dict[str, Any]:
        self.expressions.append(expression)
        self.assert_await_promise = await_promise
        if not self.payloads:
            raise AssertionError("No fake CDP payload queued.")
        return self.payloads.pop(0)


class FakeProc:
    def __init__(self, pid: int, name: str, exe: str | None):
        self.info = {"pid": pid, "name": name, "exe": exe}


class FakePsutil:
    class NoSuchProcess(Exception):
        pass

    class AccessDenied(Exception):
        pass

    def __init__(self, processes: list[FakeProc]):
        self.processes = processes

    def process_iter(self, attrs: list[str]) -> list[FakeProc]:
        self.attrs = attrs
        return self.processes


def api_payload(data: dict[str, Any], status: int = 200) -> dict[str, Any]:
    return {
        "ok": True,
        "status": status,
        "contentType": "application/json",
        "bodyLength": len(json.dumps(data)),
        "data": data,
        "shape": {"jsonType": "object", "topKeys": sorted(data.keys()), "arrays": []},
    }


def song(song_id: int, name: str, artists: list[str], album: str, duration_ms: int) -> dict[str, Any]:
    return {
        "id": song_id,
        "name": name,
        "ar": [{"id": index + 1000, "name": artist} for index, artist in enumerate(artists)],
        "al": {"id": song_id + 2000, "name": album},
        "dt": duration_ms,
    }


def playlist_detail_fixture() -> dict[str, Any]:
    first = song(11, "Song A", ["Artist A", "Artist B"], "Album A", 210_999)
    first["displayTags"] = [{"name": "tag", "token": "hidden", "coverImgUrl": "https://example.test/a.jpg"}]
    second = song(22, "\u2062", ["Artist C"], "Album B", 177_000)
    return {
        "playlist": {
            "tracks": [first, second],
            "trackIds": [
                {"id": 11, "at": 1_716_200_000_000, "uid": 42},
                {"id": 22, "at": None, "privileges": [{"id": 22}]},
            ],
            "creator": {"nickname": "hidden"},
            "subscribers": [{"userId": 1}],
        }
    }


def ranking_fixture() -> list[dict[str, Any]]:
    return [
        {"song": song(11, "Song A", ["Artist A"], "Album A", 210_999), "playCount": 32, "score": 98},
        {"song": song(33, "Song C", ["Artist D"], "Album C", 360_000), "playCount": 3, "score": 1},
    ]


def recent_shift_fixture() -> list[dict[str, Any]]:
    return [
        {"song": song(101, "Rise A", ["Artist A"], "Album A", 210_000), "playCount": 60},
        {"song": song(102, "Stable B", ["Artist B"], "Album B", 220_000), "playCount": 50},
        {"song": song(201, "Recent Only 1", ["Artist R"], "Album R", 230_000), "playCount": 40},
        {"song": song(202, "Recent Only 2", ["Artist R"], "Album R", 240_000), "playCount": 30},
        {"song": song(203, "Recent Only 3", ["Artist R"], "Album R", 250_000), "playCount": 20},
        {"song": song(103, "Drop C", ["Artist C"], "Album C", 260_000), "playCount": 10},
    ]


def all_time_shift_fixture() -> list[dict[str, Any]]:
    return [
        {"song": song(103, "Drop C", ["Artist C"], "Album C", 260_000), "playCount": 300},
        {"song": song(102, "Stable B", ["Artist B"], "Album B", 220_000), "playCount": 250},
        {"song": song(301, "All Only 1", ["Artist L"], "Album L", 230_000), "playCount": 200},
        {"song": song(302, "All Only 2", ["Artist L"], "Album L", 240_000), "playCount": 150},
        {"song": song(101, "Rise A", ["Artist A"], "Album A", 210_000), "playCount": 100},
    ]


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


class NcmProfileV3Tests(unittest.TestCase):
    def test_windows_client_discovery_launch_args_and_process_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exe = Path(temp_dir) / "CloudMusic" / "cloudmusic.exe"
            exe.parent.mkdir()
            exe.write_text("", encoding="utf-8")

            with (
                patch("sys.platform", "win32"),
                patch.dict("os.environ", {"NCM_CLIENT_PATH": str(exe)}, clear=False),
                patch("ncm_env._windows_candidate_from_registry", return_value=[]),
                patch("ncm_env._windows_common_candidates", return_value=[]),
            ):
                paths = discover_client_paths()
                self.assertEqual(paths, [exe.resolve()])
                client = require_unique_client()
                self.assertEqual(client.platform, "windows")
                self.assertEqual(client.kind, "windows_exe")
                self.assertEqual(
                    client_launch_args(client, 9222),
                    [
                        str(exe.resolve()),
                        "--force-renderer-accessibility=complete",
                        "--remote-debugging-port=9222",
                    ],
                )

            fake_psutil = FakePsutil(
                [
                    FakeProc(101, "cloudmusic.exe", str(exe)),
                    FakeProc(102, "notepad.exe", r"C:\Windows\notepad.exe"),
                ]
            )
            with patch("sys.platform", "win32"), patch("ncm_env._load_psutil", return_value=fake_psutil):
                running = find_running_client_processes()
            self.assertEqual(running, [NcmProcess(pid=101, name="cloudmusic.exe", exe=str(exe))])

    def test_macos_client_discovery_launch_args_and_process_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = Path(temp_dir) / "NeteaseMusic.app"
            app.mkdir()

            with (
                patch("sys.platform", "darwin"),
                patch.dict("os.environ", {}, clear=True),
                patch("ncm_env._macos_common_candidates", return_value=[app]),
            ):
                paths = discover_client_paths()
                self.assertEqual(paths, [app.resolve()])
                client = require_unique_client()
                self.assertEqual(client.platform, "macos")
                self.assertEqual(client.kind, "macos_app")
                self.assertEqual(
                    client_launch_args(client, 9222),
                    [
                        "open",
                        "-na",
                        str(app.resolve()),
                        "--args",
                        "--force-renderer-accessibility=complete",
                        "--remote-debugging-port=9222",
                    ],
                )

            fake_psutil = FakePsutil(
                [
                    FakeProc(201, "NeteaseMusic", str(app / "Contents" / "MacOS" / "NeteaseMusic")),
                    FakeProc(202, "NeteaseMusic Helper (Renderer)", str(app / "Contents" / "Frameworks" / "NeteaseMusic Helper.app")),
                    FakeProc(203, "Music", "/Applications/Music.app/Contents/MacOS/Music"),
                ]
            )
            with patch("sys.platform", "darwin"), patch("ncm_env._load_psutil", return_value=fake_psutil):
                running = find_running_client_processes()
            self.assertEqual([proc.pid for proc in running], [201, 202])

    def test_client_path_validation_unsupported_platform_and_port_conflict_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid = Path(temp_dir) / "NeteaseMusic.app"
            invalid.write_text("not a directory", encoding="utf-8")

            with patch("sys.platform", "darwin"):
                self.assertEqual(discover_client_paths(str(invalid)), [])
                with self.assertRaises(UserActionRequired) as missing:
                    require_unique_client(str(invalid))
                self.assertIn("--client-path", str(missing.exception))

            with patch("sys.platform", "linux"):
                with self.assertRaises(UserActionRequired) as unsupported:
                    require_unique_client()
                self.assertIn("Windows and macOS", str(unsupported.exception))

            with patch("ncm_env.port_is_open", return_value=True), patch("ncm_env.describe_port_owner", return_value="other app (pid 9)"):
                with self.assertRaises(UserActionRequired) as occupied:
                    assert_port_9222_available(9222)
                self.assertIn("Port 9222 is occupied by other app (pid 9)", str(occupied.exception))

    def test_fetch_api_json_uses_page_context_payload_and_rejects_unsafe_status(self) -> None:
        client = FakeCdpClient([api_payload({"code": 200, "ok": True})])

        result = fetch_api_json(client, "/api/nuser/account/get")

        self.assertEqual(result.data["code"], 200)
        self.assertTrue(client.expressions)
        self.assertIn("fetch(url", client.expressions[0])
        self.assertIn("credentials: 'include'", client.expressions[0])

        blocked = FakeCdpClient([api_payload({"code": 200}, status=429)])
        with self.assertRaises(NcmApiError) as raised:
            fetch_api_json(blocked, "/api/user/playlist", {"uid": "42"})
        self.assertEqual(raised.exception.details["status"], 429)

    def test_fetch_listening_record_allows_empty_recent_week_but_rejects_empty_all_time(self) -> None:
        recent_client = FakeCdpClient([api_payload({"code": 200, "weekData": []})])

        recent_rows, recent_summary = fetch_listening_record(recent_client, "42", "recent_week")

        self.assertEqual(recent_rows, [])
        self.assertEqual(recent_summary["rowsFound"], 0)
        self.assertEqual(recent_summary["recordType"], 1)

        all_time_client = FakeCdpClient([api_payload({"code": 200, "allData": []})])
        with self.assertRaises(NcmApiError):
            fetch_listening_record(all_time_client, "42", "all_time")

    def test_list_created_playlists_filters_current_user_and_keeps_special_types(self) -> None:
        client = FakeCdpClient(
            [
                api_payload(
                    {
                        "code": 200,
                        "playlist": [
                            {"id": 1, "name": "主歌单", "userId": 42, "subscribed": False, "trackCount": 2, "playCount": 9, "specialType": 0},
                            {"id": 2, "name": "特别歌单", "userId": "42", "subscribed": False, "trackCount": 3, "playCount": 10, "specialType": 100},
                            {"id": 3, "name": "收藏歌单", "userId": 42, "subscribed": True, "trackCount": 4},
                            {"id": 4, "name": "别人歌单", "userId": 7, "subscribed": False, "trackCount": 5},
                        ],
                    }
                )
            ]
        )

        playlists, summary = list_created_playlists(client, "42")

        self.assertEqual([item["name"] for item in playlists], ["主歌单", "特别歌单"])
        self.assertEqual(playlists[1]["specialType"], 100)
        self.assertEqual(summary["allPlaylistRows"], 4)
        self.assertEqual(summary["createdPlaylistRows"], 2)
        self.assertEqual(resolve_playlist(playlists, None, 2)["name"], "特别歌单")

    def test_public_playlist_choices_excludes_internal_fields(self) -> None:
        playlists = [
            {
                "index": 1,
                "name": "主歌单",
                "playlistId": "hidden",
                "trackCount": 2,
                "playCount": 9,
                "specialType": 100,
                "privacy": 0,
                "updateTime": 1_716_200_000_000,
                "source": "api",
            }
        ]

        public = public_playlist_choices(playlists)

        self.assertEqual(public, [{"index": 1, "name": "主歌单", "trackCount": 2}])
        self.assertFalse({"playlistId", "playCount", "specialType", "privacy", "updateTime", "source"} & set(public[0]))

    def test_resolve_playlist_accepts_public_index(self) -> None:
        playlists = [
            {"index": 1, "name": "主歌单", "playlistId": "1", "trackCount": 2},
            {"index": 2, "name": "特别歌单", "playlistId": "2", "trackCount": 3},
        ]

        self.assertEqual(resolve_playlist(playlists, None, 2)["playlistId"], "2")

    def test_skill_keeps_complete_prompt_suitability_text(self) -> None:
        skill_md = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
        prompt_aggregate_line = "<run_dir>\\aggregate\\aggregate.json，这是从上面数据预先算出的统计和索引，用来快速定位趋势、极端值、重合项和样本；完整事实仍以上面三份 result 为准。"

        self.assertIn(
            "适合已经很熟悉和 AI 对话的人，也适合你想保留一点未知感和神秘感的时候。它不给AI太多方向，只把数据交出去，让对方自己靠近、观察和理解你。适合期待更自由、更意外、更像一次重新相识的分析。",
            skill_md,
        )
        self.assertIn(
            "适合你希望被认真看见的时候。它会引导AI慢下来，从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解你，而不是只给出一份音乐品味总结。适合想要更稳定、更细腻、更有温度回答的场景。",
            skill_md,
        )
        self.assertEqual(skill_md.count(prompt_aggregate_line), 2)

        minimal_prompt = skill_md.split("## 极简版 Prompt", 1)[1].split("## 引导版 Prompt", 1)[0]
        guided_prompt = skill_md.split("## 引导版 Prompt", 1)[1].split("## 运行规则", 1)[0]
        for prompt in (minimal_prompt, guided_prompt):
            aggregate_index = prompt.index("<run_dir>\\aggregate\\aggregate.json")
            self.assertLess(prompt.index("<run_dir>\\result\\primary_playlist.jsonl"), aggregate_index)
            self.assertLess(prompt.index("<run_dir>\\result\\ranking_all_time.jsonl"), aggregate_index)
            self.assertLess(prompt.index("<run_dir>\\result\\ranking_recent_week.jsonl"), aggregate_index)

    def test_readme_opens_with_concrete_user_owned_framing(self) -> None:
        readme = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "你的网易云里藏着一份很长的自我备忘录：主歌单里留下的歌，最近一周反复回来的歌，所有时间里一直没有退场的歌。",
            readme,
        )
        self.assertIn(
            "`ncm-listening-profile` 会采集你确认的主歌单、最近一周听歌排行和所有时间听歌排行，生成本地数据文件和可复制给 AI 的分析 prompt。",
            readme,
        )
        self.assertIn("它把材料放到你手里，也把解释权留给你。最终要不要分析、交给谁分析、分享哪些文件，都由你决定。", readme)

    def test_primary_and_ranking_rows_are_shaped_from_api_without_extra_result_fields(self) -> None:
        primary_raw, primary_result = shape_primary_rows(playlist_detail_fixture())
        recent_raw, recent_result = shape_ranking_rows("ranking_recent_week", ranking_fixture())

        self.assertEqual(primary_raw[0]["source"], "api")
        self.assertEqual(primary_result[0]["duration"], "03:30")
        self.assertEqual(primary_result[0]["durationMs"], 210_999)
        self.assertRegex(primary_result[0]["addedAt"], r"^\d{4}-\d{2}-\d{2} ")
        self.assertEqual(primary_result[1]["title"], "\u2062")
        self.assertIsNone(primary_result[1]["addedAt"])
        self.assertEqual(
            set(primary_result[0]),
            {"order", "title", "artistNames", "album", "duration", "durationMs", "addedAt"},
        )

        self.assertEqual(recent_raw[0]["source"], "api")
        self.assertEqual(recent_raw[0]["score"], 98)
        self.assertEqual(recent_result[0], {"rank": 1, "title": "Song A", "artistNames": "Artist A", "playCount": 32})
        self.assertEqual(set(recent_result[0]), {"rank", "title", "artistNames", "playCount"})

    def test_raw_sanitizer_excludes_forbidden_fields(self) -> None:
        forbidden = {
            "creator",
            "subscribers",
            "privileges",
            "coverImgUrl",
            "recommendInfo",
            "cookies",
            "token",
            "headers",
            "postData",
            "requestBody",
        }
        raw_rows, _ = shape_primary_rows(playlist_detail_fixture())
        cleaned = sanitize_raw_value(
            {
                "safe": raw_rows,
                "creator": {"nickname": "hidden"},
                "headers": {"x": "hidden"},
                "nested": {"token": "hidden", "keep": True},
            }
        )

        self.assertFalse(forbidden & walk_keys(cleaned))

    def test_write_run_creates_expected_files_and_no_playlist_list_raw(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir)
            run_dir = create_run_dirs(skill_dir, "20260604-120000")
            CollectionDiagnostics(run_dir, skill_dir, 9222).phase_ok("validation")
            primary_raw, primary_result = shape_primary_rows(playlist_detail_fixture())
            recent_raw, recent_result = shape_ranking_rows("ranking_recent_week", ranking_fixture())
            all_raw, all_result = shape_ranking_rows("ranking_all_time", ranking_fixture())
            aggregate = build_aggregate(primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result)

            write_run(run_dir, primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result, aggregate)

            assert_only_expected_output_files(run_dir)
            self.assertFalse((run_dir / "raw" / "user_playlists.jsonl").exists())
            self.assertEqual(describe_output_run(run_dir)["status"], "success")
            self.assertTrue(describe_output_run(run_dir)["hasAggregate"])
            with (run_dir / "csv" / "primary_playlist.csv").open("r", encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(list(row), ["order", "title", "artistNames", "album", "duration", "durationMs", "addedAt"])
            with (run_dir / "aggregate" / "aggregate.json").open("r", encoding="utf-8") as handle:
                self.assertEqual(json.load(handle)["counts"]["primaryPlaylistRows"], 2)

    def test_empty_recent_week_run_writes_outputs_diagnostics_and_zero_aggregate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir)
            run_dir = create_run_dirs(skill_dir, "20260604-120000")
            diagnostics = CollectionDiagnostics(run_dir, skill_dir, 9222)
            primary_raw, primary_result = shape_primary_rows(playlist_detail_fixture())
            recent_raw, recent_result = shape_ranking_rows("ranking_recent_week", [])
            all_raw, all_result = shape_ranking_rows("ranking_all_time", ranking_fixture())
            diagnostics.phase_ok(
                "result_shaping",
                primaryRows=len(primary_result),
                recentWeekRows=len(recent_result),
                allTimeRows=len(all_result),
                recentWeekPlayCountRows=0,
                recentWeekPlayCountMissingRows=0,
            )
            aggregate = build_aggregate(primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result)
            diagnostics.phase_ok("aggregate", aggregateSchemaVersion=aggregate.get("schemaVersion"))

            write_run(run_dir, primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result, aggregate)
            diagnostics.set_quality(primaryRows=len(primary_result), recentWeekRows=0, allTimeRows=len(all_result), collectionSource="api")
            diagnostics.phase_ok("validation")

            assert_only_expected_output_files(run_dir)
            self.assertEqual((run_dir / "raw" / "ranking_recent_week.jsonl").read_text(encoding="utf-8"), "")
            self.assertEqual((run_dir / "result" / "ranking_recent_week.jsonl").read_text(encoding="utf-8"), "")
            with (run_dir / "csv" / "ranking_recent_week.csv").open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, ["rank", "title", "artistNames", "playCount"])
                self.assertEqual(list(reader), [])

            self.assertEqual(aggregate["counts"]["rankingRecentWeekRows"], 0)
            self.assertEqual(aggregate["rankingStats"]["recentWeekTotalPlayCount"], 0)
            self.assertEqual(aggregate["rankingStats"]["recentWeekTop1PlayCountShare"], 0)
            self.assertEqual(aggregate["rankingStats"]["recentWeekTop3PlayCountShare"], 0)
            self.assertEqual(aggregate["rankingStats"]["recentWeekTop10PlayCountShare"], 0)
            self.assertEqual(aggregate["rankingStats"]["top20RecentWeekTracksByPlayCount"], [])
            self.assertEqual(aggregate["rankingStats"]["bottom20RecentWeekTracksByPlayCount"], [])
            stats = aggregate["recentLongTermShiftStats"]
            self.assertEqual(stats["recentWeekTop20TracksInAllTimeTop100Count"], 0)
            self.assertEqual(stats["recentWeekTop20TracksInAllTimeTop100Share"], 0)
            self.assertEqual(stats["allTimeTop20TracksInRecentWeekTop100Count"], 0)
            self.assertEqual(stats["allTimeTop20TracksInRecentWeekTop100Share"], 0)
            self.assertIsNone(stats["recentWeekAllTimeOverlapMedianAbsoluteRankDelta"])
            self.assertEqual(stats["top10RecentWeekAllTimeOverlapByRankRise"], [])
            self.assertEqual(stats["top10RecentWeekAllTimeOverlapByRankDrop"], [])

            diagnostics_data = json.loads((run_dir / "log" / "collection_diagnostics.json").read_text(encoding="utf-8"))
            self.assertEqual(diagnostics_data["quality"]["recentWeekRows"], 0)
            self.assertNotIn("failedPhase", diagnostics_data)
            self.assertNotEqual(diagnostics_data["phases"].get("ranking_recent_week_api", {}).get("status"), "failed")

    def test_aggregate_contains_neutral_metrics_and_explicit_index_names(self) -> None:
        primary_raw, primary_result = shape_primary_rows(playlist_detail_fixture())
        recent_raw, recent_result = shape_ranking_rows("ranking_recent_week", ranking_fixture())
        all_raw, all_result = shape_ranking_rows("ranking_all_time", ranking_fixture())

        aggregate = build_aggregate(primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result)

        self.assertEqual(aggregate["schemaVersion"], 1)
        self.assertEqual(aggregate["counts"]["rankingRecentWeekRows"], 2)
        self.assertEqual(aggregate["durationStats"]["primaryDurationBuckets"]["shortLt3m"]["count"], 1)
        self.assertEqual(aggregate["durationStats"]["primaryDurationBuckets"]["medium3To5m"]["count"], 1)
        self.assertAlmostEqual(aggregate["rankingStats"]["recentWeekTop1PlayCountShare"], 32 / 35, places=4)
        self.assertEqual(aggregate["overlapStats"]["allThreeCount"], 1)
        self.assertIn("top30ArtistsByPrimaryTrackCount", aggregate["artistStats"])
        self.assertIn("bottom20RecentWeekTracksByPlayCount", aggregate["rankingStats"])
        self.assertIn("top50PrimaryRecentWeekOverlapByRecentWeekPlayCount", aggregate["overlapStats"])
        self.assertIn("recentLongTermShiftStats", aggregate)
        serialized = json.dumps(aggregate, ensure_ascii=False)
        self.assertNotIn("evidenceStrength", serialized)
        self.assertNotIn("profileConclusion", serialized)

    def test_recent_long_term_shift_stats_cover_overlap_share_and_rank_delta_samples(self) -> None:
        primary_raw, primary_result = shape_primary_rows(playlist_detail_fixture())
        recent_raw, recent_result = shape_ranking_rows("ranking_recent_week", recent_shift_fixture())
        all_raw, all_result = shape_ranking_rows("ranking_all_time", all_time_shift_fixture())

        aggregate = build_aggregate(primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result)
        stats = aggregate["recentLongTermShiftStats"]

        self.assertEqual(stats["recentWeekTop20TracksInAllTimeTop100Count"], 3)
        self.assertAlmostEqual(stats["recentWeekTop20TracksInAllTimeTop100Share"], 0.5)
        self.assertEqual(stats["allTimeTop20TracksInRecentWeekTop100Count"], 3)
        self.assertAlmostEqual(stats["allTimeTop20TracksInRecentWeekTop100Share"], 0.6)
        self.assertEqual(stats["recentWeekAllTimeOverlapMedianAbsoluteRankDelta"], 4)

        rise = stats["top10RecentWeekAllTimeOverlapByRankRise"][0]
        self.assertEqual(
            {key: rise[key] for key in ("title", "artistNames", "recentWeekRank", "allTimeRank", "rankDelta", "recentWeekPlayCount", "allTimePlayCount")},
            {
                "title": "Rise A",
                "artistNames": "Artist A",
                "recentWeekRank": 1,
                "allTimeRank": 5,
                "rankDelta": 4,
                "recentWeekPlayCount": 60,
                "allTimePlayCount": 100,
            },
        )

        drop = stats["top10RecentWeekAllTimeOverlapByRankDrop"][0]
        self.assertEqual(
            {key: drop[key] for key in ("title", "artistNames", "recentWeekRank", "allTimeRank", "rankDelta", "recentWeekPlayCount", "allTimePlayCount")},
            {
                "title": "Drop C",
                "artistNames": "Artist C",
                "recentWeekRank": 6,
                "allTimeRank": 1,
                "rankDelta": 5,
                "recentWeekPlayCount": 10,
                "allTimePlayCount": 300,
            },
        )

    def test_diagnostics_records_api_failure_without_sensitive_details(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir)
            run_dir = create_run_dirs(skill_dir, "20260604-120000")
            diagnostics = CollectionDiagnostics(run_dir, skill_dir, 9222)
            diagnostics.phase_fail(
                "current_user_api",
                NcmApiError(
                    "API returned unsafe status 403",
                    {"apiPath": "/api/nuser/account/get", "status": 403, "headers": {"cookie": "hidden"}, "requestBody": "hidden"},
                ),
            )

            data = json.loads((run_dir / "log" / "collection_diagnostics.json").read_text(encoding="utf-8"))
            self.assertEqual(data["schemaVersion"], 3)
            self.assertEqual(data["skillVersion"], "ncm-listening-profile-v6")
            self.assertIn("verifiedEnvironments", data)
            self.assertNotIn("verifiedClient", data)
            self.assertEqual(data["failedPhase"], "current_user_api")
            self.assertEqual(data["errorDetails"]["status"], 403)
            self.assertFalse({"headers", "cookie", "requestBody", "token"} & walk_keys(data))
            self.assertIn("ncm_api.py", " ".join(data["repairHints"][0]["read"]))

    def test_diagnostics_records_platform_neutral_client_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir)
            run_dir = create_run_dirs(skill_dir, "20260604-120000")
            diagnostics = CollectionDiagnostics(run_dir, skill_dir, 9222)
            diagnostics.set_environment(clientPath="/Applications/NeteaseMusic.app", clientPlatform="macos", clientKind="macos_app")

            data = json.loads((run_dir / "log" / "collection_diagnostics.json").read_text(encoding="utf-8"))
            self.assertEqual(data["environment"]["clientPath"], "/Applications/NeteaseMusic.app")
            self.assertEqual(data["environment"]["clientPlatform"], "macos")
            self.assertEqual(data["environment"]["clientKind"], "macos_app")
            self.assertNotIn("cloudmusicExe", data["environment"])

    def test_runtime_scripts_do_not_keep_legacy_collection_tokens(self) -> None:
        scripts_dir = Path(__file__).resolve().parent
        runtime_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in scripts_dir.glob("*.py")
            if path.name not in {"test_ncm_profile.py"}
        )
        legacy_tokens = [
            "D" + "OM",
            "d" + "om",
            "sel" + "ector",
            "playing" + "List",
            "cache" + "Status",
            "ncm_" + "cache",
            "collect_created_play" + "lists",
            "open_play" + "list",
            "collect_primary_play" + "list_rows",
            "collect_rank" + "ing_rows",
        ]
        for token in legacy_tokens:
            self.assertNotIn(token, runtime_text)

    def test_format_duration_uses_api_milliseconds(self) -> None:
        self.assertEqual(format_duration(238_000), "03:58")
        self.assertEqual(format_duration(3_723_000), "1:02:03")
        self.assertEqual(format_duration(None), "")

    def test_timestamp_collision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            create_run_dirs(Path(temp_dir), "20260604-120000")
            with self.assertRaises(FileExistsError):
                create_run_dirs(Path(temp_dir), "20260604-120000")


if __name__ == "__main__":
    unittest.main()
