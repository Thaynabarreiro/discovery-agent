from __future__ import annotations


class ScopeEstimator:
    role = "Technical Project Manager"
    goal = "Estimate implementation phases, acceptance criteria, limitations, and environment needs."

    TIMELINES = {
        "low": ("1-2 weeks", [("01", "Setup and calibration", "Core workflow runs on sample data with documented inputs.", "Wk 1"),
                              ("02", "Client-ready handoff", "Proposal/spec outputs match agreed templates.", "Wk 2")]),
        "medium": ("2-4 weeks", [("01", "Discovery and setup", "Credentials, sample data, and integration access are confirmed.", "Wk 1"),
                                  ("02", "Workflow build", "Agents complete the target workflow on at least 5 representative examples.", "Wk 2-3"),
                                  ("03", "QA and handoff", "Acceptance tests pass and operational notes are delivered.", "Wk 4")]),
        "high": ("4-6 weeks", [("01", "Architecture and data readiness", "All systems, data contracts, and edge cases are documented.", "Wk 1-2"),
                                ("02", "Phased implementation", "Critical path workflow runs with monitored fallbacks.", "Wk 3-4"),
                                ("03", "Pilot and stabilization", "Pilot users validate outputs and support runbooks are complete.", "Wk 5-6")]),
    }

    def run(self, intake: dict, architecture: dict) -> dict:
        complexity = intake.get("complexity", "medium")
        timeline, phase_rows = self.TIMELINES.get(complexity, self.TIMELINES["medium"])
        return {
            "timeline_summary": timeline,
            "phases": [
                {
                    "phase": phase,
                    "deliverable": deliverable,
                    "acceptance_criteria": criteria,
                    "timeline": timeline_label,
                }
                for phase, deliverable, criteria, timeline_label in phase_rows
            ],
            "known_limitations": [
                "Final accuracy depends on representative transcript samples and client feedback during calibration.",
                "Third-party system rate limits or missing API access may delay integration testing.",
                "Ambiguous call language may require human review before sharing client-facing outputs.",
            ],
            "watch_points": [
                "Confirm source systems and owners before implementation starts.",
                "Validate whether production data contains sensitive personal information.",
            ],
            "infra_cost": "Estimated low to moderate monthly API and hosting cost; final number depends on call volume, transcript length, and model choice.",
            "environment_variables": [
                {"variable": "ANTHROPIC_API_KEY", "purpose": "LLM access", "who_provides": "Zaigo"},
                {"variable": "OPENAI_API_KEY", "purpose": "Whisper transcription", "who_provides": "Zaigo"},
                {"variable": "CHROMA_PERSIST_DIR", "purpose": "Local vector database path", "who_provides": "Zaigo"},
                {"variable": "[CLIENT_SYSTEM]_KEY", "purpose": "Client system access", "who_provides": "Client IT"},
            ],
        }
