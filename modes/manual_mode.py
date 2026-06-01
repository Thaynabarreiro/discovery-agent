from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import SpinnerColumn, TextColumn, Progress

from _agent.agents.crew import run_discovery_crew
from _agent.agents.intake_parser import IntakeParser
from _agent.agents.proposal_drafter import ProposalDrafter
from _agent.agents.scope_estimator import ScopeEstimator
from _agent.agents.solution_architect import SolutionArchitect
from _agent.tools.github_uploader import upload_to_github
from _agent.tools.markdown_generator import generate_engineering_spec
from _agent.tools.pdf_generator import generate_client_proposal


console = Console()


def run_manual_mode() -> None:
    transcript = _read_transcript()
    if not transcript.strip():
        console.print("[red]No transcript provided.[/red]")
        return
    result = run_pipeline(transcript)
    _print_result(result)


def run_pipeline(transcript: str, push_to_github: bool = True) -> dict:
    crew_review = None
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        if os.getenv("ENABLE_CREWAI", "false").lower() == "true":
            progress.add_task("CrewAI coordinating agents...", total=None)
            try:
                crew_review = run_discovery_crew(transcript)
                console.print(Panel(crew_review, title="CrewAI Coordination Output"))
            except Exception as exc:
                console.print(f"[yellow]CrewAI coordination skipped/failed: {exc}[/yellow]")

        progress.add_task("IntakeParser working...", total=None)
        intake = IntakeParser().run(transcript)
        console.print(Panel(str(intake), title="IntakeParser Output"))

        progress.add_task("SolutionArchitect working...", total=None)
        architecture = SolutionArchitect().run(transcript, intake)
        console.print(Panel(architecture["architecture_summary"], title="SolutionArchitect Output"))

        progress.add_task("ScopeEstimator working...", total=None)
        scope = ScopeEstimator().run(intake, architecture)
        console.print(Panel(scope["timeline_summary"], title="ScopeEstimator Output"))

        progress.add_task("ProposalDrafter working...", total=None)
        payload = ProposalDrafter().run(intake, architecture, scope)
        if crew_review:
            payload["engineering_spec"]["crew_review"] = crew_review

    pdf_path = generate_client_proposal(payload)
    md_path = generate_engineering_spec(payload)
    repo_url = None
    if push_to_github and os.getenv("ENABLE_GITHUB_UPLOAD", "true").lower() == "true":
        try:
            repo_url = upload_to_github(intake.get("client_name", "TBD"), os.getenv("GITHUB_REPO_NAME", "discovery-agent"))
        except Exception as exc:
            console.print(f"[yellow]GitHub upload skipped/failed: {exc}[/yellow]")

    return {"pdf_path": pdf_path, "md_path": md_path, "repo_url": repo_url, "payload": payload}


def _read_transcript() -> str:
    console.print("[bold]Paste transcript text or enter a path to a .txt/.md file.[/bold]")
    value = console.input("> ").strip()
    candidate = Path(value).expanduser()
    if candidate.exists() and candidate.suffix.lower() in {".txt", ".md"}:
        return candidate.read_text(encoding="utf-8", errors="ignore")
    console.print("[dim]Paste remaining text. Press CTRL+D when finished, or Enter for single-line mode.[/dim]")
    lines = [value]
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line and len(lines) == 1:
            break
        lines.append(line)
    return "\n".join(lines)


def _print_result(result: dict) -> None:
    lines = [
        f"Client proposal: {result['pdf_path']}",
        f"Engineering spec: {result['md_path']}",
        f"GitHub URL: {result['repo_url'] or 'not available'}",
    ]
    console.print(Panel("\n".join(lines), title="Done", border_style="green"))
