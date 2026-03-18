from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER_REPO = ROOT / "server_repo"
VENDOR_SRC = ROOT / "vendor_src"
ASSETS_SRC = ROOT / "assets_src"


def _zip_dir(src_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in src_dir.rglob("*"):
            if path.is_dir():
                continue
            arc = path.relative_to(src_dir)
            zf.write(path, arcname=str(arc))


def main() -> int:
    if SERVER_REPO.exists():
        shutil.rmtree(SERVER_REPO)
    (SERVER_REPO / "deps").mkdir(parents=True, exist_ok=True)
    (SERVER_REPO / "assets").mkdir(parents=True, exist_ok=True)

    _zip_dir(VENDOR_SRC, SERVER_REPO / "deps" / "vendor_bundle.zip")
    _zip_dir(ASSETS_SRC, SERVER_REPO / "assets" / "assets.zip")

    print(f"Built server repo at: {SERVER_REPO}")
    print("Files:")
    for p in sorted(SERVER_REPO.rglob("*")):
        if p.is_file():
            print(f" - {p.relative_to(SERVER_REPO)} ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

