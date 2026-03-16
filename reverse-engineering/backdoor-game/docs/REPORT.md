# Rwanda Coding Academy — Defending Rwanda Cyberspace (Safe Implementation)

Date: March 16, 2026  
Presentation: Wednesday, March 18, 2026 (13h30–17h00)

## Important note (ethics + safety)

The assignment text mentions building a “backdoor”, “shell access”, and “persistence”. Those are malware behaviors. This project **does not implement a backdoor, remote shell, or stealth persistence**.

Instead, we implement a **cybersecurity-awareness game** with:
- A **consent screen** (user is notified before anything runs).
- **Offline dependency/resource installation** from a **local class server** (no Internet required).
- A **teacher “listener” dashboard** that receives **harmless telemetry** (game events only).
- A **Cleaner tool** that removes everything the project stored locally.

This makes the demo legal/ethical and safe to run inside Windows + Ubuntu VMs.

## Project overview

Components:
- Game/Launcher: `run_rca_defender.py`
- Local repo server (hosts offline bundles): `tools/local_repo_server.py`
- Bundle builder (creates zip bundles for the local server): `tools/build_server_repo.py`
- Listener dashboard (receives telemetry): `tools/telemetry_listener.py`
- Cleaner (removes local data created by the game): `tools/cleaner.py`

Local data directory created by the game:
- Windows: `%APPDATA%\\RCA-Defender`
- Ubuntu/Linux: `~/.local/share/RCA-Defender` (or `$XDG_DATA_HOME/RCA-Defender`)

## Installation (teacher machine / local server VM)

1) Build the offline bundles (vendor + assets):
```bash
python tools/build_server_repo.py
```

2) Start the local repo server (default port `8000`):
```bash
python tools/local_repo_server.py --host 0.0.0.0 --port 8000
```

This serves:
- `http://<server-ip>:8000/deps/vendor_bundle.zip`
- `http://<server-ip>:8000/assets/assets.zip`

3) Start the telemetry listener dashboard (default port `9000`):
```bash
python tools/telemetry_listener.py --host 0.0.0.0 --port 9000
```

Open the dashboard in a browser:
- `http://<listener-ip>:9000`

## Installation (target VM: Windows and Ubuntu)

Pre-requirements:
- Python 3.9+
- Tkinter available
  - Ubuntu: `sudo apt-get install python3-tk`
  - Windows: Tkinter usually comes with the official Python installer

Run the game:
```bash
python run_rca_defender.py --repo-url http://<server-ip>:8000 --listener-url http://<listener-ip>:9000
```

## Gameplay process

1) The game shows a **Consent & Safety Notice** explaining:
   - what will happen (downloads, telemetry),
   - what will **not** happen (no backdoor, no remote shell, no stealth persistence),
   - how to remove everything (Cleaner tool).

2) Dependency/resource checks:
   - Checks Python version and Tkinter availability.
   - Checks whether offline bundles are already installed in the app data directory.
   - If missing, downloads bundles from the **local server** and installs them (unzips into app data).

3) No interruption while playing (safe approach):
   - The game runs fullscreen by default.
   - If the window loses focus, the game **pauses itself** (no OS blocking).
   - Press `Esc` to pause/resume (also exits fullscreen during pause).

4) Listener access (safe alternative):
   - Instead of a remote shell, the listener receives **telemetry events**:
     - game started/finished,
     - round started,
     - player choices and correctness.
   - This is enough to demonstrate monitoring and “command & control” concepts safely.

## Cleaner / removal tool

To remove local files created by the game:
```bash
python tools/cleaner.py
```

Dry-run (prints what would be removed):
```bash
python tools/cleaner.py --dry-run
```

## Attack prevention (what defenders should do in real life)

How real backdoors/persistence are detected and prevented (high-level):
- Use EDR/antivirus and keep OS/software patched.
- Monitor startup locations (Windows Run keys, Startup folder, Scheduled Tasks; Linux systemd user services, cron).
- Use least privilege and application allowlisting.
- Monitor network egress (unexpected outbound connections, unknown domains/IPs).
- Centralize logs (Windows Event Logs, Syslog) and alert on anomalies.
- Require code signing and verify installers and update channels.

## Ethical considerations

- Only test in systems you own or have explicit permission to test.
- Use isolated VMs, snapshots, and a closed network for classroom demos.
- Avoid building or distributing code that enables unauthorized access.
- Prefer simulations (like this project) for learning objectives.

