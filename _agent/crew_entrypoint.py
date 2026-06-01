from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from modes.manual_mode import run_pipeline


def kickoff(inputs: dict[str, Any] | None = None) -> dict[str, str | None]:
    load_dotenv()
    inputs = inputs or {}
    transcript = _resolve_transcript(inputs)
    result = run_pipeline(transcript, push_to_github=False)
    return {
        "client_proposal": str(result["pdf_path"]),
        "engineering_spec": str(result["md_path"]),
        "github_url": result["repo_url"],
    }


def _resolve_transcript(inputs: dict[str, Any]) -> str:
    if inputs.get("transcript"):
        return str(inputs["transcript"])

    path_value = inputs.get("transcript_path")
    if path_value:
        path = Path(str(path_value)).expanduser()
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore")

    return (
        "Client: TBD. The discovery call transcript was not provided. "
        "Generate a draft with open questions and clear placeholders."
    )
