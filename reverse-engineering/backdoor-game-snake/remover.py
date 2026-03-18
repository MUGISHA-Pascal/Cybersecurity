"""
**EDUCATIONAL DEMO ONLY – Rwanda Coding Academy Assignment**
Use exclusively in isolated VMs. Never deploy on real systems.
This code demonstrates backdoor techniques for defense learning purposes.

Remover: removes persistence and files added by the backdoor game.
Compile to remover.exe and run on the target VM to clean up.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

if sys.platform == "win32":
    import winreg

APPDATA_EXE_NAME = "SystemUpdateService.exe"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "SystemUpdateService"


def get_appdata_exe_path():
    return os.path.join(os.environ.get("APPDATA", ""), APPDATA_EXE_NAME)


def remove_registry_key():
    if sys.platform != "win32":
        return True, "N/A (not Windows)"
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, VALUE_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True, "Registry Run key removed."
    except Exception as e:
        return False, str(e)


def remove_appdata_exe():
    path = get_appdata_exe_path()
    if not os.path.isfile(path):
        return True, "No copy in APPDATA (already removed or never installed)."
    try:
        os.remove(path)
        return True, f"Removed: {path}"
    except Exception as e:
        return False, str(e)


def do_cleanup():
    results = []
    ok1, msg1 = remove_registry_key()
    results.append(("Registry", ok1, msg1))
    ok2, msg2 = remove_appdata_exe()
    results.append(("APPDATA exe", ok2, msg2))
    return results


def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    msg = (
        "This will remove the educational backdoor demo:\n\n"
        "• Delete the Run key (SystemUpdateService)\n"
        "• Remove the copied executable from %APPDATA%\n\n"
        "Continue?"
    )
    if not messagebox.askyesno("Backdoor Remover – Confirm", msg, icon="question"):
        root.destroy()
        return
    root.destroy()

    results = do_cleanup()
    lines = []
    all_ok = True
    for name, ok, detail in results:
        status = "OK" if ok else "FAILED"
        if not ok:
            all_ok = False
        lines.append(f"{name}: {status} – {detail}")

    root2 = tk.Tk()
    root2.title("Remover Result")
    root2.geometry("500x200")
    root2.configure(bg="#1a1a2e")
    text = "\n".join(lines)
    lbl = tk.Label(
        root2,
        text=text,
        font=("Segoe UI", 10),
        fg="#eaeaea",
        bg="#1a1a2e",
        justify="left",
    )
    lbl.pack(padx=20, pady=20, anchor="w")
    if all_ok:
        tk.Label(
            root2,
            text="Cleanup completed successfully.",
            font=("Segoe UI", 10),
            fg="#4ecca3",
            bg="#1a1a2e",
        ).pack(pady=5)
    tk.Button(
        root2,
        text="Close",
        command=root2.destroy,
        bg="#e94560",
        fg="white",
        relief="flat",
        padx=15,
        pady=5,
    ).pack(pady=10)
    root2.mainloop()


if __name__ == "__main__":
    main()
