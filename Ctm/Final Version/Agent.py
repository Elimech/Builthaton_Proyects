from google import genai
import os

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3-flash-preview"


def Z_to_text(Z: dict, max_commits=200) -> str:
    lines = []

    repo = Z["repo"]
    timeline = Z["timeline"][:max_commits]

    lines.append("=== REPOSITORY INFO ===")
    lines.append(f"Path: {repo['path']}")
    lines.append(f"HEAD: {repo['head']}")
    lines.append(f"Total commits: {repo['total_commits']}\n")

    for c in timeline:
        lines.append(f"=== COMMIT {c['index']} ===")
        lines.append(f"Hash: {c['hash']}")
        lines.append(f"Author: {c['author']}")
        lines.append(f"Date: {c['date']}")
        lines.append(f"Message: {c['message']}\n")

        stats = c["stats"]
        lines.append(
            f"Stats: Files {stats['files_changed']}, "
            f"+{stats['insertions']} -{stats['deletions']}"
        )

        lines.append("Files:")
        for f in c["files"]:
            lines.append(f"- {f}")

        lines.append("Diff summary:")
        for s in c["diff"]["summary"]:
            lines.append(s)

        lines.append("\n" + "-" * 60 + "\n")

    return "\n".join(lines)


def answer_question(Z: dict, question: str) -> str:
    context = Z_to_text(Z)

    prompt = f"""
You are a senior software engineer AI.

You have FULL access to a repository history.

Rules:
- Answer ONLY using the provided information
- Refer to commits by index when relevant
- Do NOT hallucinate missing data

--- REPOSITORY DATA ---
{context}

User question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )

    return response.text
