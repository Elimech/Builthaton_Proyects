from git import Repo


def analyze_git_history(repo_path):
    repo = Repo(repo_path)
    Commit_Data_List = []

    for commit in repo.iter_commits():
        diff_text = ""

        if commit.parents:
            diff = commit.parents[0].diff(commit, create_patch=True)
            for d in diff:
                if d.diff:
                    diff_text += d.diff.decode("utf-8", "replace")

        Commit_Data_List.append({
            "author": str(commit.author),
            "date": commit.committed_datetime,
            "hash": commit.hexsha,
            "message": commit.message.strip(),
            "stats": commit.stats.total,
            "diff": diff_text
        })

    return Commit_Data_List


def clean_diff(diff_text):
    lines = diff_text.splitlines()
    result = []

    for line in lines:
        if line.startswith("+"):
            result.append(f"ADD {line[1:200]}")
        elif line.startswith("-"):
            result.append(f"DEL {line[1:200]}")

        if len(result) >= 20:
            break

    return "\n".join(result)


def build_Z(repo_path):
    commits = analyze_git_history(repo_path)
    Z = []

    for commit in commits:
        Z.append(f"""
=== Commit Details ===
Commit Hash: {commit['hash']}
Author: {commit['author']}
Date: {commit['date']}
Message: {commit['message']}
Stats: {commit['stats']}
Code Diff:
{clean_diff(commit['diff'])}
""")

    return reversed(Z)


# for i in build_Z("C:/Study/2026/Works/Buildathon/Codebas_Time_Machine/Pinshi_Clonado"):
#     print(i)
