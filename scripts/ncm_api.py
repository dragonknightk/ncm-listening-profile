from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from ncm_cdp import CdpClient
from ncm_env import NcmError


ALLOWED_API_PATHS = {
    "/api/nuser/account/get",
    "/api/user/playlist",
    "/api/v6/playlist/detail",
    "/api/v1/play/record",
}

UNSAFE_STATUSES = {401, 403, 429}


@dataclass
class ApiResult:
    data: dict[str, Any]
    summary: dict[str, Any]


class NcmApiError(NcmError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


def _json_arg(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _api_url(path: str, params: dict[str, Any] | None = None) -> str:
    if path not in ALLOWED_API_PATHS:
        raise NcmApiError(f"API path is not allowed: {path}", {"apiPath": path})
    query = urlencode({key: value for key, value in (params or {}).items() if value is not None})
    return f"https://music.163.com{path}" + (f"?{query}" if query else "")


def _summary_from_response(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    return {
        "apiPath": path,
        "status": payload.get("status"),
        "apiCode": data.get("code") if isinstance(data, dict) else None,
        "contentType": payload.get("contentType"),
        "bodyLength": payload.get("bodyLength"),
        "responseShape": payload.get("shape"),
    }


def fetch_api_json(client: CdpClient, path: str, params: dict[str, Any] | None = None) -> ApiResult:
    url = _api_url(path, params)
    expression = f"""
(async () => {{
  const url = {_json_arg(url)};
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  const summarize = data => {{
    const out = {{ jsonType: Array.isArray(data) ? 'array' : typeof data }};
    if (data && typeof data === 'object' && !Array.isArray(data)) {{
      out.topKeys = Object.keys(data).sort().slice(0, 40);
    }}
    const arrays = [];
    const walk = (node, path) => {{
      if (arrays.length >= 30) return;
      if (Array.isArray(node)) {{
        const first = node[0];
        arrays.push({{
          path: path || '$',
          length: node.length,
          firstItemKeys: first && typeof first === 'object' && !Array.isArray(first)
            ? Object.keys(first).sort().slice(0, 35)
            : null
        }});
        if (first) walk(first, (path || '$') + '[]');
      }} else if (node && typeof node === 'object') {{
        for (const key of Object.keys(node)) walk(node[key], path ? `${{path}}.${{key}}` : key);
      }}
    }};
    walk(data, '');
    out.arrays = arrays;
    return out;
  }};
  try {{
    const response = await fetch(url, {{ credentials: 'include', method: 'GET', signal: controller.signal }});
    const text = await response.text();
    const base = {{
      ok: true,
      status: response.status,
      contentType: response.headers && response.headers.get('content-type'),
      bodyLength: text.length
    }};
    try {{
      const data = JSON.parse(text);
      return {{ ...base, data, shape: summarize(data) }};
    }} catch (error) {{
      return {{
        ...base,
        parseError: error && error.name || 'Error',
        prefixKind: /^[\\[{{]/.test(text.trim()) ? 'json_like' : 'opaque_text'
      }};
    }}
  }} catch (error) {{
    return {{ ok: false, fetchError: String(error), errorName: error && error.name || 'Error' }};
  }} finally {{
    clearTimeout(timer);
  }}
}})()
"""
    payload = client.evaluate(expression, await_promise=True)
    if not isinstance(payload, dict):
        raise NcmApiError(f"API call returned an unexpected payload for {path}", {"apiPath": path})
    summary = _summary_from_response(path, payload)
    if not payload.get("ok"):
        raise NcmApiError(f"API fetch failed for {path}: {payload.get('errorName') or payload.get('fetchError')}", summary)
    status = payload.get("status")
    if status in UNSAFE_STATUSES:
        raise NcmApiError(f"API returned unsafe status {status} for {path}", summary)
    if status != 200:
        raise NcmApiError(f"API returned status {status} for {path}", summary)
    if payload.get("parseError"):
        raise NcmApiError(f"API JSON parse failed for {path}: {payload.get('parseError')}", summary)
    data = payload.get("data")
    if not isinstance(data, dict):
        raise NcmApiError(f"API response was not a JSON object for {path}", summary)
    code = data.get("code")
    if code != 200:
        raise NcmApiError(f"API returned code {code} for {path}", summary)
    return ApiResult(data=data, summary=summary)


def get_current_user(client: CdpClient) -> tuple[dict[str, str], dict[str, Any]]:
    result = fetch_api_json(client, "/api/nuser/account/get")
    profile = result.data.get("profile")
    account = result.data.get("account")
    if not isinstance(profile, dict) or profile.get("userId") in (None, ""):
        raise NcmApiError("Current user API did not return profile.userId.", result.summary)
    user = {"userId": str(profile.get("userId"))}
    if isinstance(account, dict) and account.get("id") not in (None, ""):
        user["accountId"] = str(account.get("id"))
    return user, result.summary


def list_created_playlists(client: CdpClient, user_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    result = fetch_api_json(client, "/api/user/playlist", {"uid": user_id, "limit": 1000, "offset": 0})
    playlists = result.data.get("playlist")
    if not isinstance(playlists, list):
        raise NcmApiError("Playlist API did not return playlist[].", result.summary)
    created = [
        item
        for item in playlists
        if isinstance(item, dict) and str(item.get("userId")) == str(user_id) and item.get("subscribed") is False
    ]
    if not created:
        raise NcmApiError("Playlist API returned no user-created playlists.", result.summary)
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(created, start=1):
        normalized.append(
            {
                "index": index,
                "name": str(item.get("name") or ""),
                "playlistId": str(item.get("id") or ""),
                "trackCount": item.get("trackCount"),
                "playCount": item.get("playCount"),
                "specialType": item.get("specialType"),
                "privacy": item.get("privacy"),
                "updateTime": item.get("updateTime"),
                "source": "api",
            }
        )
    summary = dict(result.summary)
    summary.update({"allPlaylistRows": len(playlists), "createdPlaylistRows": len(normalized)})
    return normalized, summary


def public_playlist_choices(playlists: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "index": item.get("index"),
            "name": item.get("name"),
            "trackCount": item.get("trackCount"),
        }
        for item in playlists
    ]


def _playlist_label(item: dict[str, Any]) -> str:
    return f"- {item.get('index')}: {item.get('name')} ({item.get('trackCount')} tracks)"


def resolve_playlist(playlists: list[dict[str, Any]], name: str | None, playlist_index: int | None) -> dict[str, Any]:
    if playlist_index is not None:
        matches = [item for item in playlists if item.get("index") == playlist_index]
    elif name:
        exact = [item for item in playlists if str(item.get("name")) == name]
        matches = exact or [item for item in playlists if name in str(item.get("name"))]
    else:
        raise NcmError("A playlist name or public index is required.")
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise NcmError("No matching playlist found. List playlists and choose one exact name or public index.")
    formatted = "\n".join(_playlist_label(item) for item in matches)
    raise NcmError("Playlist selection matched multiple playlists. Choose exactly one public index or exact name:\n" + formatted)


def fetch_primary_playlist(client: CdpClient, playlist_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    result = fetch_api_json(client, "/api/v6/playlist/detail", {"id": playlist_id, "n": 100000, "s": 0})
    playlist = result.data.get("playlist")
    if not isinstance(playlist, dict):
        raise NcmApiError("Playlist detail API did not return playlist.", result.summary)
    tracks = playlist.get("tracks")
    track_ids = playlist.get("trackIds")
    if not isinstance(tracks, list) or not isinstance(track_ids, list) or not tracks:
        raise NcmApiError("Playlist detail API returned invalid tracks or trackIds.", result.summary)
    summary = dict(result.summary)
    summary.update({"tracksFound": len(tracks), "trackIdsFound": len(track_ids)})
    return result.data, summary


def fetch_listening_record(client: CdpClient, user_id: str, period: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if period == "recent_week":
        record_type = 1
        key = "weekData"
    elif period == "all_time":
        record_type = 0
        key = "allData"
    else:
        raise ValueError(f"Unsupported listening record period: {period}")
    result = fetch_api_json(client, "/api/v1/play/record", {"uid": user_id, "type": record_type})
    rows = result.data.get(key)
    if not isinstance(rows, list) or (period == "all_time" and not rows):
        raise NcmApiError(f"Listening record API did not return {key}[].", result.summary)
    summary = dict(result.summary)
    summary.update({"rowsFound": len(rows), "recordType": record_type})
    return rows, summary
