# RCA Defender — “Backdoor Game” (Safe Classroom Demo)

This folder contains a **safe cybersecurity-awareness game** for Windows + Ubuntu VMs.

It **does not** implement a real backdoor, remote shell, or stealth persistence. Instead it demonstrates:
- user consent and transparency,
- offline dependency/resource installation from a **local class server**,
- a “listener” dashboard that receives **harmless gameplay telemetry**,
- a cleaner tool that removes files created by the game.

## Folder structure

- Game entry: `run_rca_defender.py`
- Game code: `rca_defender/`
- Tools:
  - `tools/build_server_repo.py` (build offline zip bundles)
  - `tools/local_repo_server.py` (serve bundles over HTTP)
  - `tools/telemetry_listener.py` (listener/dashboard for telemetry)
  - `tools/cleaner.py` (remove local game data)
- Offline bundle sources:
  - `assets_src/` (scenario content)
  - `vendor_src/` (example “vendor” module)
- Built server content (generated): `server_repo/`
- Report: `docs/REPORT.md`

## Requirements (Windows + Ubuntu VM)

- Python 3.9+
- Tkinter
  - Ubuntu: `sudo apt-get install python3-tk`
  - Windows: install Python from python.org and ensure Tcl/Tk is included

## How to run (teacher / server VM)

From the repo root:

1) Build the offline bundles:
```bash
python reverse-engineering/backdoor-game/tools/build_server_repo.py
```

2) Start the local repo server (default port `8000`):
```bash
python reverse-engineering/backdoor-game/tools/local_repo_server.py --host 0.0.0.0 --port 8000
```

It serves:
- `http://<server-ip>:8000/deps/vendor_bundle.zip`
- `http://<server-ip>:8000/assets/assets.zip`

3) Start the telemetry listener dashboard (default port `9000`):
```bash
python reverse-engineering/backdoor-game/tools/telemetry_listener.py --host 0.0.0.0 --port 9000
```

Open:
- `http://<listener-ip>:9000`

## How to run (target VM)

Run the game (fullscreen by default):
```bash
python reverse-engineering/backdoor-game/run_rca_defender.py --repo-url http://<server-ip>:8000 --listener-url http://<listener-ip>:9000
```

Disable fullscreen:
```bash
python reverse-engineering/backdoor-game/run_rca_defender.py --no-fullscreen --repo-url http://<server-ip>:8000
```

## How the app works

1) Consent & notice (before anything else)
- On launch, the app shows a consent screen explaining what it will do (optional downloads + optional telemetry) and what it will not do (no remote shell/backdoor).

2) Dependency/resource checks
- Checks Python version and whether Tkinter is available.
- Checks whether offline bundles are already installed in the per-user app data directory.

3) Offline installation from local server (if needed and allowed)
- If missing, it downloads:
  - `vendor_bundle.zip` into `<app_data>/vendor/`
  - `assets.zip` into `<app_data>/assets/`
- Then the game loads scenarios from `<app_data>/assets/scenarios.txt`.

4) Gameplay
- Tkinter UI runs a sequence of scenarios.
- The player chooses actions and gets immediate feedback + score.
- Press `Esc` to pause/resume; on focus loss the game pauses itself (it does not block the OS).

5) “Listener” (safe telemetry)
- If `--listener-url` is provided, the game POSTs JSON events to `<listener-url>/event`.
- Events include: game start/finish, round start, and the player’s choice/correctness.
- Telemetry failures never interrupt the game.

## Where files are stored (and what Cleaner removes)

Per-user app data directory:
- Windows: `%APPDATA%\\RCA-Defender`
- Ubuntu/Linux: `~/.local/share/RCA-Defender` (or `$XDG_DATA_HOME/RCA-Defender`)

Cleaner tool:
```bash
python reverse-engineering/backdoor-game/tools/cleaner.py --dry-run
python reverse-engineering/backdoor-game/tools/cleaner.py
```
