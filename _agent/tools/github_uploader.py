from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

from git import Repo


def upload_to_github(client_name: str, repo_name: str = "discovery-agent") -> str | None:
    root = Path.cwd()
    repo = Repo.init(root) if not (root / ".git").exists() else Repo(root)
    _ensure_gitignore(root)

    repo.git.add(A=True)
    if repo.is_dirty(untracked_files=True):
        message = f"discovery-agent: {client_name} - {datetime.now():%Y-%m-%d}"
        repo.index.commit(message)

    remotes = [remote.name for remote in repo.remotes]
    if "origin" not in remotes:
        if not _command_exists("gh"):
            print("GitHub CLI not found. Install gh or add a remote manually.")
            return None
        subprocess.run(["gh", "repo", "create", repo_name, "--public", "--source=.", "--push"], check=True)
    else:
        branch = repo.active_branch.name
        if branch != "main":
            try:
                repo.git.branch("-M", "main")
            except Exception:
                pass
        repo.git.push("origin", "main")

    return _remote_url(repo)


def _ensure_gitignore(root: Path) -> None:
    required = [
        ".env",
        ".chromadb/",
        "output/",
        "__pycache__/",
        "*.pyc",
        "venv/",
        ".venv/",
        "/tmp/chunk_*.wav",
    ]
    path = root / ".gitignore"
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    merged = existing + [item for item in required if item not in existing]
    path.write_text("\n".join(merged) + "\n", encoding="utf-8")


def _command_exists(command: str) -> bool:
    return subprocess.run(["which", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def _remote_url(repo: Repo) -> str | None:
    if "origin" not in [remote.name for remote in repo.remotes]:
        return None
    url = repo.remotes.origin.url
    if url.startswith("git@github.com:"):
        return "https://github.com/" + url.removeprefix("git@github.com:").removesuffix(".git")
    return url.removesuffix(".git")
