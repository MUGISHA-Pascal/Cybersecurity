from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: bytes


def http_get(url: str, timeout_s: int = 15) -> HttpResult:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return HttpResult(status=resp.status, body=resp.read())


def http_post_json(url: str, payload: dict, timeout_s: int = 10) -> HttpResult:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return HttpResult(status=resp.status, body=resp.read())

