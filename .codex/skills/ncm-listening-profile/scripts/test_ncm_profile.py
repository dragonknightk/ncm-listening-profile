from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from ncm_aggregate import build_aggregate
from ncm_api import NcmApiError, fetch_api_json, list_created_playlists, public_playlist_choices, resolve_playlist
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

        self.assertIn(
            "适合已经很熟悉和 AI 对话的人，也适合你想保留一点未知感和神秘感的时候。它不给AI太多方向，只把数据交出去，让对方自己靠近、观察和理解你。适合期待更自由、更意外、更像一次重新相识的分析。",
            skill_md,
        )
        self.assertIn(
            "适合你希望被认真看见的时候。它会引导AI慢下来，从长期偏好、近期状态、审美意象、生活节奏和细小异常里理解你，而不是只给出一份音乐品味总结。适合想要更稳定、更细腻、更有温度回答的场景。",
            skill_md,
        )

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
        serialized = json.dumps(aggregate, ensure_ascii=False)
        self.assertNotIn("evidenceStrength", serialized)
        self.assertNotIn("profileConclusion", serialized)

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
            self.assertEqual(data["schemaVersion"], 2)
            self.assertEqual(data["skillVersion"], "ncm-listening-profile-v3")
            self.assertEqual(data["failedPhase"], "current_user_api")
            self.assertEqual(data["errorDetails"]["status"], 403)
            self.assertFalse({"headers", "cookie", "requestBody", "token"} & walk_keys(data))
            self.assertIn("ncm_api.py", " ".join(data["repairHints"][0]["read"]))

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
