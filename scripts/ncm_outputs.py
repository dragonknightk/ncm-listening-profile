from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


PRIMARY_FIELDS = ["order", "title", "artistNames", "album", "duration", "durationMs", "addedAt"]

RANKING_FIELDS = ["rank", "title", "artistNames", "playCount"]

FORBIDDEN_RAW_KEYS = {
    "creator",
    "subscribers",
    "privileges",
    "coverImgUrl",
    "recommendInfo",
    "cookies",
    "cookie",
    "token",
    "headers",
    "header",
    "postData",
    "requestBody",
}


def format_added_at(value: Any) -> str | None:
    if value in (None, "", 0):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    seconds = number / 1000 if number > 10_000_000_000 else number
    return datetime.fromtimestamp(seconds).strftime("%Y-%m-%d %H:%M:%S")


def format_duration(value: Any) -> str:
    duration_ms = _positive_int(value)
    if duration_ms is None:
        return ""
    total_seconds = duration_ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, list):
        return "|".join(str(item) for item in value if item is not None)
    return value


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field)) for field in fields})


def create_run_dirs(skill_dir: Path, timestamp: str | None = None) -> Path:
    stamp = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = skill_dir / "outputs" / stamp
    if run_dir.exists():
        raise FileExistsError(f"Output directory already exists: {run_dir}")
    (run_dir / "log").mkdir(parents=True, exist_ok=False)
    return run_dir


def ensure_data_dirs(run_dir: Path) -> None:
    for subdir in ("raw", "result", "csv", "aggregate"):
        (run_dir / subdir).mkdir(parents=True, exist_ok=False)


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _string_value(value: Any) -> str:
    return "" if value is None else str(value)


def _artist_rows(song: dict[str, Any]) -> list[dict[str, Any]]:
    artists = song.get("ar")
    if not isinstance(artists, list):
        return []
    result: list[dict[str, Any]] = []
    for artist in artists:
        if not isinstance(artist, dict):
            continue
        row: dict[str, Any] = {
            "id": _string_value(artist.get("id")),
            "name": _string_value(artist.get("name")),
        }
        if artist.get("alias"):
            row["alias"] = sanitize_raw_value(artist.get("alias"))
        if artist.get("tns"):
            row["tns"] = sanitize_raw_value(artist.get("tns"))
        result.append(row)
    return result


def _artist_names(song: dict[str, Any]) -> str:
    return "/".join(row["name"] for row in _artist_rows(song) if row.get("name"))


def _album_row(song: dict[str, Any]) -> dict[str, Any]:
    album = song.get("al")
    if not isinstance(album, dict):
        return {"id": "", "name": ""}
    result = {
        "id": _string_value(album.get("id")),
        "name": _string_value(album.get("name")),
    }
    if album.get("tns"):
        result["tns"] = sanitize_raw_value(album.get("tns"))
    return result


def sanitize_raw_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: sanitize_raw_value(child)
            for key, child in value.items()
            if key not in FORBIDDEN_RAW_KEYS and "cookie" not in key.lower() and "token" not in key.lower()
        }
    if isinstance(value, list):
        return [sanitize_raw_value(item) for item in value]
    return value


def _song_source(song: dict[str, Any]) -> dict[str, Any]:
    album = _album_row(song)
    source: dict[str, Any] = {
        "id": _string_value(song.get("id")),
        "name": _string_value(song.get("name")),
        "artistNames": _artist_names(song),
        "artists": _artist_rows(song),
        "album": album,
        "durationMs": _positive_int(song.get("dt")),
    }
    for key in (
        "alia",
        "mainTitle",
        "additionalTitle",
        "displayReason",
        "displayTags",
        "entertainmentTags",
        "awardTags",
        "pop",
        "fee",
        "mark",
        "no",
        "cd",
    ):
        if key in song and song.get(key) not in (None, "", []):
            source[key] = sanitize_raw_value(song.get(key))
    return source


def _track_id_source(track_id: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(track_id, dict):
        return None
    return sanitize_raw_value(track_id)


def _require_api_track(song: Any, dataset: str) -> dict[str, Any]:
    if not isinstance(song, dict):
        raise ValueError(f"{dataset} row is missing song object.")
    if song.get("id") in (None, ""):
        raise ValueError(f"{dataset} row is missing song id.")
    if song.get("name") is None:
        raise ValueError(f"{dataset} row is missing song name.")
    if _positive_int(song.get("dt")) is None:
        raise ValueError(f"{dataset} row is missing positive duration.")
    return song


def shape_primary_rows(playlist_detail: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    playlist = playlist_detail.get("playlist")
    if not isinstance(playlist, dict):
        raise ValueError("Playlist detail did not contain playlist.")
    tracks = playlist.get("tracks")
    track_ids = playlist.get("trackIds")
    if not isinstance(tracks, list) or not isinstance(track_ids, list) or not tracks:
        raise ValueError("Playlist detail did not contain non-empty tracks and trackIds.")
    raw_rows: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    for index, value in enumerate(tracks):
        song = _require_api_track(value, "primary_playlist")
        order = index + 1
        track_id = track_ids[index] if index < len(track_ids) and isinstance(track_ids[index], dict) else None
        duration_ms = _positive_int(song.get("dt"))
        added_at = track_id.get("at") if isinstance(track_id, dict) else None
        source = _song_source(song)
        raw_rows.append(
            {
                "dataset": "primary_playlist",
                "source": "api",
                "order": order,
                "trackId": source["id"],
                "apiTrack": source,
                "apiTrackId": _track_id_source(track_id),
            }
        )
        result_rows.append(
            {
                "order": order,
                "title": _string_value(song.get("name")),
                "artistNames": source["artistNames"],
                "album": source["album"].get("name") or "",
                "duration": format_duration(duration_ms),
                "durationMs": duration_ms,
                "addedAt": format_added_at(added_at),
            }
        )
    return raw_rows, result_rows


def shape_ranking_rows(dataset: str, api_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_rows: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    for index, row in enumerate(api_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{dataset} row is not an object.")
        song = _require_api_track(row.get("song"), dataset)
        play_count = _positive_int(row.get("playCount"))
        if play_count is None:
            raise ValueError(f"{dataset} row is missing positive playCount.")
        source = _song_source(song)
        raw_row: dict[str, Any] = {
            "dataset": dataset,
            "source": "api",
            "rank": index,
            "trackId": source["id"],
            "playCount": play_count,
            "apiSong": source,
        }
        if row.get("score") is not None:
            raw_row["score"] = row.get("score")
        raw_rows.append(raw_row)
        result_rows.append(
            {
                "rank": index,
                "title": _string_value(song.get("name")),
                "artistNames": source["artistNames"],
                "playCount": play_count,
            }
        )
    return raw_rows, result_rows


def write_run(
    run_dir: Path,
    primary_raw: list[dict[str, Any]],
    primary_result: list[dict[str, Any]],
    recent_raw: list[dict[str, Any]],
    recent_result: list[dict[str, Any]],
    all_raw: list[dict[str, Any]],
    all_result: list[dict[str, Any]],
    aggregate: dict[str, Any],
) -> dict[str, Path]:
    ensure_data_dirs(run_dir)
    paths = {
        "raw_primary": run_dir / "raw" / "primary_playlist.jsonl",
        "raw_recent": run_dir / "raw" / "ranking_recent_week.jsonl",
        "raw_all": run_dir / "raw" / "ranking_all_time.jsonl",
        "result_primary": run_dir / "result" / "primary_playlist.jsonl",
        "result_recent": run_dir / "result" / "ranking_recent_week.jsonl",
        "result_all": run_dir / "result" / "ranking_all_time.jsonl",
        "csv_primary": run_dir / "csv" / "primary_playlist.csv",
        "csv_recent": run_dir / "csv" / "ranking_recent_week.csv",
        "csv_all": run_dir / "csv" / "ranking_all_time.csv",
        "aggregate": run_dir / "aggregate" / "aggregate.json",
    }
    write_jsonl(paths["raw_primary"], primary_raw)
    write_jsonl(paths["raw_recent"], recent_raw)
    write_jsonl(paths["raw_all"], all_raw)
    write_jsonl(paths["result_primary"], primary_result)
    write_jsonl(paths["result_recent"], recent_result)
    write_jsonl(paths["result_all"], all_result)
    write_csv(paths["csv_primary"], primary_result, PRIMARY_FIELDS)
    write_csv(paths["csv_recent"], recent_result, RANKING_FIELDS)
    write_csv(paths["csv_all"], all_result, RANKING_FIELDS)
    write_json(paths["aggregate"], aggregate)
    return paths


def expected_output_files(run_dir: Path) -> set[Path]:
    return {
        run_dir / "raw" / "primary_playlist.jsonl",
        run_dir / "raw" / "ranking_recent_week.jsonl",
        run_dir / "raw" / "ranking_all_time.jsonl",
        run_dir / "result" / "primary_playlist.jsonl",
        run_dir / "result" / "ranking_recent_week.jsonl",
        run_dir / "result" / "ranking_all_time.jsonl",
        run_dir / "csv" / "primary_playlist.csv",
        run_dir / "csv" / "ranking_recent_week.csv",
        run_dir / "csv" / "ranking_all_time.csv",
        run_dir / "aggregate" / "aggregate.json",
        run_dir / "log" / "collection_diagnostics.json",
    }


def assert_only_expected_output_files(run_dir: Path) -> None:
    actual = {path for path in run_dir.rglob("*") if path.is_file()}
    expected = expected_output_files(run_dir)
    if actual != expected:
        extra = sorted(str(path) for path in actual - expected)
        missing = sorted(str(path) for path in expected - actual)
        raise AssertionError(f"Unexpected output files. Extra={extra}; Missing={missing}")


def _run_files(run_dir: Path) -> dict[str, Path]:
    return {
        "rawPrimary": run_dir / "raw" / "primary_playlist.jsonl",
        "rawRecentWeek": run_dir / "raw" / "ranking_recent_week.jsonl",
        "rawAllTime": run_dir / "raw" / "ranking_all_time.jsonl",
        "resultPrimary": run_dir / "result" / "primary_playlist.jsonl",
        "resultRecentWeek": run_dir / "result" / "ranking_recent_week.jsonl",
        "resultAllTime": run_dir / "result" / "ranking_all_time.jsonl",
        "csvPrimary": run_dir / "csv" / "primary_playlist.csv",
        "csvRecentWeek": run_dir / "csv" / "ranking_recent_week.csv",
        "csvAllTime": run_dir / "csv" / "ranking_all_time.csv",
        "aggregate": run_dir / "aggregate" / "aggregate.json",
        "diagnostics": run_dir / "log" / "collection_diagnostics.json",
    }


def describe_output_run(run_dir: Path) -> dict[str, Any]:
    files = _run_files(run_dir)
    has_raw = all(files[key].exists() for key in ("rawPrimary", "rawRecentWeek", "rawAllTime"))
    has_result = all(files[key].exists() for key in ("resultPrimary", "resultRecentWeek", "resultAllTime"))
    has_csv = all(files[key].exists() for key in ("csvPrimary", "csvRecentWeek", "csvAllTime"))
    has_aggregate = files["aggregate"].exists()
    has_log = files["diagnostics"].exists()
    if has_raw and has_result and has_csv and has_aggregate:
        status = "success"
    elif has_raw and has_result and has_csv:
        status = "legacy_success"
    elif has_log:
        status = "failed"
    else:
        status = "unknown"
    return {
        "timestamp": run_dir.name,
        "runDir": str(run_dir),
        "status": status,
        "hasRaw": has_raw,
        "hasResult": has_result,
        "hasCsv": has_csv,
        "hasAggregate": has_aggregate,
        "hasLog": has_log,
        "resultFiles": {
            "primaryPlaylist": str(files["resultPrimary"]) if files["resultPrimary"].exists() else None,
            "rankingRecentWeek": str(files["resultRecentWeek"]) if files["resultRecentWeek"].exists() else None,
            "rankingAllTime": str(files["resultAllTime"]) if files["resultAllTime"].exists() else None,
        },
        "csvFiles": {
            "primaryPlaylist": str(files["csvPrimary"]) if files["csvPrimary"].exists() else None,
            "rankingRecentWeek": str(files["csvRecentWeek"]) if files["csvRecentWeek"].exists() else None,
            "rankingAllTime": str(files["csvAllTime"]) if files["csvAllTime"].exists() else None,
        },
        "aggregateFile": str(files["aggregate"]) if files["aggregate"].exists() else None,
        "diagnosticsFile": str(files["diagnostics"]) if files["diagnostics"].exists() else None,
    }


def list_output_runs(skill_dir: Path) -> list[dict[str, Any]]:
    outputs_dir = skill_dir / "outputs"
    if not outputs_dir.exists():
        return []
    runs = [path for path in outputs_dir.iterdir() if path.is_dir()]
    return [describe_output_run(path) for path in sorted(runs, key=lambda item: item.name, reverse=True)]
