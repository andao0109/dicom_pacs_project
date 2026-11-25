import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk


# ==============================
# Main Window
# ==============================

root = tk.Tk()
root.title("DICOM PACS Controller")
root.geometry("900x620")
root.minsize(800, 550)
root.configure(bg="#F1F5F9")


# ==============================
# Style
# ==============================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TButton",
    font=("Segoe UI", 10),
    padding=10
)

style.configure(
    "Title.TLabel",
    font=("Segoe UI", 22, "bold"),
    background="#172033",
    foreground="white"
)

style.configure(
    "Subtitle.TLabel",
    font=("Segoe UI", 10),
    background="#172033",
    foreground="#CBD5E1"
)


# ==============================
# Header
# ==============================

header = tk.Frame(root, bg="#172033", height=110)
header.pack(fill="x")
header.pack_propagate(False)

title = ttk.Label(
    header,
    text="DICOM PACS CONTROLLER",
    style="Title.TLabel"
)
title.pack(anchor="w", padx=25, pady=(20, 5))

subtitle = ttk.Label(
    header,
    text="PACS & Teleradiology Management System",
    style="Subtitle.TLabel"
)
subtitle.pack(anchor="w", padx=27)


# ==============================
# Main Content
# ==============================

main = tk.Frame(root, bg="#F1F5F9")
main.pack(fill="both", expand=True, padx=25, pady=20)


# System Status
status_frame = tk.LabelFrame(
    main,
    text=" SYSTEM STATUS ",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    fg="#334155",
    padx=15,
    pady=12
)
status_frame.pack(fill="x", pady=(0, 15))

status_label = tk.Label(
    status_frame,
    text="Status: Not checked",
    font=("Segoe UI", 11),
    bg="white",
    fg="#64748B"
)
status_label.pack(anchor="w")

# ==============================
# System Functions
# ==============================

PROJECT_DIR = Path(__file__).resolve().parent.parent


def log_message(message):
    log_text.config(state="normal")
    log_text.insert("end", message + "\n")
    log_text.see("end")
    log_text.config(state="disabled")


def start_system():
    def worker():
        root.after(0, lambda: log_message("Starting PACS system..."))

        try:
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True
            )

            output = result.stdout + result.stderr

            root.after(
                0,
                lambda: log_message(output.strip() or "Docker command completed.")
            )

            if result.returncode == 0:
                root.after(
                    0,
                    lambda: status_label.config(
                        text="Status: Start command completed",
                        fg="#16A34A"
                    )
                )
            else:
                root.after(
                    0,
                    lambda: status_label.config(
                        text="Status: Start failed",
                        fg="#DC2626"
                    )
                )

        except Exception as e:
            root.after(0, lambda: log_message(f"Error: {e}"))

    threading.Thread(target=worker, daemon=True).start()
def check_status():
    def worker():
        root.after(0, lambda: log_message("Checking PACS system status..."))

        try:
            result = subprocess.run(
                ["docker", "compose", "ps"],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True
            )

            output = result.stdout + result.stderr

            root.after(
                0,
                lambda: log_message(output.strip() or "No containers found.")
            )

            if result.returncode == 0:
                root.after(
                    0,
                    lambda: status_label.config(
                        text="Status: Checked - see System Log",
                        fg="#16A34A"
                    )
                )
            else:
                root.after(
                    0,
                    lambda: status_label.config(
                        text="Status: Check failed",
                        fg="#DC2626"
                    )
                )

        except Exception as e:
            root.after(0, lambda: log_message(f"Error: {e}"))

    threading.Thread(target=worker, daemon=True).start()
# Control Buttons
control_frame = tk.LabelFrame(
    main,
    text=" SYSTEM CONTROL ",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    padx=15,
    pady=12
)
control_frame.pack(fill="x", pady=(0, 15))

buttons = tk.Frame(control_frame, bg="white")
buttons.pack(fill="x")

ttk.Button(
    buttons,
    text="Start System",
    command=start_system
).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

ttk.Button(
    buttons,
    text="Stop System"
).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Button(
    buttons,
    text="Check Status",
    command=check_status
).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

for i in range(3):
    buttons.columnconfigure(i, weight=1)


# DICOM Operations
dicom_frame = tk.LabelFrame(
    main,
    text=" DICOM OPERATIONS ",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    padx=15,
    pady=12
)
dicom_frame.pack(fill="x", pady=(0, 15))

dicom_buttons = tk.Frame(dicom_frame, bg="white")
dicom_buttons.pack(fill="x")

ttk.Button(
    dicom_buttons,
    text="Send Synthetic CT"
).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

ttk.Button(
    dicom_buttons,
    text="Send Real CT"
).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

for i in range(2):
    dicom_buttons.columnconfigure(i, weight=1)


# Viewer Access
viewer_frame = tk.LabelFrame(
    main,
    text=" VIEWER ACCESS ",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    padx=15,
    pady=12
)
viewer_frame.pack(fill="x", pady=(0, 15))

viewer_buttons = tk.Frame(viewer_frame, bg="white")
viewer_buttons.pack(fill="x")

ttk.Button(
    viewer_buttons,
    text="Open Orthanc"
).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

ttk.Button(
    viewer_buttons,
    text="Open OHIF"
).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

for i in range(2):
    viewer_buttons.columnconfigure(i, weight=1)


# Log Area
log_frame = tk.LabelFrame(
    main,
    text=" SYSTEM LOG ",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    padx=10,
    pady=10
)
log_frame.pack(fill="both", expand=True)

log_text = tk.Text(
    log_frame,
    height=5,
    font=("Consolas", 9),
    bg="#0F172A",
    fg="#E2E8F0",
    insertbackground="white",
    relief="flat",
    state="disabled"
)
log_text.pack(fill="both", expand=True)


# ==============================
# Run Application
# ==============================

root.mainloop()
