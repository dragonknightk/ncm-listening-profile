from __future__ import annotations

import json
import platform
from datetime import datetime
from pathlib import Path
from typing import Any


DIAGNOSTICS_SCHEMA_VERSION = 3
VERIFIED_ENVIRONMENTS = [
    {
        "platform": "Windows",
        "status": "verified",
        "details": "Windows 10 with NetEase Cloud Music 3.0.0 Beta 64-bit / Build 201967 / Patch dd70f35; higher Windows systems and newer NetEase Cloud Music desktop clients have also passed real collection runs.",
    },
    {
        "platform": "macOS",
        "status": "verified",
        "details": "macOS 26.3.1 arm64 with NeteaseMusicDesktop/3.1.7.3283.",
    },
]


REPAIR_HINTS: dict[str, dict[str, Any]] = {
    "launch": {
        "likelyFiles": ["scripts/ncm_env.py", "scripts/collect_ncm_profile.py"],
        "likelyFunctions": ["connect_runtime", "block_if_client_running", "assert_port_9222_available"],
    },
    "cdp_connection": {
        "likelyFiles": ["scripts/ncm_cdp.py", "scripts/ncm_env.py"],
        "likelyFunctions": ["wait_for_cdp_version", "select_ncm_target", "CdpClient.connect"],
    },
    "current_user_api": {
        "likelyFiles": ["scripts/ncm_api.py", "scripts/collect_ncm_profile.py"],
        "likelyFunctions": ["get_current_user", "fetch_api_json"],
    },
    "playlist_listing_api": {
        "likelyFiles": ["scripts/ncm_api.py", "scripts/collect_ncm_profile.py"],
        "likelyFunctions": ["list_created_playlists", "fetch_api_json"],
    },
    "playlist_selection": {
        "likelyFiles": ["scripts/ncm_api.py"],
        "likelyFunctions": ["resolve_playlist"],
    },
    "primary_playlist_api": {
        "likelyFiles": ["scripts/ncm_api.py", "scripts/ncm_outputs.py"],
        "likelyFunctions": ["fetch_primary_playlist", "shape_primary_rows"],
    },
    "ranking_recent_week_api": {
        "likelyFiles": ["scripts/ncm_api.py", "scripts/ncm_outputs.py"],
        "likelyFunctions": ["fetch_listening_record", "shape_ranking_rows"],
    },
    "ranking_all_time_api": {
        "likelyFiles": ["scripts/ncm_api.py", "scripts/ncm_outputs.py"],
        "likelyFunctions": ["fetch_listening_record", "shape_ranking_rows"],
    },
    "result_shaping": {
        "likelyFiles": ["scripts/ncm_outputs.py", "scripts/test_ncm_profile.py"],
        "likelyFunctions": ["shape_primary_rows", "shape_ranking_rows", "format_duration"],
    },
    "aggregate": {
        "likelyFiles": ["scripts/ncm_aggregate.py", "scripts/test_ncm_profile.py"],
        "likelyFunctions": ["build_aggregate"],
    },
    "output_writing": {
        "likelyFiles": ["scripts/ncm_outputs.py", "scripts/test_ncm_profile.py"],
        "likelyFunctions": ["write_run", "assert_only_expected_output_files"],
    },
    "validation": {
        "likelyFiles": ["scripts/ncm_outputs.py", "scripts/test_ncm_profile.py"],
        "likelyFunctions": ["assert_only_expected_output_files"],
    },
}


SENSITIVE_DIAGNOSTIC_KEYS = {
    "apiResponse",
    "fullResponse",
    "playlistContents",
    "songList",
    "username",
    "cookies",
    "cookie",
    "token",
    "headers",
    "header",
    "postData",
    "requestBody",
}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _safe_error_summary(error: BaseException) -> str:
    text = str(error).replace("\r", "\n").split("\n", 1)[0].strip()
    if not text:
        text = error.__class__.__name__
    return text[:300]


def _error_code(phase: str, error: BaseException) -> str:
    name = error.__class__.__name__.lower()
    normalized = phase.replace(".", "_")
    return f"{normalized}_{name}"


def _sanitize_details(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _sanitize_details(child)
            for key, child in value.items()
            if key not in SENSITIVE_DIAGNOSTIC_KEYS and "cookie" not in key.lower() and "token" not in key.lower()
        }
    if isinstance(value, list):
        return [_sanitize_details(item) for item in value]
    return value


class CollectionDiagnostics:
    def __init__(self, run_dir: Path, skill_dir: Path, port: int):
        self.run_dir = run_dir
        self.path = run_dir / "log" / "collection_diagnostics.json"
        self.data: dict[str, Any] = {
            "schemaVersion": DIAGNOSTICS_SCHEMA_VERSION,
            "skillVersion": "ncm-listening-profile-v6",
            "runId": run_dir.name,
            "createdAt": _now_iso(),
            "updatedAt": _now_iso(),
            "skillRoot": str(skill_dir),
            "verifiedEnvironments": VERIFIED_ENVIRONMENTS,
            "environment": {
                "os": platform.system() or "unknown",
                "platform": platform.platform(),
                "cdpPort": port,
            },
            "phases": {},
            "quality": {
                "warnings": [],
            },
            "repairHints": [],
        }

    def set_environment(self, **values: Any) -> None:
        for key, value in values.items():
            if value is not None:
                self.data["environment"][key] = value
        self.write()

    def start_phase(self, phase: str, **details: Any) -> None:
        self.data["phases"][phase] = {"status": "running", **_sanitize_details({k: v for k, v in details.items() if v is not None})}
        self.write()

    def phase_ok(self, phase: str, **details: Any) -> None:
        self.data["phases"][phase] = {"status": "ok", **_sanitize_details({k: v for k, v in details.items() if v is not None})}
        self.write()

    def phase_fail(self, phase: str, error: BaseException) -> None:
        code = _error_code(phase, error)
        details = _sanitize_details(getattr(error, "details", {}) or {})
        phase_data = {
            "status": "failed",
            "errorCode": code,
            "errorSummary": _safe_error_summary(error),
        }
        if details:
            phase_data["details"] = details
        self.data["phases"][phase] = phase_data
        self.data["failedPhase"] = phase
        self.data["errorCode"] = code
        self.data["errorSummary"] = _safe_error_summary(error)
        if details:
            self.data["errorDetails"] = details
        self.data["repairHints"] = [self.repair_hint(phase, code)]
        self.write()

    def set_quality(self, **values: Any) -> None:
        for key, value in values.items():
            self.data["quality"][key] = _sanitize_details(value)
        self.write()

    def add_warning(self, code: str, message: str) -> None:
        self.data["quality"].setdefault("warnings", []).append({"code": code, "message": message})
        self.write()

    def repair_hint(self, phase: str, code: str) -> dict[str, Any]:
        hint = REPAIR_HINTS.get(phase, {})
        return {
            "phase": phase,
            "errorCode": code,
            "goal": "Repair API collection, shaping, aggregate, or output compatibility in the Skill instance that produced this diagnostics file.",
            "read": hint.get("likelyFiles", ["scripts/collect_ncm_profile.py"]),
            "likelyFunctions": hint.get("likelyFunctions", []),
            "doNotPersistInDiagnostics": [
                "complete API response",
                "full playlist contents",
                "full song lists",
                "cookies",
                "token",
                "headers",
                "post data",
            ],
            "validation": [
                "python scripts/test_ncm_profile.py",
                "retry the original collection command",
            ],
        }

    def write(self) -> Path:
        self.data["updatedAt"] = _now_iso()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        return self.path
