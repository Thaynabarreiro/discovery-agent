from __future__ import annotations


class ProposalDrafter:
    role = "Client Communications Lead"
    goal = "Generate final content for the client proposal and engineering spec."

    def run(self, intake: dict, architecture: dict, scope: dict) -> dict:
        client_name = intake.get("client_name") or "TBD"
        profile = self._solution_profile(intake, architecture, scope)

        return {
            "client_proposal": {
                "client_name": client_name,
                "what_discussed": profile["what_discussed"],
                "what_building": profile["what_building"],
                "highlight": profile["highlight"],
                "deliverables": profile["deliverables"],
                "timeline": [f"{phase['timeline']} - {phase['deliverable']}" for phase in scope["phases"]],
                "next_steps": profile["next_steps"],
            },
            "engineering_spec": {
                "project_name": architecture.get("project_name", "Discovery Automation"),
                "problem_statement": profile["problem_statement"],
                "intake": intake,
                "architecture": architecture,
                "scope": scope,
                "open_questions": profile["open_questions"],
            },
        }

    def _solution_profile(self, intake: dict, architecture: dict, scope: dict) -> dict:
        if intake.get("use_case") == "lead_qualification":
            return self._lead_qualification_profile(intake, architecture, scope)
        client_name = intake.get("client_name") or "the client"
        problem = intake.get("core_problem") or "the current manual workflow"
        desired = intake.get("desired_solution")
        if not desired or desired == "TBD":
            desired = "reduce manual work, improve consistency, and give the team a clearer operating workflow"
        return {
            "what_discussed": [
                f"We discussed how {client_name} is currently handling {problem.lower()} and where the process creates delays or inconsistent decisions.",
                "The main opportunity is to turn the existing operating knowledge into a repeatable workflow with clear inputs, review points, and measurable outcomes.",
            ],
            "what_building": f"We will build a focused AI-assisted workflow that helps {client_name} {desired}.",
            "highlight": "Manual review -> consistent, reviewable workflow",
            "deliverables": [
                "Structured intake for the source data and business context",
                "Automated analysis with clear reasoning for each recommendation",
                "Human review step before any sensitive or external action",
                "Operational handoff documentation for the team",
            ],
            "next_steps": [
                "Confirm the source systems and sample data for the pilot.",
                "Agree the decision rules and human approval points.",
                "Run the first pilot examples and review the outputs together.",
            ],
            "problem_statement": f"Build an AI-assisted workflow for {client_name} that addresses {problem.lower()} by extracting structured inputs, retrieving relevant context, applying business rules, and preparing reviewable recommendations for the team.",
            "open_questions": [
                "Which source system is the system of record for the pilot?",
                "Which recommendations can be automated and which require human approval?",
                "What data can be stored locally during the pilot?",
            ],
        }

    def _lead_qualification_profile(self, intake: dict, architecture: dict, scope: dict) -> dict:
        client_name = intake.get("client_name") or "Atlas Industrial Supply"
        return {
            "what_discussed": [
                f"{client_name} receives inbound leads from website forms, email, LinkedIn, and trade show lists, but qualification is still handled manually by a sales coordinator. Today that person checks the company website, CRM history, the lead message, LinkedIn, and sometimes past invoices before deciding whether a lead should go to a sales rep.",
                "The main issue is speed and consistency. Strong leads can wait two or three days before follow-up, and priority decisions vary depending on who reviews the lead. The sales manager also wants better visibility into missed opportunities and why each lead was prioritized.",
            ],
            "what_building": (
                "We will build an AI-assisted inbound lead qualification workflow. It will read new leads, enrich company context, compare each lead against similar past accounts, assign a priority score, explain the reason for that score, and recommend the right sales rep while keeping human approval before any CRM update."
            ),
            "highlight": "High-priority lead routing: 2-3 days -> under 1 hour",
            "deliverables": [
                "Inbound lead intake from website forms, email, LinkedIn, and trade show lists",
                "Company context enrichment using CRM history and available public context",
                "Similar-account matching against past won and lost opportunities",
                "Explainable lead score with the evidence behind each priority decision",
                "Recommended sales rep based on assignment rules and lead context",
                "Draft CRM update and manager visibility summary for human approval",
            ],
            "next_steps": [
                "Confirm Salesforce access and provide representative won/lost opportunity data.",
                "Approve the lead scoring criteria for size, industry, location, urgency, equipment fit, and similarity to past wins.",
                "Define sales rep routing rules and who approves CRM draft updates during the pilot.",
                "Run a pilot on recent inbound leads before the upcoming campaign.",
            ],
            "problem_statement": (
                f"Build an AI-assisted lead qualification and routing workflow for {client_name}. The system must ingest inbound leads from multiple channels, enrich company context, retrieve similar Salesforce history, produce an explainable lead score, recommend the right sales rep, and keep CRM updates in draft form until a human approves them."
            ),
            "open_questions": [
                "Which Salesforce objects and fields contain the best closed-won, closed-lost, account, invoice, and sales note history?",
                "What exact score thresholds define high, medium, and low priority leads?",
                "Which routing rules determine the recommended sales rep when territory, product category, and existing ownership conflict?",
                "What public or third-party enrichment sources are approved for company context?",
                "Who approves draft Salesforce updates during the pilot: coordinator, sales manager, or both?",
            ],
        }
