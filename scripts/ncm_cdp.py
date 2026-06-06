from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests
import websocket

from ncm_env import NcmError


@dataclass
class CdpTarget:
    id: str
    title: str
    url: str
    web_socket_debugger_url: str


def get_targets(port: int) -> list[CdpTarget]:
    response = requests.get(f"http://127.0.0.1:{port}/json", timeout=2.0)
    response.raise_for_status()
    targets: list[CdpTarget] = []
    for item in response.json():
        ws = item.get("webSocketDebuggerUrl")
        if not ws:
            continue
        targets.append(
            CdpTarget(
                id=str(item.get("id") or ""),
                title=str(item.get("title") or ""),
                url=str(item.get("url") or ""),
                web_socket_debugger_url=str(ws),
            )
        )
    return targets


def select_ncm_target(port: int) -> CdpTarget:
    targets = get_targets(port)
    for target in targets:
        text = f"{target.url} {target.title}".lower()
        if "orpheus://" in text or "cloudmusic" in text or "netease" in text:
            return target
    if len(targets) == 1:
        return targets[0]
    formatted = "\n".join(f"- {t.title} {t.url}" for t in targets)
    raise NcmError(f"Could not identify NetEase Cloud Music CDP target. Targets:\n{formatted}")


class CdpClient:
    def __init__(self, target: CdpTarget):
        self.target = target
        self.ws = websocket.create_connection(target.web_socket_debugger_url, timeout=10)
        self._next_id = 0

    @classmethod
    def connect(cls, port: int) -> "CdpClient":
        return cls(select_ncm_target(port))

    def close(self) -> None:
        self.ws.close()

    def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._next_id += 1
        message_id = self._next_id
        self.ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            raw = self.ws.recv()
            message = json.loads(raw)
            if message.get("id") == message_id:
                if "error" in message:
                    raise NcmError(f"CDP error for {method}: {message['error']}")
                return message.get("result") or {}

    def evaluate(self, expression: str, await_promise: bool = False) -> Any:
        result = self.send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": True,
                "userGesture": True,
            },
        )
        if "exceptionDetails" in result:
            raise NcmError(f"CDP evaluation failed: {result['exceptionDetails']}")
        remote = result.get("result") or {}
        return remote.get("value")
