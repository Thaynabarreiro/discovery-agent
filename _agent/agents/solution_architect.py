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

        if intake.get("use_case") == "lead_qualification":
            orchestration = "CrewAI"
            llm = "Claude Sonnet 4.6"
            rationale = "The workflow benefits from clear specialist roles without requiring complex graph state for the pilot."
        elif complexity == "high":
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
            "agent_architecture": self._agent_architecture(intake),
            "data_flow": self._data_flow(intake),
            "similar_cases": cases,
            "decisions": [
                {
                    "layer": "Orchestration",
                    "chosen": orchestration,
                    "alternatives": "CrewAI, LangGraph, Claude SDK, Gemini SDK",
                    "rationale": self._orchestration_rationale(intake, rationale),
                },
                {
                    "layer": "LLM",
                    "chosen": llm,
                    "alternatives": "Claude Haiku, Gemini Flash",
                    "rationale": self._llm_rationale(intake),
                },
                {
                    "layer": "Vector DB",
                    "chosen": "ChromaDB",
                    "alternatives": "Pinecone, Weaviate, Postgres pgvector",
                    "rationale": self._vector_rationale(intake),
                },
                {
                    "layer": "Infra",
                    "chosen": "Client-approved Python service with GitHub-based delivery",
                    "alternatives": "Serverless functions, managed workflow platform, manual scripts",
                    "rationale": self._infra_rationale(intake),
                },
            ],
        }

    def _project_name(self, intake: dict) -> str:
        client = intake.get("client_name") or "Client"
        if intake.get("use_case") == "lead_qualification":
            return f"{client} Lead Qualification Workflow".replace("TBD ", "").strip()
        problem = intake.get("core_problem") or "AI Workflow"
        keyword = "Automation" if "manual" in problem.lower() else "AI Solution"
        return f"{client} {keyword}".replace("TBD ", "").strip()

    def _architecture_summary(self, intake: dict, orchestration: str, llm: str) -> str:
        if intake.get("use_case") == "lead_qualification":
            return (
                "Build an AI-assisted lead qualification workflow that ingests inbound leads, enriches company context, "
                "retrieves similar Salesforce history, produces an explainable priority score, recommends the right sales rep, "
                "and keeps a human approval step before CRM updates are written."
            )
        return (
            f"Build a {orchestration}-coordinated AI workflow using {llm} for structured reasoning, "
            "local ChromaDB retrieval for relevant records, and deterministic tools for the final workflow actions."
        )

    def _agent_architecture(self, intake: dict) -> list[dict]:
        if intake.get("use_case") == "lead_qualification":
            return [
                {
                    "name": "LeadIntakeAgent",
                    "input": "New inbound lead from website forms, Gmail, LinkedIn, or trade show lists",
                    "output": "Normalized lead profile with source, message, company, contact, and urgency signals",
                    "tools": "Salesforce API, Gmail API, LinkedIn Sales Navigator export/API where available",
                    "notes": "Keeps source metadata so every score can be traced back to observed evidence",
                },
                {
                    "name": "CompanyContextAgent",
                    "input": "Normalized lead profile",
                    "output": "Enriched company context including industry, location, size, and equipment mentions",
                    "tools": "Company website lookup, CRM account history, optional enrichment provider",
                    "notes": "Does not invent company facts; unknown fields stay blank or require review",
                },
                {
                    "name": "SimilarAccountRetriever",
                    "input": "Company profile, industry, equipment keywords, and CRM account context",
                    "output": "Top similar closed-won/closed-lost Salesforce accounts with source references",
                    "tools": "ChromaDB vector search over Salesforce history and sales notes",
                    "notes": "Uses Chroma as the vector database for retrieval and evidence grounding",
                },
                {
                    "name": "LeadScoringAgent",
                    "input": "Lead profile, enriched context, similar accounts, and scoring criteria",
                    "output": "Lead score, priority level, and explanation for each scoring factor",
                    "tools": "LLM reasoning with deterministic scoring rubric",
                    "notes": "Scores company size, industry fit, location, urgency, equipment specificity, and similarity to prior wins",
                },
                {
                    "name": "RoutingRecommendationAgent",
                    "input": "Lead score, territory/product signals, and sales rep assignment rules",
                    "output": "Recommended sales rep and routing reason",
                    "tools": "Salesforce owner data, routing rules table",
                    "notes": "Flags conflicts or missing ownership rules instead of guessing",
                },
                {
                    "name": "ApprovalDraftAgent",
                    "input": "Score, explanation, routing recommendation, and source references",
                    "output": "Draft Salesforce update and Slack summary awaiting human approval",
                    "tools": "Salesforce draft/update endpoint, Slack",
                    "notes": "Pilot mode requires human approval before writing back to Salesforce",
                },
            ]
        return [
            {
                "name": "IntakeAgent",
                "input": "Client request, transcript, and available source data",
                "output": "Structured case profile with problem, tools, data, users, urgency, and constraints",
                "tools": "Source-system connectors as approved",
                "notes": "Preserves missing fields as open questions",
            },
            {
                "name": "RetrievalAgent",
                "input": "Case profile and searchable business context",
                "output": "Relevant historical records or reference cases with citations",
                "tools": "ChromaDB",
                "notes": "Grounds recommendations in retrieved evidence when data is available",
            },
            {
                "name": "DecisionAgent",
                "input": "Case profile, retrieved context, and business rules",
                "output": "Recommended action, explanation, and confidence/risk flags",
                "tools": "LLM plus deterministic validators",
                "notes": "Separates reasoning from final automated actions",
            },
            {
                "name": "ApprovalAgent",
                "input": "Recommended action and evidence",
                "output": "Human-approved final action or rejected draft",
                "tools": "Client workflow tools",
                "notes": "Keeps humans in the loop for first pilot decisions",
            },
        ]

    def _data_flow(self, intake: dict) -> list[dict]:
        if intake.get("use_case") == "lead_qualification":
            return [
                {"step": "Trigger", "description": "A new inbound lead arrives from website forms, Gmail, LinkedIn, or a trade show list."},
                {"step": "Extraction", "description": "LeadIntakeAgent normalizes the message, company, contact, source, and urgency signals."},
                {"step": "Retrieval", "description": "SimilarAccountRetriever searches ChromaDB for comparable Salesforce accounts, closed-won/closed-lost opportunities, and sales notes."},
                {"step": "Processing", "description": "LeadScoringAgent applies Atlas's scoring rubric and RoutingRecommendationAgent maps the lead to the best sales rep."},
                {"step": "Output", "description": "ApprovalDraftAgent creates a draft Salesforce update and Slack summary for human review before any CRM write-back."},
            ]
        return [
            {"step": "Trigger", "description": "The workflow starts from a manual run, webhook, or approved source-system event."},
            {"step": "Extraction", "description": "The intake agent converts raw inputs into structured data and open questions."},
            {"step": "Retrieval", "description": "ChromaDB retrieves relevant records or reference cases using local embeddings."},
            {"step": "Processing", "description": "Specialized agents reason over the case, apply business rules, and prepare recommendations."},
            {"step": "Output", "description": "The workflow writes approved outputs back to the selected client systems."},
        ]

    def _orchestration_rationale(self, intake: dict, fallback: str) -> str:
        if intake.get("use_case") == "lead_qualification":
            return (
                "CrewAI fits the Atlas pilot because the work can be split into clear specialist roles: intake, enrichment, retrieval, scoring, routing, and approval drafting."
            )
        return fallback

    def _llm_rationale(self, intake: dict) -> str:
        if intake.get("use_case") == "lead_qualification":
            return (
                "Claude Sonnet 4.6 is preferred for explainable scoring and source-grounded recommendations where the sales team must trust why a lead was prioritized."
            )
        return "Chosen based on the balance of reasoning quality, reliability, cost, and the detected implementation complexity."

    def _vector_rationale(self, intake: dict) -> str:
        if intake.get("use_case") == "lead_qualification":
            return (
                "ChromaDB is used as the local vector database for the pilot so Atlas can compare new leads against historical Salesforce opportunities and sales notes before investing in managed vector infrastructure."
            )
        return "Local persistence is enough for pilot-stage retrieval and avoids managed database cost."

    def _infra_rationale(self, intake: dict) -> str:
        if intake.get("use_case") == "lead_qualification":
            return (
                "A Python service keeps Salesforce, Gmail, Slack, retrieval, scoring, and approval logic transparent during the pilot while remaining easy to deploy behind n8n or a scheduled worker."
            )
        return "A Python service keeps the agent pipeline transparent, testable, and easy to hand over."
