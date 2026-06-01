from __future__ import annotations


class ProposalDrafter:
    role = "Client Communications Lead"
    goal = "Generate final content for the client proposal and engineering spec."

    def run(self, intake: dict, architecture: dict, scope: dict) -> dict:
        client_name = intake.get("client_name") or "TBD"
        core_problem = intake.get("core_problem") or "The team needs a more reliable way to turn discovery conversations into actionable project outputs."
        outcome = self._outcome_line(intake)

        return {
            "client_proposal": {
                "client_name": client_name,
                "what_discussed": [
                    f"We discussed the current challenge around {core_problem.lower()}",
                    "The opportunity is to reduce manual follow-up work, make decisions easier to review, and give both business and technical teams a clearer path after each call.",
                ],
                "what_building": "We will build a focused AI-assisted workflow that turns call notes into a client-ready proposal and an internal implementation brief.",
                "highlight": outcome,
                "deliverables": [
                    "A structured intake process for discovery calls",
                    "A polished client proposal generated from each call",
                    "An internal engineering spec with scope, risks, and open questions",
                    "A repeatable handoff flow for future calls",
                ],
                "timeline": [f"{phase['timeline']} - {phase['deliverable']}" for phase in scope["phases"]],
                "next_steps": [
                    "Confirm the sample call transcript and expected tone.",
                    "Review the first generated proposal together.",
                    "Approve the final delivery workflow before ongoing use.",
                ],
            },
            "engineering_spec": {
                "project_name": architecture.get("project_name", "Discovery Automation"),
                "problem_statement": (
                    f"Build a system that transforms discovery call transcripts for {client_name} into "
                    "separate executive and engineering artifacts while preserving decision rationale, scope, risks, and implementation questions."
                ),
                "intake": intake,
                "architecture": architecture,
                "scope": scope,
                "open_questions": [
                    "Which source systems must be integrated in the first production version?",
                    "Who approves generated client-facing proposals before they are sent?",
                    "What transcript retention policy should be used for client data?",
                ],
            },
        }

    def _outcome_line(self, intake: dict) -> str:
        if intake.get("urgency") == "high":
            return "Faster follow-up after urgent calls, with fewer manual handoff gaps."
        return "Discovery notes become shareable project documents in minutes instead of days."
