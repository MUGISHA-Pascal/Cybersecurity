from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

from rca_defender import deps
from rca_defender.game_data import load_scenarios_from_assets
from rca_defender.platform_paths import get_app_data_dir
from rca_defender.telemetry import TelemetryClient
from rca_defender.ui_tk import run_game_window, show_blocking_error, show_consent_dialog


APP_TITLE = "RCA Defender (Safe Classroom Game)"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=APP_TITLE)
    p.add_argument(
        "--repo-url",
        default=os.environ.get("RCA_REPO_URL", "").strip() or None,
        help="Local class server base URL (example: http://192.168.56.1:8000)",
    )
    p.add_argument(
        "--listener-url",
        default=os.environ.get("RCA_LISTENER_URL", "").strip() or None,
        help="Teacher dashboard base URL (example: http://192.168.56.1:9000)",
    )
    p.add_argument("--no-fullscreen", action="store_true", help="Disable fullscreen mode.")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    app_dir = get_app_data_dir()
    app_dir.mkdir(parents=True, exist_ok=True)

    consent = show_consent_dialog(APP_TITLE)
    if not consent.accepted:
        return 1

    plan = deps.check_plan(app_dir)
    if not plan.python_ok:
        show_blocking_error(
            APP_TITLE,
            "Python 3.9+ is required to run this game.\n\n"
            f"Current version: {sys.version.split()[0]}",
        )
        return 2

    if not plan.tkinter_ok:
        show_blocking_error(
            APP_TITLE,
            "Tkinter is missing.\n\n"
            "Ubuntu fix: sudo apt-get install python3-tk\n"
            "Windows: reinstall Python from python.org and ensure 'tcl/tk' is included.",
        )
        return 3

    if (plan.vendor_needed or plan.assets_needed) and not consent.allow_downloads:
        show_blocking_error(
            APP_TITLE,
            "Offline resources are not installed yet, and downloads were not allowed.\n\n"
            "Re-run the game and allow downloads, or install resources manually using your class server.",
        )
        return 4

    if (plan.vendor_needed or plan.assets_needed) and not args.repo_url:
        show_blocking_error(
            APP_TITLE,
            "Offline resources are missing, but no local server URL was provided.\n\n"
            "Run with: python rca_defender/launcher.py --repo-url http://<server-ip>:8000",
        )
        return 5

    # Install missing offline bundles.
    try:
        if plan.vendor_needed:
            deps.install_vendor_from_repo(args.repo_url, app_dir)
        if plan.assets_needed:
            deps.install_assets_from_repo(args.repo_url, app_dir)
    except Exception as e:
        show_blocking_error(APP_TITLE, f"Failed to install offline resources:\n\n{e}")
        return 6

    deps.add_vendor_to_syspath(app_dir)

    assets_dir = app_dir / "assets"
    scenarios = load_scenarios_from_assets(assets_dir)
    if not scenarios:
        show_blocking_error(APP_TITLE, f"No scenarios loaded from: {assets_dir}")
        return 7

    session_id = uuid.uuid4().hex[:12]
    telemetry = TelemetryClient(listener_url=args.listener_url, session_id=session_id)
    telemetry.emit("launcher_start", {"platform": sys.platform})

    run_game_window(
        app_title=APP_TITLE,
        scenarios=scenarios,
        telemetry_emit=telemetry.emit,
        fullscreen=not args.no_fullscreen,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

