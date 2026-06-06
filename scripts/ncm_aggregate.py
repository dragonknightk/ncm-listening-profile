from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean, median
from typing import Any


def _round_share(value: float) -> float:
    return round(value, 4)


def _sample_primary(row: dict[str, Any], raw: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "order": row.get("order"),
        "title": row.get("title"),
        "artistNames": row.get("artistNames"),
        "album": row.get("album"),
        "duration": row.get("duration"),
        "durationMs": row.get("durationMs"),
        "addedAt": row.get("addedAt"),
    }
    if raw and raw.get("trackId") is not None:
        result["trackId"] = raw.get("trackId")
    return result


def _sample_ranking(row: dict[str, Any], raw: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "rank": row.get("rank"),
        "title": row.get("title"),
        "artistNames": row.get("artistNames"),
        "playCount": row.get("playCount"),
    }
    if raw and raw.get("trackId") is not None:
        result["trackId"] = raw.get("trackId")
    api_song = raw.get("apiSong") if raw else None
    album = api_song.get("album") if isinstance(api_song, dict) else None
    if isinstance(album, dict) and album.get("name"):
        result["album"] = album.get("name")
    return result


def _track_key(row: dict[str, Any], raw: dict[str, Any] | None) -> str:
    if raw and raw.get("trackId") not in (None, ""):
        return f"id:{raw.get('trackId')}"
    return f"titleArtist:{str(row.get('title') or '').casefold()}::{str(row.get('artistNames') or '').casefold()}"


def _parse_added_at(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _duration_bucket(ms: int) -> str:
    if ms < 180_000:
        return "shortLt3m"
    if ms <= 300_000:
        return "medium3To5m"
    return "longGt5m"


def _bucket_counts(values: list[str], total: int) -> dict[str, dict[str, float | int]]:
    counts = Counter(values)
    return {
        key: {"count": counts.get(key, 0), "share": _round_share(counts.get(key, 0) / total) if total else 0}
        for key in ("shortLt3m", "medium3To5m", "longGt5m")
    }


def _top_counts(counter: Counter[str], limit: int) -> list[dict[str, Any]]:
    return [{"value": key, "count": count} for key, count in counter.most_common(limit)]


def _top_play_counts(counter: Counter[str], limit: int) -> list[dict[str, Any]]:
    return [{"value": key, "playCount": count} for key, count in counter.most_common(limit)]


def _split_names(value: Any) -> list[str]:
    return [part.strip() for part in str(value or "").split("/") if part.strip()]


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'_-]*|\d+|[\u4e00-\u9fff]+|[\u3040-\u30ff]+")


def _terms(value: Any) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(str(value or ""))]


def _char_stats(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    char_counts = Counter()
    track_counts = Counter()
    symbol_heavy = 0
    for row in rows:
        text = str(row.get(field) or "")
        seen: set[str] = set()
        symbols = 0
        meaningful = 0
        for ch in text:
            if ch.isspace():
                continue
            meaningful += 1
            code = ord(ch)
            if "\u4e00" <= ch <= "\u9fff":
                kind = "cjk"
            elif "\u3040" <= ch <= "\u30ff":
                kind = "kana"
            elif ch.isascii() and ch.isalpha():
                kind = "ascii"
            elif ch.isdigit():
                kind = "digit"
            elif ch.isalnum():
                kind = "otherLetter"
            else:
                kind = "symbol"
                symbols += 1
            char_counts[kind] += 1
            seen.add(kind)
        for kind in seen:
            track_counts[kind] += 1
        if meaningful and symbols / meaningful >= 0.5:
            symbol_heavy += 1
    return {
        "characterCounts": dict(sorted(char_counts.items())),
        "trackCounts": dict(sorted(track_counts.items())),
        "symbolHeavyTrackCount": symbol_heavy,
    }


def _ranking_concentration(rows: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    play_counts = [int(row.get("playCount") or 0) for row in rows]
    total = sum(play_counts)

    def share(top_n: int) -> float:
        return _round_share(sum(play_counts[:top_n]) / total) if total else 0

    return {
        f"{prefix}TotalPlayCount": total,
        f"{prefix}Top1PlayCountShare": share(1),
        f"{prefix}Top3PlayCountShare": share(3),
        f"{prefix}Top10PlayCountShare": share(10),
    }


def _counter_samples(counter: Counter[str], sample_map: dict[str, dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    rows = []
    for value, count in counter.items():
        if count == 1:
            rows.append({"value": value, "sample": sample_map[value]})
    return rows[:limit]


def _rank_shift_sample(recent: dict[str, Any], all_time: dict[str, Any], rank_delta: int) -> dict[str, Any]:
    result = {
        "title": recent.get("title") or all_time.get("title"),
        "artistNames": recent.get("artistNames") or all_time.get("artistNames"),
        "recentWeekRank": recent.get("rank"),
        "allTimeRank": all_time.get("rank"),
        "rankDelta": rank_delta,
        "recentWeekPlayCount": recent.get("playCount"),
        "allTimePlayCount": all_time.get("playCount"),
    }
    track_id = recent.get("trackId") or all_time.get("trackId")
    if track_id is not None:
        result["trackId"] = track_id
    return result


def _rank_shift_samples(recent_keyed: dict[str, dict[str, Any]], all_keyed: dict[str, dict[str, Any]], mode: str, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in recent_keyed.keys() & all_keyed.keys():
        recent = recent_keyed[key]
        all_time = all_keyed[key]
        recent_rank = int(recent.get("rank") or 0)
        all_time_rank = int(all_time.get("rank") or 0)
        if not recent_rank or not all_time_rank:
            continue
        if mode == "rise":
            rank_delta = all_time_rank - recent_rank
        elif mode == "drop":
            rank_delta = recent_rank - all_time_rank
        else:
            raise ValueError(f"Unsupported rank shift mode: {mode}")
        if rank_delta <= 0:
            continue
        rows.append(_rank_shift_sample(recent, all_time, rank_delta))
    return sorted(rows, key=lambda item: (-int(item["rankDelta"]), int(item["recentWeekRank"] or 0), int(item["allTimeRank"] or 0)))[:limit]


def build_aggregate(
    primary_raw: list[dict[str, Any]],
    primary_result: list[dict[str, Any]],
    recent_raw: list[dict[str, Any]],
    recent_result: list[dict[str, Any]],
    all_raw: list[dict[str, Any]],
    all_result: list[dict[str, Any]],
) -> dict[str, Any]:
    primary_samples = [_sample_primary(row, primary_raw[index] if index < len(primary_raw) else None) for index, row in enumerate(primary_result)]
    recent_samples = [_sample_ranking(row, recent_raw[index] if index < len(recent_raw) else None) for index, row in enumerate(recent_result)]
    all_samples = [_sample_ranking(row, all_raw[index] if index < len(all_raw) else None) for index, row in enumerate(all_result)]

    durations = [int(row["durationMs"]) for row in primary_result if isinstance(row.get("durationMs"), int)]
    duration_buckets = [_duration_bucket(value) for value in durations]
    added_pairs = [(row, raw, _parse_added_at(row.get("addedAt"))) for row, raw in zip(primary_result, primary_raw)]
    added_pairs = [(row, raw, dt) for row, raw, dt in added_pairs if dt is not None]

    by_year = Counter(dt.strftime("%Y") for _, _, dt in added_pairs)
    by_year_month = Counter(dt.strftime("%Y-%m") for _, _, dt in added_pairs)
    by_month = Counter(dt.strftime("%m") for _, _, dt in added_pairs)
    by_hour = Counter(dt.strftime("%H") for _, _, dt in added_pairs)
    by_weekday = Counter(str(dt.weekday()) for _, _, dt in added_pairs)

    primary_keyed = {_track_key(row, primary_raw[index] if index < len(primary_raw) else None): primary_samples[index] for index, row in enumerate(primary_result)}
    recent_keyed = {_track_key(row, recent_raw[index] if index < len(recent_raw) else None): recent_samples[index] for index, row in enumerate(recent_result)}
    all_keyed = {_track_key(row, all_raw[index] if index < len(all_raw) else None): all_samples[index] for index, row in enumerate(all_result)}
    recent_keys_by_rank = [_track_key(row, recent_raw[index] if index < len(recent_raw) else None) for index, row in enumerate(recent_result)]
    all_keys_by_rank = [_track_key(row, all_raw[index] if index < len(all_raw) else None) for index, row in enumerate(all_result)]
    primary_keys = set(primary_keyed)
    recent_keys = set(recent_keyed)
    all_keys = set(all_keyed)
    match_method = "trackId" if all(key.startswith("id:") for key in primary_keys | recent_keys | all_keys) else "titleArtist"

    def overlap_rows(keys: set[str], sort_source: dict[str, dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        rows = [sort_source[key] for key in keys if key in sort_source]
        return sorted(rows, key=lambda item: int(item.get("playCount") or 0), reverse=True)[:limit]

    artist_primary = Counter()
    artist_recent_play = Counter()
    artist_all_play = Counter()
    artist_all_appearance = Counter()
    artist_sample: dict[str, dict[str, Any]] = {}
    for sample in primary_samples:
        for artist in _split_names(sample.get("artistNames")):
            artist_primary[artist] += 1
            artist_all_appearance[artist] += 1
            artist_sample.setdefault(artist, sample)
    for sample in recent_samples:
        for artist in _split_names(sample.get("artistNames")):
            artist_recent_play[artist] += int(sample.get("playCount") or 0)
            artist_all_appearance[artist] += 1
    for sample in all_samples:
        for artist in _split_names(sample.get("artistNames")):
            artist_all_play[artist] += int(sample.get("playCount") or 0)
            artist_all_appearance[artist] += 1

    album_primary = Counter(str(sample.get("album") or "") for sample in primary_samples if sample.get("album"))
    album_recent_play = Counter()
    album_all_play = Counter()
    album_sample: dict[str, dict[str, Any]] = {}
    for sample in recent_samples:
        album = sample.get("album")
        if album:
            album_recent_play[str(album)] += int(sample.get("playCount") or 0)
    for sample in all_samples:
        album = sample.get("album")
        if album:
            album_all_play[str(album)] += int(sample.get("playCount") or 0)
    for sample in primary_samples:
        album = str(sample.get("album") or "")
        if album:
            album_sample.setdefault(album, sample)

    title_terms = Counter(term for row in primary_result for term in _terms(row.get("title")))
    album_terms = Counter(term for row in primary_result for term in _terms(row.get("album")))
    artist_terms = Counter(term for row in primary_result for term in _terms(row.get("artistNames")))

    recent_only = recent_keys - primary_keys - all_keys
    all_only = all_keys - primary_keys - recent_keys
    primary_not_ranked = primary_keys - recent_keys - all_keys
    all_three = primary_keys & recent_keys & all_keys
    recent_top20_keys = set(recent_keys_by_rank[:20])
    recent_top100_keys = set(recent_keys_by_rank[:100])
    all_top20_keys = set(all_keys_by_rank[:20])
    all_top100_keys = set(all_keys_by_rank[:100])
    rank_delta_values = [
        abs(int(recent_keyed[key].get("rank") or 0) - int(all_keyed[key].get("rank") or 0))
        for key in recent_keys & all_keys
        if int(recent_keyed[key].get("rank") or 0) and int(all_keyed[key].get("rank") or 0)
    ]

    return {
        "schemaVersion": 1,
        "sources": {
            "resultPrimaryPlaylist": "result/primary_playlist.jsonl",
            "resultRankingRecentWeek": "result/ranking_recent_week.jsonl",
            "resultRankingAllTime": "result/ranking_all_time.jsonl",
            "rawPrimaryPlaylist": "raw/primary_playlist.jsonl",
            "rawRankingRecentWeek": "raw/ranking_recent_week.jsonl",
            "rawRankingAllTime": "raw/ranking_all_time.jsonl",
        },
        "counts": {
            "primaryPlaylistRows": len(primary_result),
            "rankingRecentWeekRows": len(recent_result),
            "rankingAllTimeRows": len(all_result),
        },
        "durationStats": {
            "primaryAverageDurationMs": round(mean(durations), 2) if durations else None,
            "primaryMedianDurationMs": median(durations) if durations else None,
            "primaryMinDurationMs": min(durations) if durations else None,
            "primaryMaxDurationMs": max(durations) if durations else None,
            "primaryDurationBuckets": _bucket_counts(duration_buckets, len(durations)),
            "top20LongestPrimaryTracksByDurationMs": sorted(primary_samples, key=lambda item: int(item.get("durationMs") or 0), reverse=True)[:20],
            "top20ShortestPrimaryTracksByDurationMs": sorted(primary_samples, key=lambda item: int(item.get("durationMs") or 0))[:20],
        },
        "addedAtStats": {
            "primaryEarliestAddedAt": min((dt for _, _, dt in added_pairs), default=None).strftime("%Y-%m-%d %H:%M:%S") if added_pairs else None,
            "primaryLatestAddedAt": max((dt for _, _, dt in added_pairs), default=None).strftime("%Y-%m-%d %H:%M:%S") if added_pairs else None,
            "primaryAddedByYear": dict(sorted(by_year.items())),
            "primaryAddedByYearMonth": dict(sorted(by_year_month.items())),
            "primaryAddedByCalendarMonth": dict(sorted(by_month.items())),
            "primaryAddedByHour": dict(sorted(by_hour.items())),
            "primaryAddedByWeekday": dict(sorted(by_weekday.items())),
            "top20YearMonthsByAddedCount": _top_counts(by_year_month, 20),
            "top20HoursByAddedCount": _top_counts(by_hour, 20),
            "top20EarliestAddedPrimaryTracks": [_sample_primary(row, raw) for row, raw, _ in sorted(added_pairs, key=lambda item: item[2])[:20]],
            "top20LatestAddedPrimaryTracks": [_sample_primary(row, raw) for row, raw, _ in sorted(added_pairs, key=lambda item: item[2], reverse=True)[:20]],
        },
        "rankingStats": {
            **_ranking_concentration(recent_result, "recentWeek"),
            **_ranking_concentration(all_result, "allTime"),
            "top20RecentWeekTracksByPlayCount": sorted(recent_samples, key=lambda item: int(item.get("playCount") or 0), reverse=True)[:20],
            "bottom20RecentWeekTracksByPlayCount": sorted(recent_samples, key=lambda item: int(item.get("playCount") or 0))[:20],
            "top20AllTimeTracksByPlayCount": sorted(all_samples, key=lambda item: int(item.get("playCount") or 0), reverse=True)[:20],
            "bottom20AllTimeTracksByPlayCount": sorted(all_samples, key=lambda item: int(item.get("playCount") or 0))[:20],
        },
        "overlapStats": {
            "matchMethod": match_method,
            "primaryAndRecentWeekCount": len(primary_keys & recent_keys),
            "primaryAndAllTimeCount": len(primary_keys & all_keys),
            "recentWeekAndAllTimeCount": len(recent_keys & all_keys),
            "allThreeCount": len(all_three),
            "top50PrimaryRecentWeekOverlapByRecentWeekPlayCount": overlap_rows(primary_keys & recent_keys, recent_keyed, 50),
            "top50PrimaryAllTimeOverlapByAllTimePlayCount": overlap_rows(primary_keys & all_keys, all_keyed, 50),
            "top50RecentWeekAllTimeOverlapByAllTimePlayCount": overlap_rows(recent_keys & all_keys, all_keyed, 50),
            "top50AllThreeOverlapByAllTimePlayCount": overlap_rows(all_three, all_keyed, 50),
            "onlyInRecentWeekTop20ByPlayCount": overlap_rows(recent_only, recent_keyed, 20),
            "onlyInAllTimeTop20ByPlayCount": overlap_rows(all_only, all_keyed, 20),
            "primaryNotInAnyRankingCount": len(primary_not_ranked),
        },
        "recentLongTermShiftStats": {
            "recentWeekTop20TracksInAllTimeTop100Count": len(recent_top20_keys & all_top100_keys),
            "recentWeekTop20TracksInAllTimeTop100Share": _round_share(len(recent_top20_keys & all_top100_keys) / len(recent_top20_keys)) if recent_top20_keys else 0,
            "allTimeTop20TracksInRecentWeekTop100Count": len(all_top20_keys & recent_top100_keys),
            "allTimeTop20TracksInRecentWeekTop100Share": _round_share(len(all_top20_keys & recent_top100_keys) / len(all_top20_keys)) if all_top20_keys else 0,
            "recentWeekAllTimeOverlapMedianAbsoluteRankDelta": median(rank_delta_values) if rank_delta_values else None,
            "top10RecentWeekAllTimeOverlapByRankRise": _rank_shift_samples(recent_keyed, all_keyed, "rise", 10),
            "top10RecentWeekAllTimeOverlapByRankDrop": _rank_shift_samples(recent_keyed, all_keyed, "drop", 10),
        },
        "artistStats": {
            "top30ArtistsByPrimaryTrackCount": _top_counts(artist_primary, 30),
            "top30ArtistsByRecentWeekPlayCount": _top_play_counts(artist_recent_play, 30),
            "top30ArtistsByAllTimePlayCount": _top_play_counts(artist_all_play, 30),
            "top30ArtistsByAllDatasetAppearanceCount": _top_counts(artist_all_appearance, 30),
            "singletonArtistsInPrimaryCount": sum(1 for count in artist_primary.values() if count == 1),
            "singletonArtistsInPrimarySamplesMax50": _counter_samples(artist_primary, artist_sample, 50),
        },
        "albumStats": {
            "top30AlbumsByPrimaryTrackCount": _top_counts(album_primary, 30),
            "top30AlbumsByRecentWeekPlayCount": _top_play_counts(album_recent_play, 30),
            "top30AlbumsByAllTimePlayCount": _top_play_counts(album_all_play, 30),
            "singletonAlbumsInPrimaryCount": sum(1 for count in album_primary.values() if count == 1),
            "singletonAlbumsInPrimarySamplesMax50": _counter_samples(album_primary, album_sample, 50),
        },
        "lexicalStats": {
            "top50TitleTermsByFrequency": _top_counts(title_terms, 50),
            "top50AlbumTermsByFrequency": _top_counts(album_terms, 50),
            "top50ArtistNameTermsByFrequency": _top_counts(artist_terms, 50),
            "titleScriptCounts": _char_stats(primary_result, "title"),
            "albumScriptCounts": _char_stats(primary_result, "album"),
            "tracksWithAsciiTitleCount": _char_stats(primary_result, "title")["trackCounts"].get("ascii", 0),
            "tracksWithCjkTitleCount": _char_stats(primary_result, "title")["trackCounts"].get("cjk", 0),
            "tracksWithKanaTitleCount": _char_stats(primary_result, "title")["trackCounts"].get("kana", 0),
            "tracksWithSymbolHeavyTitleCount": _char_stats(primary_result, "title")["symbolHeavyTrackCount"],
        },
        "sampleIndexes": {
            "top20PrimaryTracksByOrder": primary_samples[:20],
            "top20LatestPrimaryTracksByOrder": primary_samples[-20:],
            "top20EarliestAddedPrimaryTracks": [_sample_primary(row, raw) for row, raw, _ in sorted(added_pairs, key=lambda item: item[2])[:20]],
            "top20LatestAddedPrimaryTracks": [_sample_primary(row, raw) for row, raw, _ in sorted(added_pairs, key=lambda item: item[2], reverse=True)[:20]],
            "top20LongestPrimaryTracksByDurationMs": sorted(primary_samples, key=lambda item: int(item.get("durationMs") or 0), reverse=True)[:20],
            "top20ShortestPrimaryTracksByDurationMs": sorted(primary_samples, key=lambda item: int(item.get("durationMs") or 0))[:20],
            "top20RecentWeekTracksByPlayCount": sorted(recent_samples, key=lambda item: int(item.get("playCount") or 0), reverse=True)[:20],
            "bottom20RecentWeekTracksByPlayCount": sorted(recent_samples, key=lambda item: int(item.get("playCount") or 0))[:20],
            "top20AllTimeTracksByPlayCount": sorted(all_samples, key=lambda item: int(item.get("playCount") or 0), reverse=True)[:20],
            "bottom20AllTimeTracksByPlayCount": sorted(all_samples, key=lambda item: int(item.get("playCount") or 0))[:20],
        },
    }
