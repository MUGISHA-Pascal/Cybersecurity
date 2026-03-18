from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rca_defender.platform_paths import get_app_data_dir  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Remove RCA Defender local data (safe cleaner).")
    p.add_argument("--dry-run", action="store_true", help="Print what would be removed.")
    args = p.parse_args()

    app_dir = get_app_data_dir()
    if not app_dir.exists():
        print(f"Nothing to remove. App data dir not found: {app_dir}")
        return 0

    if args.dry_run:
        print("Would remove:")
        for pth in sorted(app_dir.rglob("*"), key=lambda p: (p.is_file(), str(p))):
            print(f" - {pth}")
        print(f" - {app_dir}")
        return 0

    shutil.rmtree(app_dir)
    print(f"Removed: {app_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
