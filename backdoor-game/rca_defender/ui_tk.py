from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ConsentResult:
    accepted: bool
    allow_downloads: bool


def show_consent_dialog(app_title: str) -> ConsentResult:
    root = tk.Tk()
    root.title(app_title)
    root.geometry("760x520")
    root.resizable(False, False)

    accepted_var = tk.BooleanVar(value=False)
    downloads_var = tk.BooleanVar(value=True)

    header = tk.Label(
        root,
        text="Consent & Safety Notice",
        font=("Segoe UI", 18, "bold"),
        pady=12,
    )
    header.pack()

    msg = (
        "This game is for cybersecurity awareness and classroom demos in a VM.\n\n"
        "What it DOES:\n"
        "- Runs a local game and teaches defensive decisions.\n"
        "- Optionally downloads offline game resources from your class local server.\n"
        "- Optionally sends harmless gameplay telemetry to a teacher dashboard.\n\n"
        "What it DOES NOT do:\n"
        "- No backdoor, no remote shell, no stealth persistence.\n"
        "- No data theft. No hidden changes.\n\n"
        "You can remove everything later using the Cleaner tool."
    )

    text = tk.Text(root, height=16, wrap="word")
    text.insert("1.0", msg)
    text.config(state="disabled", padx=12, pady=12)
    text.pack(fill="both", expand=True, padx=16, pady=8)

    downloads = tk.Checkbutton(
        root,
        text="Allow downloading offline resources from the local class server (recommended)",
        variable=downloads_var,
    )
    downloads.pack(anchor="w", padx=18, pady=6)

    buttons = tk.Frame(root)
    buttons.pack(fill="x", padx=16, pady=12)

    def on_accept() -> None:
        accepted_var.set(True)
        root.destroy()

    def on_decline() -> None:
        accepted_var.set(False)
        root.destroy()

    tk.Button(buttons, text="Decline", width=14, command=on_decline).pack(
        side="right", padx=8
    )
    tk.Button(buttons, text="Accept", width=14, command=on_accept).pack(side="right")

    root.mainloop()
    return ConsentResult(
        accepted=bool(accepted_var.get()),
        allow_downloads=bool(downloads_var.get()),
    )


def show_blocking_error(title: str, message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("640x240")
    win.resizable(False, False)

    label = tk.Label(win, text=message, justify="left", wraplength=600, padx=16, pady=16)
    label.pack(fill="both", expand=True)

    def close() -> None:
        win.destroy()
        root.destroy()

    tk.Button(win, text="Close", width=14, command=close).pack(pady=12)
    win.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


def run_game_window(
    *,
    app_title: str,
    scenarios: list[dict],
    telemetry_emit: Callable[[str, dict], None],
    fullscreen: bool,
) -> None:
    root = tk.Tk()
    root.title(app_title)
    root.configure(bg="#0b1220")
    root.geometry("960x640")

    if fullscreen:
        root.attributes("-fullscreen", True)

    paused = {"value": False}
    idx = {"value": 0}
    score = {"value": 0}

    container = tk.Frame(root, bg="#0b1220")
    container.pack(fill="both", expand=True, padx=18, pady=18)

    title = tk.Label(
        container,
        text="Defending Rwanda Cyberspace",
        font=("Segoe UI", 22, "bold"),
        fg="#e7efff",
        bg="#0b1220",
    )
    title.pack(anchor="w")

    subtitle = tk.Label(
        container,
        text="Choose the safest defensive action for each scenario.",
        font=("Segoe UI", 12),
        fg="#b9c7e6",
        bg="#0b1220",
        pady=8,
    )
    subtitle.pack(anchor="w")

    score_label = tk.Label(
        container,
        text="Score: 0",
        font=("Consolas", 12, "bold"),
        fg="#9ae6b4",
        bg="#0b1220",
    )
    score_label.pack(anchor="w", pady=(0, 10))

    scenario_title = tk.Label(
        container,
        text="",
        font=("Segoe UI", 16, "bold"),
        fg="#e7efff",
        bg="#0b1220",
        pady=10,
    )
    scenario_title.pack(anchor="w")

    scenario_body = tk.Label(
        container,
        text="",
        font=("Segoe UI", 13),
        fg="#d6def0",
        bg="#0b1220",
        justify="left",
        wraplength=920,
    )
    scenario_body.pack(anchor="w", pady=(0, 14))

    feedback = tk.Label(
        container,
        text="",
        font=("Segoe UI", 12),
        fg="#ffd166",
        bg="#0b1220",
        justify="left",
        wraplength=920,
    )
    feedback.pack(anchor="w", pady=(0, 14))

    actions = tk.Frame(container, bg="#0b1220")
    actions.pack(anchor="w", pady=10)

    next_btn = tk.Button(container, text="Next", width=14, state="disabled")
    next_btn.pack(anchor="e", pady=10)

    def set_feedback(text: str) -> None:
        feedback.config(text=text)

    def load_scenario() -> None:
        set_feedback("")
        next_btn.config(state="disabled")
        i = idx["value"]
        if i >= len(scenarios):
            telemetry_emit("game_finished", {"score": score["value"], "total": len(scenarios)})
            show_end()
            return
        sc = scenarios[i]
        scenario_title.config(text=f"Round {i + 1}/{len(scenarios)} — {sc['title']}")
        scenario_body.config(text=sc["prompt"])
        telemetry_emit("round_started", {"round": i + 1, "title": sc["title"]})

    def answer(choice_key: str) -> None:
        i = idx["value"]
        sc = scenarios[i]
        correct = sc["correct"] == choice_key
        if correct:
            score["value"] += 1
            score_label.config(text=f"Score: {score['value']}")
        explanation = sc["explain_allow"] if choice_key == "allow" else sc["explain_block"]
        outcome = "Correct" if correct else "Not ideal"
        set_feedback(f"{outcome}. {explanation}")
        telemetry_emit(
            "round_answer",
            {"round": i + 1, "choice": choice_key, "correct": correct},
        )
        next_btn.config(state="normal")

    def next_round() -> None:
        idx["value"] += 1
        load_scenario()

    def show_end() -> None:
        for w in container.winfo_children():
            w.destroy()
        tk.Label(
            container,
            text="Mission complete",
            font=("Segoe UI", 24, "bold"),
            fg="#e7efff",
            bg="#0b1220",
            pady=10,
        ).pack(anchor="w")
        tk.Label(
            container,
            text=f"Final score: {score['value']} / {len(scenarios)}",
            font=("Consolas", 16, "bold"),
            fg="#9ae6b4",
            bg="#0b1220",
            pady=10,
        ).pack(anchor="w")
        tk.Label(
            container,
            text=(
                "This game simulates defensive decisions.\n"
                "For real systems, always follow your organization’s policies and laws."
            ),
            font=("Segoe UI", 12),
            fg="#b9c7e6",
            bg="#0b1220",
            pady=8,
            justify="left",
        ).pack(anchor="w")

        def quit_game() -> None:
            root.destroy()

        tk.Button(container, text="Exit", width=14, command=quit_game).pack(
            anchor="e", pady=12
        )

    allow_btn = tk.Button(
        actions,
        text="Allow (Safe)",
        width=18,
        command=lambda: answer("allow"),
        bg="#1f6feb",
        fg="white",
        activebackground="#2f81f7",
    )
    allow_btn.pack(side="left", padx=(0, 10))

    block_btn = tk.Button(
        actions,
        text="Block (Defend)",
        width=18,
        command=lambda: answer("block"),
        bg="#238636",
        fg="white",
        activebackground="#2ea043",
    )
    block_btn.pack(side="left")

    next_btn.config(command=next_round)

    def on_escape(_: object = None) -> None:
        if paused["value"]:
            paused["value"] = False
            root.attributes("-fullscreen", fullscreen)
            telemetry_emit("resume", {})
            return
        paused["value"] = True
        telemetry_emit("pause", {})
        # Minimal pause effect: exit fullscreen and show an exit confirm.
        root.attributes("-fullscreen", False)
        set_feedback("Paused. Press ESC again to resume. Close window to exit.")

    root.bind("<Escape>", on_escape)

    def on_focus_out(_: object = None) -> None:
        # No OS-level blocking: just pause internally.
        if not paused["value"]:
            paused["value"] = True
            telemetry_emit("pause_focus_lost", {})
            root.attributes("-fullscreen", False)
            set_feedback("Paused (focus lost). Click the game window and press ESC to resume.")

    root.bind("<FocusOut>", on_focus_out)

    telemetry_emit("game_started", {"total_rounds": len(scenarios)})
    load_scenario()
    root.mainloop()

