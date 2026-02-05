import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform
from App.Logic.CTM import build_Z
from App.Logic.Agent import analyze_commit, answer_question
from App.Logic.Text_Formater import clean_markdown
import threading
import os
import sys
from git import Repo, InvalidGitRepositoryError


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ======================
# Window
# ======================
root = tk.Tk()
root.title("Codebase Time Machine")
if platform.system() == "Windows":
    root.iconbitmap(resource_path("Icon.ico"))
root.geometry("900x650")
root.configure(bg="#1e1e1e")

# ======================
# Variables
# ======================
path_var = tk.StringVar()

# ======================
# Functions
# ======================


def select_repo():
    folder = filedialog.askdirectory()
    if folder:
        path_var.set(folder)


def reset_app():
    path_var.set("")
    output.delete("1.0", "end")
    progress.stop()
    progress.pack_forget()


def validate_repo(path):
    try:
        Repo(path)
        return True
    except InvalidGitRepositoryError:
        return False
    except Exception:
        return False


analysis_context = ""


def run_analysis():
    global analysis_context
    repo = path_var.get()
    if not repo:
        root.after(0, lambda: messagebox.showwarning(
            "Warning", "Select a repository first"))
        return

    if not validate_repo(repo):
        root.after(0, lambda: messagebox.showerror(
            "Error", "Selected folder is not a valid Git repository"))
        return

    root.after(0, start_progress)
    root.after(0, lambda: output.insert("end", "Analysis started...\n\n"))

    analysis_context = ""

    Z = build_Z(repo)
    for i, commit in enumerate(Z):
        output.insert("end", f"\nCommit {i + 1}\n", "commit_title")
        output.insert("end", "─" * 40 + "\n", "dim")

        result = analyze_commit(commit)

        if result is None:
            result = "[No response]"

        analysis_context += f"\nCommit {i + 1}\n{result}\n"
        for line, tag in clean_markdown(result):
            output.insert("end", line + "\n", tag)

    root.after(0, stop_progress)


def start_analysis():
    threading.Thread(target=run_analysis, daemon=True).start()


def start_progress():
    progress.pack(fill="x", padx=20, pady=10)
    progress.start(10)


def stop_progress():
    progress.stop()


def ask_question():
    question = question_var.get().strip()

    if not question:
        return

    if not analysis_context:
        output.insert("end", "\n⚠️ Analyze a repository first.\n")
        return

    output.insert("end", f"\n❓ Question\n", "section")
    output.insert("end", f"{question}\n", "normal")
    output.insert("end", "🤖 Thinking...\n", "dim")

    def run():
        try:
            answer = answer_question(analysis_context, question)
            output.insert("end", "\n✅ Answer\n", "section")
            output.insert("end", f"{answer}\n", "answer")

        except Exception as e:
            output.insert("end", f"\n❌ Error: {e}\n")

    threading.Thread(target=run).start()

    question_var.set("")


# ======================
# UI – Top
# ======================
tk.Label(
    root, text="Git Repository",
    bg="#1e1e1e", fg="white", font=("Segoe UI", 12, "bold")
).pack(pady=(10, 5))

path_frame = tk.Frame(root, bg="#1e1e1e")
path_frame.pack(fill="x", padx=20)

tk.Entry(
    path_frame, textvariable=path_var,
    bg="#2d2d2d", fg="white", insertbackground="white",
    relief="flat", font=("Consolas", 10)
).pack(side="left", fill="x", expand=True, padx=(0, 10))

tk.Button(
    path_frame, text="Browse",
    command=select_repo, bg="#3a3d41", fg="white",
    relief="flat"
).pack(side="right")

# ======================
# Progress Bar
# ======================
progress = ttk.Progressbar(
    root, mode="indeterminate"
)

# ======================
# Output
# ======================
frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(fill="both", expand=True, padx=20, pady=10)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side="right", fill="y")

output = tk.Text(
    frame, yscrollcommand=scrollbar.set,
    bg="#252526", fg="#d4d4d4",
    insertbackground="white",
    wrap="word", font=("Consolas", 10),
    relief="flat"
)

output.pack(side="left", fill="both", expand=True)
scrollbar.config(command=output.yview)


output.tag_configure("commit_title", font=(
    "Segoe UI", 11, "bold"), foreground="#61afef")  # FF2900
output.tag_configure("section", font=(
    "Segoe UI", 10, "bold"), foreground="#c678dd")
output.tag_configure("normal", font=("Segoe UI", 10), foreground="#e6e6e6")
output.tag_configure("dim", font=("Segoe UI", 9), foreground="#aaaaaa")
output.tag_configure("answer", font=("Segoe UI", 10), foreground="#98c379")


question_frame = tk.Frame(root, bg="#1e1e1e")
question_frame.pack(fill='x', padx=12, pady=(8, 4))

question_var = tk.StringVar()

question_entry = tk.Entry(
    question_frame,
    textvariable=question_var,
    font=("Segoe UI", 10),
    bg="#2b2b2b", fg="#e6e6e6",
    insertbackground="white",
    relief="flat"

)

question_entry.pack(side="left", fill="x", expand=True,
                    ipady=6, padx=(6, 4), pady=6)

question_entry.insert(0, "Ask something about the analysis...")
question_entry.config(fg="#888888")


def on_focus_in(event):
    if question_entry.get() == "Ask something about the analysis...":
        question_entry.delete(0, "end")
        question_entry.config(fg="#e6e6e6")


def on_focus_out(event):
    if not question_entry.get():
        question_entry.insert(0, "Ask something about the analysis...")
        question_entry.config(fg="#888888")


question_entry.bind("<FocusIn>", on_focus_in)
question_entry.bind("<FocusOut>", on_focus_out)


ask_button = tk.Button(
    question_frame,
    text="Ask",
    command=lambda: ask_question(),
    bg="#3a3a3a", fg="white",
    activebackground="#505050",
    activeforeground="white",
    relief="flat",
    font=("Segoe UI", 9, "bold"),
    padx=12,
    pady=4
)

ask_button.pack(side="right", padx=(4, 6), pady=6)

# ======================
# Buttons
# ======================
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

tk.Button(
    btn_frame, text="Analyze Repo",
    command=start_analysis,
    bg="#FF0000", fg="white",
    relief="flat", width=15
).pack(side="left", padx=10)

tk.Button(
    btn_frame, text="Reset",
    command=reset_app,
    bg="#3a3d41", fg="white",
    relief="flat", width=10
).pack(side="left")

# ======================
root.mainloop()
