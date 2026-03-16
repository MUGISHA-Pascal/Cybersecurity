from __future__ import annotations

import os
import sys
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from rca_defender.http_utils import http_get


@dataclass(frozen=True)
class DependencyPlan:
    vendor_needed: bool
    assets_needed: bool
    tkinter_ok: bool
    python_ok: bool


def _extract_zip_bytes(zip_bytes: bytes, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(dest_dir)


def check_plan(app_dir: Path) -> DependencyPlan:
    python_ok = sys.version_info >= (3, 9)
    try:
        import tkinter  # noqa: F401

        tkinter_ok = True
    except Exception:
        tkinter_ok = False

    vendor_dir = app_dir / "vendor" / "rca_vendor"
    assets_dir = app_dir / "assets"

    vendor_needed = not (vendor_dir / "__init__.py").exists()
    assets_needed = not (assets_dir / "scenarios.txt").exists()
    return DependencyPlan(
        vendor_needed=vendor_needed,
        assets_needed=assets_needed,
        tkinter_ok=tkinter_ok,
        python_ok=python_ok,
    )


def install_vendor_from_repo(repo_url: str, app_dir: Path) -> None:
    url = repo_url.rstrip("/") + "/deps/vendor_bundle.zip"
    res = http_get(url)
    if res.status != 200:
        raise RuntimeError(f"Failed to download vendor bundle (HTTP {res.status})")
    vendor_root = app_dir / "vendor"
    _extract_zip_bytes(res.body, vendor_root)


def install_assets_from_repo(repo_url: str, app_dir: Path) -> None:
    url = repo_url.rstrip("/") + "/assets/assets.zip"
    res = http_get(url)
    if res.status != 200:
        raise RuntimeError(f"Failed to download assets bundle (HTTP {res.status})")
    assets_root = app_dir / "assets"
    _extract_zip_bytes(res.body, assets_root)


def add_vendor_to_syspath(app_dir: Path) -> None:
    vendor_root = app_dir / "vendor"
    vendor_root.mkdir(parents=True, exist_ok=True)
    # Prepend so our offline-bundled modules are importable.
    sys.path.insert(0, os.fspath(vendor_root))
