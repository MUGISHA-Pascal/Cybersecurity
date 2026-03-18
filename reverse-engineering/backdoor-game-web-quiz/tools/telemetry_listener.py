from __future__ import annotations

import argparse
import json
import os
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = ROOT / "telemetry_events.jsonl"


@dataclass
class EventStore:
    lock: threading.Lock
    events: list[dict]
    log_path: Path

    def add(self, event: dict) -> None:
        with self.lock:
            self.events.append(event)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def snapshot(self, limit: int = 100) -> list[dict]:
        with self.lock:
            return list(self.events[-limit:])


def _html_page(events: list[dict]) -> bytes:
    rows = []
    for e in reversed(events):
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.get("ts", 0)))
        rows.append(
            "<tr>"
            f"<td>{ts}</td>"
            f"<td><code>{e.get('session_id','')}</code></td>"
            f"<td>{e.get('event','')}</td>"
            f"<td><pre>{json.dumps(e.get('data',{}), ensure_ascii=False, indent=2)}</pre></td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>RCA Defender Listener</title>
  <meta http-equiv="refresh" content="2"/>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 16px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ text-align: left; background: #f7f7f7; position: sticky; top: 0; }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; }}
    code {{ background: #f1f1f1; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h2>RCA Defender Listener (safe telemetry)</h2>
  <p>POST gameplay events to <code>/event</code>. This does not provide remote shell access.</p>
  <table>
    <thead><tr><th>Time</th><th>Session</th><th>Event</th><th>Data</th></tr></thead>
    <tbody>
      {''.join(rows) if rows else '<tr><td colspan="4">No events yet.</td></tr>'}
    </tbody>
  </table>
</body>
</html>"""
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    store: EventStore

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/" or self.path.startswith("/?"):
            body = _html_page(self.store.snapshot())
            self._send(200, body, "text/html; charset=utf-8")
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/event":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n)
        try:
            payload: Any = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("not an object")
            self.store.add(payload)
            self._send(200, b"ok", "text/plain; charset=utf-8")
        except Exception as e:
            self._send(400, f"bad request: {e}".encode("utf-8"), "text/plain; charset=utf-8")

    def log_message(self, format: str, *args: object) -> None:
        # Keep console readable.
        return


def main() -> int:
    p = argparse.ArgumentParser(description="RCA Defender telemetry listener (dashboard).")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=int(os.environ.get("RCA_LISTENER_PORT", "9000")))
    p.add_argument("--log", default=str(DEFAULT_LOG), help="Where to append JSONL events.")
    args = p.parse_args()

    store = EventStore(lock=threading.Lock(), events=[], log_path=Path(args.log).resolve())
    Handler.store = store
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Listener: http://{args.host}:{args.port}")
    print("Endpoint: POST /event (application/json)")
    print(f"Log file: {store.log_path}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

