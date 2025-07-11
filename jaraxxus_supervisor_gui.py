#!/usr/bin/env python3
# jaraxxus_supervisor_gui.py – GUI for the Jaraxxus Supervisor

# Dark-mode palette
BG_DARK   = "#000000"
BG_PANEL  = "#1e1e1e"
BG_CHAT   = "#2a2a2a"
FG_USER   = "#3DA5FF"
FG_GEMINI = "#FF973D" # Renamed from FG_BOT
FG_TEXT   = "#FFFFFF"

import tkinter as tk
from tkinter import scrolledtext, ttk
from threading import Thread
from queue import Queue, Empty
import atexit

# ---- core supervisor + config ------------------------------------
from jaraxxus_supervisor import JaraxxusSupervisor
from core.app_config import settings

# ---- GUI -----------------------------------------------------
root = tk.Tk()
root.title("Jaraxxus Supervisor")
root.configure(bg=BG_PANEL)
root.geometry("1280x720")

# ---- Communication Queues ----------------------------------
command_queue = Queue()
update_queue = Queue()

# ---- Supervisor Instance -----------------------------------
supervisor = JaraxxusSupervisor(command_queue, update_queue)
# Run the supervisor's main loop in a background thread
supervisor_thread = Thread(target=supervisor.run_in_background, daemon=True)
supervisor_thread.start()

# Register supervisor.stop() to be called when the GUI closes
atexit.register(supervisor.stop)

# -- LEFT: chat -----------------------------------------------
chat_frame = tk.Frame(root, bg=BG_CHAT)
chat_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

chat_log = scrolledtext.ScrolledText(
    chat_frame, bg=BG_DARK, fg=FG_TEXT,
    insertbackground=FG_TEXT, font=("Consolas", 11), state="disabled"
)
chat_log.pack(fill="both", expand=True)
chat_log.tag_config("user", foreground=FG_USER)
chat_log.tag_config("gemini", foreground=FG_GEMINI)
chat_log.tag_config("error", foreground="#FF5555", font=("Consolas", 11, "bold"))
chat_log.tag_config("thinking", foreground="#888888")


input_entry = tk.Entry(chat_frame, bg="#3D3D3D", fg=FG_TEXT, font=("Consolas", 12))
input_entry.pack(fill="x", padx=4, pady=4)

# -- RIGHT: sidebar -------------------------------------------
side = tk.Frame(root, bg=BG_PANEL, width=280)
side.pack(side="right", fill="y")

# ---- [REMOVED] Model Picker Section ----
# This is no longer needed as the "model" is the Gemini CLI agent.
tk.Label(side, text="Agent: Gemini CLI", bg=BG_PANEL, fg=FG_GEMINI, font=("Consolas", 11, "bold")
).pack(anchor="w", padx=4, pady=(6,2))


# permissions toggles (still useful for the GEMINI.md context)
tk.Label(side, text="Permissions", bg=BG_PANEL, fg=FG_GEMINI,
         font=("Consolas", 11, "bold")).pack(anchor="w", padx=4, pady=(10,2))

perm_vars = {}
for flag in ["ALLOW_FILE_CREATE", "ALLOW_FILE_DELETE",
             "ALLOW_RUN_SCRIPTS", "ALLOW_SUDO", "ALLOW_NETWORK"]:
    v = tk.BooleanVar(value=settings.get(flag, True))
    perm_vars[flag] = v
    v = tk.BooleanVar(value=settings.get(flag, True))
perm_vars[flag] = v
def _make_toggle(flag_name, var=v):
    return lambda: (settings.__setitem__(flag_name, var.get())) # Simpler for now
    tk.Checkbutton(side, text=flag.replace("_"," ").title(),
                   variable=v, bg=BG_PANEL, fg=FG_TEXT,
                   selectcolor=BG_CHAT, command=_make_toggle(flag)
    ).pack(anchor="w", padx=12)


# ---- [MODIFIED] Tools Section ----
tk.Label(side, text="Tool Management", bg=BG_PANEL, fg=FG_GEMINI,
         font=("Consolas", 11, "bold")).pack(anchor="w", padx=4, pady=(10,2))

def list_tools():
    """Sends the 'list_tools' command to the supervisor."""
    command_queue.put("list_tools")

tk.Button(side, text="List Available Tools", command=list_tools
).pack(pady=4, fill="x", padx=6)


# -- LOG panel (now combined with main chat) -------------------
# The real-time output from Gemini CLI will be shown directly in the main chat log.
# We can repurpose the log_view for something else or remove it. For now, let's remove it.

# ---- background queue poller for GUI updates -----------------
def poll_update_queue():
    try:
        while True:
            line = update_queue.get_nowait()
            chat_log.config(state="normal")

            tag = "gemini" # Default tag
            if "Thinking..." in line:
                tag = "thinking"
            elif "[SUPERVISOR_ERROR]" in line:
                tag = "error"

            chat_log.insert("end", line, (tag,))
            chat_log.config(state="disabled")
            chat_log.see("end")

    except Empty:
        pass
    root.after(100, poll_update_queue)

poll_update_queue()

# ---- send / enter key binding -------------------------------
def send():
    msg = input_entry.get().strip()
    if not msg:
        return
    input_entry.delete(0, "end")
    chat_log.config(state="normal")
    chat_log.insert("end", f"[User] {msg}\n", ("user",))
    chat_log.config(state="disabled")
    chat_log.see("end")

    # Put the user's message into the command queue for the supervisor
    command_queue.put(msg)

input_entry.bind("<Return>", lambda e: send())
tk.Button(chat_frame, text="Send", command=send, bg=FG_GEMINI).pack(pady=2)

# ---- start ---------------------------------------------------
root.mainloop()
