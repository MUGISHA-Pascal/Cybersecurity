from __future__ import annotations

import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "server_repo"


def main() -> int:
    p = argparse.ArgumentParser(description="Serve offline bundles for RCA Defender.")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=int(os.environ.get("RCA_REPO_PORT", "8000")))
    p.add_argument("--dir", default=str(DEFAULT_DIR), help="Directory to serve (default: server_repo).")
    args = p.parse_args()

    base_dir = Path(args.dir).resolve()
    if not base_dir.exists():
        raise SystemExit(f"Directory does not exist: {base_dir}\nRun: python tools/build_server_repo.py")

    handler = lambda *a, **kw: SimpleHTTPRequestHandler(*a, directory=str(base_dir), **kw)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving {base_dir} on http://{args.host}:{args.port}")
    print("Expected endpoints:")
    print(" - /deps/vendor_bundle.zip")
    print(" - /assets/assets.zip")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

