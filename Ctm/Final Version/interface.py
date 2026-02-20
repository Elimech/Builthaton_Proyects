import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from git import Repo, InvalidGitRepositoryError

from repo_reader import build_Z
from Agent import answer_question, Z_to_text


# ===============================
# CUSTOM RED BUTTON
# ===============================
class RedButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            bg="#c1121f",
            fg="white",
            activebackground="#ff2e2e",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            **kwargs
        )


# ===============================
# MAIN APP
# ===============================
class CTMApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Codebase Time Machine")
        self.root.geometry("1300x750")
        self.root.configure(bg="#0b0b0b")

        self.Z = None
        self.build_repo_selector()

    # =====================================
    # STEP 1 — REPO SELECTOR
    # =====================================
    def build_repo_selector(self):
        self.selector = tk.Frame(self.root, bg="#0b0b0b")
        self.selector.pack(fill="both", expand=True)

        tk.Label(
            self.selector,
            text="Select a Git Repository",
            bg="#0b0b0b",
            fg="#ff3b3b",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=30)

        self.repo_path = tk.StringVar()

        entry = tk.Entry(
            self.selector,
            textvariable=self.repo_path,
            font=("Consolas", 11),
            width=80,
            bg="#1a1a1a",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        entry.pack(pady=10)

        RedButton(
            self.selector,
            text="Browse",
            command=self.browse_repo
        ).pack(pady=5)

        RedButton(
            self.selector,
            text="Analyze Repository",
            command=self.start_analysis
        ).pack(pady=20)

    def browse_repo(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path.set(path)

    def start_analysis(self):
        path = self.repo_path.get().strip()
        if not path:
            messagebox.showwarning("Error", "Select a folder")
            return

        try:
            Repo(path)
        except InvalidGitRepositoryError:
            messagebox.showerror("Error", "Not a valid Git repository")
            return

        self.selector.destroy()
        self.build_main_ui()

        threading.Thread(
            target=self.load_repository,
            args=(path,),
            daemon=True
        ).start()

    # =====================================
    # STEP 2 — MAIN UI
    # =====================================
    def build_main_ui(self):

        self.main = tk.Frame(self.root, bg="#0b0b0b")
        self.main.pack(fill="both", expand=True)

        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=1)
        self.main.rowconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=0)  # fila para reset

        # ===== LEFT PANEL =====
        left_frame = tk.Frame(self.main, bg="#111111")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.commits_text = tk.Text(
            left_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#111111",
            fg="#e6e6e6",
            insertbackground="white",
            relief="flat",
            state="disabled"
        )
        self.commits_text.pack(side="left", fill="both", expand=True)

        scrollbar_left = tk.Scrollbar(left_frame, command=self.commits_text.yview)
        scrollbar_left.pack(side="right", fill="y")
        self.commits_text.config(yscrollcommand=scrollbar_left.set)

        # ===== RIGHT PANEL =====
        right_frame = tk.Frame(self.main, bg="#111111")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        self.answer_text = tk.Text(
            right_frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#111111",
            fg="white",
            insertbackground="white",
            relief="flat",
            state="disabled"
        )
        self.answer_text.grid(row=0, column=0, sticky="nsew")

        scrollbar_right = tk.Scrollbar(right_frame, command=self.answer_text.yview)
        scrollbar_right.grid(row=0, column=1, sticky="ns")
        self.answer_text.config(yscrollcommand=scrollbar_right.set)

        # ===== QUESTION BAR =====
        bottom = tk.Frame(right_frame, bg="#0b0b0b")
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        bottom.columnconfigure(0, weight=1)

        self.question_entry = tk.Entry(
            bottom,
            font=("Segoe UI", 11),
            bg="#1a1a1a",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.question_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.question_entry.bind("<Return>", lambda e: self.ask_ai())

        RedButton(
            bottom,
            text="Ask",
            command=self.ask_ai
        ).grid(row=0, column=1)

        # ===== RESET BUTTON =====
        RedButton(
            self.main,
            text="Reset",
            command=self.reset_app
        ).grid(row=1, column=0, columnspan=2, pady=15)

        self.configure_tags()

    # =====================================
    # RESET FUNCTION
    # =====================================
    def reset_app(self):
        self.main.destroy()
        self.Z = None
        self.build_repo_selector()

    # =====================================
    # (EL RESTO DEL CÓDIGO SIGUE IGUAL)
    # =====================================

    def configure_tags(self):

        self.commits_text.tag_config("header", foreground="#ff3b3b",
                                     font=("Consolas", 11, "bold"))

        self.commits_text.tag_config("meta", foreground="#888888")
        self.commits_text.tag_config("add", foreground="#00e676")
        self.commits_text.tag_config("del", foreground="#ff5252")
        self.commits_text.tag_config("separator", foreground="#444444")

        self.answer_text.tag_config("thinking",
                                    foreground="#ff9800",
                                    font=("Segoe UI", 11, "italic"))

    def load_repository(self, path):
        self.Z = build_Z(path)
        text = Z_to_text(self.Z)

        self.commits_text.config(state="normal")
        self.commits_text.delete("1.0", "end")
        self.commits_text.insert("1.0", text)
        self.highlight_commits()
        self.commits_text.config(state="disabled")

    def highlight_commits(self):
        lines = self.commits_text.get("1.0", "end").split("\n")

        index = "1.0"
        for line in lines:
            line_end = f"{index} lineend"

            if "=== COMMIT" in line:
                self.commits_text.tag_add("header", index, line_end)

            elif line.startswith(("Hash", "Author", "Date")):
                self.commits_text.tag_add("meta", index, line_end)

            elif line.startswith("ADD"):
                self.commits_text.tag_add("add", index, line_end)

            elif line.startswith("DEL"):
                self.commits_text.tag_add("del", index, line_end)

            elif "-----" in line:
                self.commits_text.tag_add("separator", index, line_end)

            index = self.commits_text.index(f"{index} +1line")

    def ask_ai(self):
        if not self.Z:
            return

        question = self.question_entry.get().strip()
        if not question:
            return

        self.question_entry.delete(0, "end")

        self.answer_text.config(state="normal")
        self.answer_text.insert("end", "\n🧠 Thinking...\n", "thinking")
        self.answer_text.config(state="disabled")

        threading.Thread(
            target=self.run_ai,
            args=(question,),
            daemon=True
        ).start()

    def run_ai(self, question):
        answer = answer_question(self.Z, question)
        answer = self.clean_markdown(answer)

        self.answer_text.config(state="normal")
        self.answer_text.insert("end", "\n" + answer + "\n\n")
        self.answer_text.config(state="disabled")
        self.answer_text.see("end")


    def clean_markdown(self, text):

        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()      

            if line.startswith("#"):
                line = line.lstrip("#").strip()

            if line.startswith("* "):
                line = "• " + line[2:]

            line = line.replace("**", "")
            line = line.replace("*", "")

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)



# =====================================
# RUN
# =====================================
if __name__ == "__main__":
    root = tk.Tk()
    app = CTMApp(root)
    root.mainloop()
