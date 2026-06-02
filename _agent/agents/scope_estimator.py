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
        if intake.get("use_case") == "lead_qualification":
            return self._lead_qualification_scope(intake)

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
                {"variable": "ANTHROPIC_API_KEY", "purpose": "LLM access", "who_provides": "Delivery Team"},
                {"variable": "OPENAI_API_KEY", "purpose": "Whisper transcription", "who_provides": "Delivery Team"},
                {"variable": "CHROMA_PERSIST_DIR", "purpose": "Local vector database path", "who_provides": "Delivery Team"},
                {"variable": "[CLIENT_SYSTEM]_KEY", "purpose": "Client system access", "who_provides": "Client IT"},
            ],
        }

    def _lead_qualification_scope(self, intake: dict) -> dict:
        return {
            "timeline_summary": "2-3 weeks",
            "phases": [
                {
                    "phase": "01",
                    "deliverable": "Lead intake and Salesforce data readiness",
                    "acceptance_criteria": "Sample inbound leads from website, Gmail, LinkedIn, and trade show lists are normalized; Salesforce closed-won/closed-lost data is mapped with source references.",
                    "timeline": "Wk 1",
                },
                {
                    "phase": "02",
                    "deliverable": "Explainable lead scoring and similar-account retrieval",
                    "acceptance_criteria": "At least 20 representative leads receive a score, priority level, explanation, and cited similar Salesforce accounts without unsupported claims.",
                    "timeline": "Wk 2",
                },
                {
                    "phase": "03",
                    "deliverable": "Routing recommendation and human-approved CRM draft",
                    "acceptance_criteria": "High-priority leads can be routed to a recommended sales rep within one hour, and Salesforce updates remain draft-only until approved by the coordinator or manager.",
                    "timeline": "Wk 3",
                },
            ],
            "known_limitations": [
                "Salesforce history is not perfectly clean, so phase one must validate field quality, duplicate accounts, and missing sales notes before scoring is trusted.",
                "LinkedIn Sales Navigator access may be limited by export/API permissions and should not be treated as guaranteed enrichment in the pilot.",
                "The pilot should not automatically write back to Salesforce until Atlas approves the scoring explanation and routing logic.",
            ],
            "watch_points": [
                "Confirm the exact scoring rubric for company size, industry, location, urgency, equipment specificity, and similarity to past wins.",
                "Define sales rep assignment rules for territory, product category, existing account ownership, and overflow cases.",
                "Agree how source citations are displayed so the team can audit why a lead received its priority level.",
            ],
            "infra_cost": "Estimated low to moderate monthly cost for LLM calls, embeddings, and lightweight hosting during the pilot; Salesforce, Slack, and Gmail costs depend on Atlas's existing plans and API limits.",
            "environment_variables": [
                {"variable": "ANTHROPIC_API_KEY", "purpose": "LLM reasoning for scoring explanations and routing recommendations", "who_provides": "Delivery Team"},
                {"variable": "CHROMA_PERSIST_DIR", "purpose": "Local vector database path for similar-account retrieval", "who_provides": "Delivery Team"},
                {"variable": "SALESFORCE_CLIENT_ID", "purpose": "Salesforce OAuth app access", "who_provides": "Client IT"},
                {"variable": "SALESFORCE_CLIENT_SECRET", "purpose": "Salesforce OAuth secret", "who_provides": "Client IT"},
                {"variable": "SALESFORCE_INSTANCE_URL", "purpose": "Atlas Salesforce tenant URL", "who_provides": "Client IT"},
                {"variable": "GMAIL_CLIENT_ID", "purpose": "Gmail lead source access if email ingestion is in pilot scope", "who_provides": "Client IT"},
                {"variable": "GMAIL_CLIENT_SECRET", "purpose": "Gmail OAuth secret", "who_provides": "Client IT"},
                {"variable": "SLACK_BOT_TOKEN", "purpose": "Slack summary and manager visibility notifications", "who_provides": "Client IT"},
            ],
        }
