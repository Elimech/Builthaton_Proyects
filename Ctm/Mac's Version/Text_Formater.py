def clean_markdown(text: str) -> list[tuple[str, str]]:
    """
    Convert text type Markdown into blocks (text, tag)
    """
    lines = text.splitlines()
    formatted = []

    for line in lines:
        line = line.rstrip()

        if not line.strip():
            formatted.append(("\n", "normal"))
            continue

        # --- Separators
        if line.strip() in ("---", "___"):
            formatted.append(("\n", "normal"))
            continue

        # ### Titles
        if line.startswith("###"):
            formatted.append(
                (line.replace("###", "").strip() + "\n", "section"))
            continue

        # **Subtitles**
        if line.startswith("**") and line.endswith("**"):
            formatted.append(
                (line.replace("**", "").strip() + "\n", "commit_title"))
            continue

        # * Lists
        if line.startswith("* "):
            formatted.append(("• " + line[2:] + "\n", "normal"))
            continue

        # Normal text
        formatted.append((line + "\n", "normal"))

    return formatted
