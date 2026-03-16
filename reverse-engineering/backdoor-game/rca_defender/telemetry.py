from __future__ import annotations

import time
from dataclasses import dataclass

from rca_defender.http_utils import http_post_json


@dataclass(frozen=True)
class TelemetryClient:
    listener_url: str | None
    session_id: str

    def emit(self, event: str, data: dict) -> None:
        if not self.listener_url:
            return
        payload = {
            "ts": time.time(),
            "session_id": self.session_id,
            "event": event,
            "data": data,
        }
        try:
            http_post_json(self.listener_url.rstrip("/") + "/event", payload)
        except Exception:
            # Telemetry must never interrupt the game.
            return

