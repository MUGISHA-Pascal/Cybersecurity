from __future__ import annotations

from pathlib import Path


def load_scenarios_from_assets(assets_dir: Path) -> list[dict]:
    """
    Load simple scenarios from `assets/scenarios.txt`.

    Format (blank lines separate scenarios):
      TITLE: ...
      PROMPT: ...
      CORRECT: allow|block
      ALLOW: ...
      BLOCK: ...
    """
    path = assets_dir / "scenarios.txt"
    raw = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    scenarios: list[dict] = []
    for b in blocks:
        lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
        item = {"title": "", "prompt": "", "correct": "", "explain_allow": "", "explain_block": ""}
        for ln in lines:
            if ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            if k == "title":
                item["title"] = v
            elif k == "prompt":
                item["prompt"] = v
            elif k == "correct":
                item["correct"] = v
            elif k == "allow":
                item["explain_allow"] = v
            elif k == "block":
                item["explain_block"] = v
        if item["title"] and item["prompt"] and item["correct"] in {"allow", "block"}:
            scenarios.append(item)
    return scenarios

