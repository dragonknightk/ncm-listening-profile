from __future__ import annotations

import json
import os
import socket
import string
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class NcmError(RuntimeError):
    """Base error for user-facing collection failures."""


class DependencyError(NcmError):
    pass


class UserActionRequired(NcmError):
    pass


@dataclass(frozen=True)
class NcmProcess:
    pid: int
    name: str
    exe: str | None


def check_dependencies() -> None:
    missing: list[str] = []
    for package, import_name in (
        ("psutil", "psutil"),
        ("requests", "requests"),
        ("websocket-client", "websocket"),
    ):
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    if missing:
        raise DependencyError(
            "Missing Python package(s): "
            + ", ".join(missing)
            + ". Install with: python -m pip install -r scripts/requirements.txt"
        )


def _load_psutil():
    try:
        import psutil  # type: ignore
    except ImportError as exc:
        raise DependencyError(
            "Missing Python package: psutil. Install with: "
            "python -m pip install -r scripts/requirements.txt"
        ) from exc
    return psutil


def find_running_cloudmusic_processes() -> list[NcmProcess]:
    psutil = _load_psutil()
    matches: list[NcmProcess] = []
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            name = proc.info.get("name") or ""
            exe = proc.info.get("exe")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        name_l = name.lower()
        exe_l = (exe or "").lower()
        if name_l == "cloudmusic.exe" or exe_l.endswith("\\cloudmusic.exe"):
            matches.append(NcmProcess(pid=int(proc.info["pid"]), name=name, exe=exe))
    return matches


def _candidate_from_env() -> list[Path]:
    value = os.environ.get("NCM_CLOUDMUSIC_EXE")
    return [Path(value)] if value else []


def _candidate_from_registry() -> list[Path]:
    if sys.platform != "win32":
        return []
    try:
        import winreg  # type: ignore
    except ImportError:
        return []

    paths: list[Path] = []
    app_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\cloudmusic.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\App Paths\cloudmusic.exe"),
    ]
    for hive, key_name in app_paths:
        try:
            with winreg.OpenKey(hive, key_name) as key:
                value, _ = winreg.QueryValueEx(key, "")
                if value:
                    paths.append(Path(value))
        except OSError:
            pass

    uninstall_roots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, root_name in uninstall_roots:
        try:
            with winreg.OpenKey(hive, root_name) as root:
                for idx in range(winreg.QueryInfoKey(root)[0]):
                    try:
                        sub_name = winreg.EnumKey(root, idx)
                        with winreg.OpenKey(root, sub_name) as sub:
                            display, _ = winreg.QueryValueEx(sub, "DisplayName")
                            if "网易云" not in display and "NetEase" not in display and "CloudMusic" not in display:
                                continue
                            try:
                                install, _ = winreg.QueryValueEx(sub, "InstallLocation")
                            except OSError:
                                install = ""
                            if install:
                                paths.append(Path(install) / "cloudmusic.exe")
                    except OSError:
                        continue
        except OSError:
            pass
    return paths


def _common_candidates() -> list[Path]:
    candidates: list[Path] = []
    env_dirs = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("LOCALAPPDATA"),
    ]
    for base in env_dirs:
        if not base:
            continue
        candidates.extend(
            [
                Path(base) / "Netease" / "CloudMusic" / "cloudmusic.exe",
                Path(base) / "NetEase" / "CloudMusic" / "cloudmusic.exe",
                Path(base) / "CloudMusic" / "cloudmusic.exe",
            ]
        )

    for drive in string.ascii_uppercase:
        root = Path(f"{drive}:\\")
        if root.exists():
            candidates.extend(
                [
                    root / "CloudMusic" / "cloudmusic.exe",
                    root / "Program Files" / "Netease" / "CloudMusic" / "cloudmusic.exe",
                    root / "Program Files (x86)" / "Netease" / "CloudMusic" / "cloudmusic.exe",
                ]
            )
    return candidates


def _unique_existing(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        try:
            resolved = path.expanduser().resolve()
        except OSError:
            continue
        key = str(resolved).lower()
        if key not in seen and resolved.exists() and resolved.name.lower() == "cloudmusic.exe":
            seen.add(key)
            result.append(resolved)
    return result


def discover_cloudmusic_exes(explicit: str | None = None) -> list[Path]:
    if explicit:
        return _unique_existing([Path(explicit)])
    return _unique_existing([*_candidate_from_env(), *_candidate_from_registry(), *_common_candidates()])


def require_unique_cloudmusic_exe(explicit: str | None = None) -> Path:
    candidates = discover_cloudmusic_exes(explicit)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise UserActionRequired(
            "Could not find cloudmusic.exe. Ask the user for the NetEase Cloud Music executable path "
            "and pass it with --cloudmusic-exe."
        )
    formatted = "\n".join(f"- {path}" for path in candidates)
    raise UserActionRequired(
        "Found multiple cloudmusic.exe candidates. Ask the user which one to use and pass it with "
        f"--cloudmusic-exe:\n{formatted}"
    )


def port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def describe_port_owner(port: int) -> str:
    try:
        psutil = _load_psutil()
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr and conn.laddr.port == port and conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    return f"{proc.name()} (pid {conn.pid})"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return f"pid {conn.pid}"
    except Exception:
        pass
    return "another program"


def assert_port_9222_available(port: int) -> None:
    if port != 9222:
        raise UserActionRequired("This Skill requires CDP port 9222. Do not use another port.")
    if port_is_open("127.0.0.1", port):
        raise UserActionRequired(
            f"Port 9222 is occupied by {describe_port_owner(port)}. This Skill requires port 9222; "
            "close the occupying program and run again."
        )


def block_if_cloudmusic_running(explicit_exe: str | None = None) -> None:
    running = find_running_cloudmusic_processes()
    if not running:
        return
    candidates = discover_cloudmusic_exes(explicit_exe)
    process_lines = "\n".join(f"- pid {p.pid}: {p.exe or p.name}" for p in running)
    if len(candidates) == 1:
        path_note = f"\nDetected executable candidate: {candidates[0]}"
    elif len(candidates) > 1:
        path_note = "\nMultiple executable candidates were found; ask the user which one to use with --cloudmusic-exe."
    else:
        path_note = "\nNo executable path was found; ask the user for cloudmusic.exe and pass --cloudmusic-exe."
    raise UserActionRequired(
        "NetEase Cloud Music is already running. Ask the user to close it manually before launching this Skill.\n"
        + process_lines
        + path_note
    )


def launch_cloudmusic(exe: Path, port: int) -> subprocess.Popen:
    args = [
        str(exe),
        "--force-renderer-accessibility=complete",
        f"--remote-debugging-port={port}",
    ]
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_for_cdp_version(port: int, timeout_s: float = 30.0) -> dict:
    import requests

    deadline = time.monotonic() + timeout_s
    url = f"http://127.0.0.1:{port}/json/version"
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = requests.get(url, timeout=1.0)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
            time.sleep(0.5)
    raise NcmError(f"Timed out waiting for NetEase Cloud Music CDP on port {port}: {last_error}")


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
