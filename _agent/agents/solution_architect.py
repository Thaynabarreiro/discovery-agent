from __future__ import annotations

from _agent.tools.rag_search import RagSearch


class SolutionArchitect:
    role = "AI Solutions Architect"
    goal = "Define architecture and justify technical decisions for the client case."

    def __init__(self, rag: RagSearch | None = None) -> None:
        self.rag = rag or RagSearch()

    def run(self, transcript: str, intake: dict) -> dict:
        cases = self.rag.search(intake.get("core_problem", transcript), n_results=3)
        complexity = intake.get("complexity", "medium")

        if complexity == "high":
            orchestration = "LangGraph"
            llm = "Claude Sonnet 4.6"
            rationale = "The workflow likely needs state, branching, and explicit review loops."
        elif complexity == "low":
            orchestration = "Claude SDK"
            llm = "Claude Haiku"
            rationale = "The use case appears linear enough to avoid orchestration overhead."
        else:
            orchestration = "CrewAI"
            llm = "Claude Sonnet 4.6"
            rationale = "The project benefits from clear specialist roles without complex graph state."

        return {
            "project_name": self._project_name(intake),
            "architecture_summary": self._architecture_summary(intake, orchestration, llm),
            "similar_cases": cases,
            "decisions": [
                {
                    "layer": "Orchestration",
                    "chosen": orchestration,
                    "alternatives": "CrewAI, LangGraph, Claude SDK, Gemini SDK",
                    "rationale": rationale,
                },
                {
                    "layer": "LLM",
                    "chosen": llm,
                    "alternatives": "Claude Haiku, Gemini Flash",
                    "rationale": "Chosen based on the balance of reasoning quality, reliability, cost, and the detected implementation complexity.",
                },
                {
                    "layer": "Vector DB",
                    "chosen": "ChromaDB",
                    "alternatives": "Pinecone, Weaviate, Postgres pgvector",
                    "rationale": "Local persistence is enough for discovery-stage case retrieval and avoids managed database cost.",
                },
                {
                    "layer": "Infra",
                    "chosen": "Client-approved Python service with GitHub-based delivery",
                    "alternatives": "Serverless functions, managed workflow platform, manual scripts",
                    "rationale": "A Python service keeps the agent pipeline transparent, testable, and easy to hand over.",
                },
            ],
        }

    def _project_name(self, intake: dict) -> str:
        client = intake.get("client_name") or "Client"
        problem = intake.get("core_problem") or "AI Workflow"
        keyword = "Automation" if "manual" in problem.lower() else "AI Solution"
        return f"{client} {keyword}".replace("TBD ", "").strip()

    def _architecture_summary(self, intake: dict, orchestration: str, llm: str) -> str:
        return (
            f"Build a {orchestration}-coordinated AI workflow using {llm} for structured reasoning, "
            "local ChromaDB retrieval for similar cases, and deterministic tools for document generation."
        )
