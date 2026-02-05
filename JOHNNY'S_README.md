# 🕰️ Codebase Time Machine

**Codebase Time Machine** is a desktop application that analyzes the evolution of a Git repository commit by commit and allows users to ask questions about the project history using AI.

The goal is to **understand why changes happened**, not just what changed.

---

## ✨ Features

### 🔍 Commit-by-Commit Analysis

* Iterates through the repository history
* Analyzes each commit individually
* Produces a human-readable explanation of:

  * Purpose of the change
  * Impact on the codebase
  * Architectural or design implications

### 🧠 AI-Powered Questions

* Ask natural language questions about the analyzed history
* The AI answers based **only on the previously generated analysis context**
* Example questions:

  * *Why did the architecture change after commit 3?*
  * *What problem was solved by this refactor?*
  * *When was X feature introduced and why?*

### 🖥️ Desktop UI (Tkinter)

* Dark-themed interface
* Repository selector
* Progress bar during analysis
* Styled and readable output
* Integrated question input bar

---

## 🧱 Project Structure

```
App/
├── GitTimeMachine.py        # Entry point
├── Files/
│   └── Interface.py         # Tkinter UI
├── Logic/
│   ├── CTM.py               # Builds commit timeline (Z)
│   ├── Agent.py             # AI analysis and Q&A logic
│   └── Text_Formater.py     # Markdown/text cleanup & tagging
```

---

## 🚀 How It Works

1. Select a local Git repository
2. The app builds a chronological list of commits
3. Each commit is analyzed independently by the AI
4. The analysis is stored as context
5. Users can ask questions based on that context
6. Answers are generated without re-analyzing the repository

---

## ▶️ How to Run

From the project root:

```powershell
python -m App.GitTimeMachine
```

---

## 🧪 Current Capabilities

* ✔ Git repository validation
* ✔ Threaded analysis (UI remains responsive)
* ✔ Styled output with semantic tags
* ✔ Question & answer system based on analysis context
* ✔ Reset and re-analysis support

---

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** – GUI
* **GitPython** – Git interaction
* **Threading** – Non-blocking UI
* **AI Agent (LLM)** – Commit analysis & Q&A

---

## 📄 License

This project is for educational and experimental purposes.

---
