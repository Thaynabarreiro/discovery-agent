from __future__ import annotations

from pathlib import Path


def generate_pm_call_review(payload: dict, output_dir: str = "output") -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata = payload["metadata"]
    prefix = metadata["artifact_prefix"]
    path = out_dir / f"{prefix}_pm_call_review.md"

    spec = payload["engineering_spec"]
    intake = spec["intake"]
    architecture = spec["architecture"]
    scope = spec["scope"]
    decisions = {item["layer"]: item["chosen"] for item in architecture["decisions"]}

    paragraph = (
        f"On this discovery call with {intake.get('client_name', 'the client')}, the PM should be able to sketch a working solution in real time: "
        f"this is primarily a {decisions.get('Orchestration', 'agentic workflow')} problem with structured transcript intake, RAG over prior reference cases, "
        f"and a document-generation layer that produces both an executive proposal and an engineering spec. The likely system shape is an agentic pipeline with "
        f"specialized agents for intake parsing, solution architecture, scope estimation, and proposal drafting, supported by deterministic tools for transcription, "
        f"retrieval, PDF rendering, Markdown generation, and repository upload. The relevant vector database is {decisions.get('Vector DB', 'a local vector store')}, "
        f"used to retrieve similar delivery cases before architecture and scope decisions are finalized. The hard parts are reliable live audio capture, clean source-system "
        f"access, messy lead or operational data, human approval rules, and integration limits; the easier parts are transcript ingestion, structured extraction, draft generation, "
        f"and packaging the outputs into reusable templates. Based on the detected {intake.get('complexity', 'medium')} complexity, the current scope should be treated as "
        f"{scope.get('timeline_summary', 'a phased pilot')}, with a first phase focused on proving the workflow on representative examples before expanding integrations."
    )

    path.write_text(f"# PM Call Review - {intake.get('client_name', 'Client')}\n\n{paragraph}\n", encoding="utf-8")
    return path
