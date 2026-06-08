from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from ncm_aggregate import build_aggregate
from ncm_api import (
    fetch_listening_record,
    fetch_primary_playlist,
    get_current_user,
    list_created_playlists,
    public_playlist_choices,
    resolve_playlist,
)
from ncm_cdp import CdpClient
from ncm_diagnostics import CollectionDiagnostics
from ncm_env import (
    DependencyError,
    NcmError,
    UserActionRequired,
    assert_port_9222_available,
    block_if_client_running,
    check_dependencies,
    launch_client,
    print_json,
    require_unique_client,
    wait_for_cdp_version,
)
from ncm_outputs import (
    assert_only_expected_output_files,
    create_run_dirs,
    list_output_runs,
    shape_primary_rows,
    shape_ranking_rows,
    write_run,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect NetEase Cloud Music listening profile data.")
    parser.add_argument("--check", action="store_true", help="Check Python dependencies and environment helpers.")
    parser.add_argument("--list-playlists", action="store_true", help="Launch/connect and print user-created playlists.")
    parser.add_argument("--list-runs", action="store_true", help="List previous output runs without launching NetEase Cloud Music.")
    parser.add_argument("--playlist-name", help="Primary playlist name to collect.")
    parser.add_argument("--playlist-index", type=int, help="Public playlist number from --list-playlists.")
    parser.add_argument("--client-path", help="Path to the NetEase Cloud Music desktop client when discovery is ambiguous.")
    parser.add_argument("--port", type=int, default=9222, help="CDP port. This Skill requires 9222.")
    parser.add_argument(
        "--connect-existing-cdp",
        action="store_true",
        help="Connect to an already Skill-launched CDP session, used after --list-playlists.",
    )
    parser.add_argument("--skill-dir", default=str(Path(__file__).resolve().parent.parent), help="Skill root directory.")
    parser.add_argument("--timestamp", help="Override output timestamp for tests, format YYYYMMDD-HHMMSS.")
    return parser


def connect_runtime(args: argparse.Namespace, diagnostics: CollectionDiagnostics | None = None) -> CdpClient:
    phase = "cdp_connection" if args.connect_existing_cdp else "launch"
    if args.connect_existing_cdp:
        try:
            if diagnostics:
                diagnostics.start_phase("cdp_connection", mode="connect_existing_cdp")
            version = wait_for_cdp_version(args.port, timeout_s=5)
            client = CdpClient.connect(args.port)
            if diagnostics:
                diagnostics.set_environment(cdpVersion=version.get("Browser"), targetUrl=client.target.url)
                diagnostics.phase_ok("cdp_connection", mode="connect_existing_cdp", targetUrl=client.target.url)
            return client
        except Exception as exc:
            if diagnostics and not diagnostics.data.get("failedPhase"):
                diagnostics.phase_fail(phase, exc)
            raise

    try:
        if diagnostics:
            diagnostics.start_phase("launch")
        block_if_client_running(args.client_path)
        assert_port_9222_available(args.port)
        client_info = require_unique_client(args.client_path)
        if diagnostics:
            diagnostics.set_environment(
                clientPath=str(client_info.path),
                clientPlatform=client_info.platform,
                clientKind=client_info.kind,
            )
        launch_client(client_info, args.port)
        version = wait_for_cdp_version(args.port)
        if diagnostics:
            diagnostics.phase_ok(
                "launch",
                clientPath=str(client_info.path),
                clientPlatform=client_info.platform,
                clientKind=client_info.kind,
                clientLaunchMode="launched_client",
            )
            diagnostics.start_phase("cdp_connection", mode="launched_client")
        client = CdpClient.connect(args.port)
        if diagnostics:
            diagnostics.set_environment(cdpVersion=version.get("Browser"), targetUrl=client.target.url)
            diagnostics.phase_ok("cdp_connection", mode="launched_client", targetUrl=client.target.url)
        return client
    except Exception as exc:
        if diagnostics and not diagnostics.data.get("failedPhase"):
            diagnostics.phase_fail(phase, exc)
        raise


def _duration_quality(rows: list[dict[str, Any]]) -> dict[str, int]:
    total = len(rows)
    parsed = sum(1 for row in rows if row.get("durationMs") is not None)
    added = sum(1 for row in rows if row.get("addedAt") is not None)
    return {
        "durationMsRows": parsed,
        "durationMsMissingRows": total - parsed,
        "addedAtRows": added,
        "addedAtMissingRows": total - added,
    }


def _ranking_quality(rows: list[dict[str, Any]], prefix: str) -> dict[str, int]:
    total = len(rows)
    counted = sum(1 for row in rows if row.get("playCount") is not None)
    return {
        f"{prefix}PlayCountRows": counted,
        f"{prefix}PlayCountMissingRows": total - counted,
    }


def _load_user_and_playlists(client: CdpClient, diagnostics: CollectionDiagnostics | None = None) -> tuple[dict[str, str], list[dict[str, Any]]]:
    if diagnostics:
        diagnostics.start_phase("current_user_api", apiPath="/api/nuser/account/get")
    try:
        user, user_summary = get_current_user(client)
    except Exception as exc:
        if diagnostics and not diagnostics.data.get("failedPhase"):
            diagnostics.phase_fail("current_user_api", exc)
        raise
    if diagnostics:
        diagnostics.phase_ok("current_user_api", **user_summary, userIdFound=True)

    if diagnostics:
        diagnostics.start_phase("playlist_listing_api", apiPath="/api/user/playlist")
    try:
        playlists, playlist_summary = list_created_playlists(client, user["userId"])
    except Exception as exc:
        if diagnostics and not diagnostics.data.get("failedPhase"):
            diagnostics.phase_fail("playlist_listing_api", exc)
        raise
    if diagnostics:
        diagnostics.phase_ok("playlist_listing_api", **playlist_summary, rowsFound=len(playlists))
    return user, playlists


def list_playlists(args: argparse.Namespace) -> int:
    client = connect_runtime(args)
    try:
        _, playlists = _load_user_and_playlists(client)
        print_json({"playlists": public_playlist_choices(playlists)})
    finally:
        client.close()
    return 0


def list_runs(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill_dir).resolve()
    print_json({"runs": list_output_runs(skill_dir)})
    return 0


def collect(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill_dir).resolve()
    run_dir = create_run_dirs(skill_dir, args.timestamp)
    diagnostics = CollectionDiagnostics(run_dir, skill_dir, args.port)
    diagnostics.write()
    client: CdpClient | None = None
    current_phase = "input_validation"
    try:
        choice_count = sum(value is not None for value in (args.playlist_name, args.playlist_index))
        if choice_count != 1:
            raise UserActionRequired("Pass exactly one primary playlist with --playlist-index or --playlist-name.")

        current_phase = "cdp_connection"
        client = connect_runtime(args, diagnostics)

        current_phase = "playlist_listing_api"
        user, playlists = _load_user_and_playlists(client, diagnostics)

        current_phase = "playlist_selection"
        playlist = resolve_playlist(playlists, args.playlist_name, args.playlist_index)
        diagnostics.phase_ok(
            current_phase,
            selectedBy="playlistIndex" if args.playlist_index is not None else "playlistName",
            selectedTrackCount=playlist.get("trackCount"),
            selectedSpecialType=playlist.get("specialType"),
        )

        current_phase = "primary_playlist_api"
        diagnostics.start_phase(current_phase, apiPath="/api/v6/playlist/detail")
        playlist_detail, primary_summary = fetch_primary_playlist(client, str(playlist.get("playlistId")))
        diagnostics.phase_ok(current_phase, **primary_summary)

        current_phase = "ranking_recent_week_api"
        diagnostics.start_phase(current_phase, apiPath="/api/v1/play/record", recordType=1)
        recent_api, recent_summary = fetch_listening_record(client, user["userId"], "recent_week")
        diagnostics.phase_ok(current_phase, **recent_summary)

        current_phase = "ranking_all_time_api"
        diagnostics.start_phase(current_phase, apiPath="/api/v1/play/record", recordType=0)
        all_api, all_summary = fetch_listening_record(client, user["userId"], "all_time")
        diagnostics.phase_ok(current_phase, **all_summary)

        current_phase = "result_shaping"
        diagnostics.start_phase(current_phase)
        primary_raw, primary_result = shape_primary_rows(playlist_detail)
        recent_raw, recent_result = shape_ranking_rows("ranking_recent_week", recent_api)
        all_raw, all_result = shape_ranking_rows("ranking_all_time", all_api)
        diagnostics.phase_ok(
            current_phase,
            primaryRows=len(primary_result),
            recentWeekRows=len(recent_result),
            allTimeRows=len(all_result),
            **_duration_quality(primary_result),
            **_ranking_quality(recent_result, "recentWeek"),
            **_ranking_quality(all_result, "allTime"),
        )

        current_phase = "aggregate"
        diagnostics.start_phase(current_phase)
        aggregate = build_aggregate(primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result)
        diagnostics.phase_ok(current_phase, aggregateSchemaVersion=aggregate.get("schemaVersion"))

        current_phase = "output_writing"
        diagnostics.start_phase(current_phase)
        paths = write_run(run_dir, primary_raw, primary_result, recent_raw, recent_result, all_raw, all_result, aggregate)
        diagnostics.phase_ok(current_phase)
        diagnostics.set_quality(
            primaryRows=len(primary_result),
            recentWeekRows=len(recent_result),
            allTimeRows=len(all_result),
            collectionSource="api",
            **_duration_quality(primary_result),
            **_ranking_quality(recent_result, "recentWeek"),
            **_ranking_quality(all_result, "allTime"),
        )

        current_phase = "validation"
        diagnostics.start_phase(current_phase)
        assert_only_expected_output_files(run_dir)
        diagnostics.phase_ok(current_phase)
        print_json(
            {
                "runDir": str(run_dir),
                "resultFiles": {
                    "primaryPlaylist": str(paths["result_primary"]),
                    "rankingRecentWeek": str(paths["result_recent"]),
                    "rankingAllTime": str(paths["result_all"]),
                },
                "csvFiles": {
                    "primaryPlaylist": str(paths["csv_primary"]),
                    "rankingRecentWeek": str(paths["csv_recent"]),
                    "rankingAllTime": str(paths["csv_all"]),
                },
                "aggregateFile": str(paths["aggregate"]),
                "diagnosticsFile": str(diagnostics.path),
            }
        )
    except Exception as exc:
        if not diagnostics.data.get("failedPhase"):
            diagnostics.phase_fail(current_phase, exc)
        raise
    finally:
        if client is not None:
            client.close()
    return 0


def check() -> int:
    check_dependencies()
    print_json({"ok": True, "dependencies": ["psutil", "requests", "websocket-client"]})
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.list_runs:
            return list_runs(args)
        check_dependencies()
        if args.check:
            return check()
        if args.list_playlists:
            return list_playlists(args)
        return collect(args)
    except (DependencyError, UserActionRequired, NcmError, FileExistsError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
