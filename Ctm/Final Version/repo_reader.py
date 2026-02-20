from git import Repo

def summarize_diff(diff_text, max_lines=40):
    summary = []

    for line in diff_text.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue

        if line.startswith("+"):
            summary.append(f"ADD {line[1:200]}")
        elif line.startswith("-"):
            summary.append(f"DEL {line[1:200]}")

        if len(summary) >= max_lines:
            break

    return summary


def build_Z(repo_path):
    repo = Repo(repo_path)
    commits = list(repo.iter_commits())
    commits.reverse()

    Z = {
        "repo": {
            "path": repo_path,
            "head": repo.head.commit.hexsha,
            "total_commits": len(commits)
        },
        "timeline": []
    }

    for i, commit in enumerate(commits, start=1):
        full_diff = ""

        if commit.parents:
            diff = commit.parents[0].diff(commit, create_patch=True)
            for d in diff:
                if d.diff:
                    full_diff += d.diff.decode("utf-8", "replace")

        Z["timeline"].append({
            "index": i,
            "hash": commit.hexsha,
            "author": str(commit.author),
            "date": commit.committed_datetime.isoformat(),
            "message": commit.message.strip(),
            "is_initial": not commit.parents,
            "stats": {
                "files_changed": len(commit.stats.files),
                "insertions": commit.stats.total.get("insertions", 0),
                "deletions": commit.stats.total.get("deletions", 0),
            },
            "files": list(commit.stats.files.keys()),
            "diff": {
                "summary": summarize_diff(full_diff),
                "patch": full_diff[:15000]
            }
        })

    return Z
