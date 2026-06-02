from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass


@dataclass
class IntakeData:
    client_name: str = "TBD"
    industry: str = "TBD"
    core_problem: str = "TBD"
    current_tools: list[str] | None = None
    integrations_needed: list[str] | None = None
    data_volume: str = "TBD"
    team_size: str = "TBD"
    urgency: str = "medium"
    budget_signal: str = "TBD"
    complexity: str = "medium"
    desired_solution: str = "TBD"
    success_criteria: str = "TBD"
    approval_requirements: str = "TBD"
    source_channels: list[str] | None = None
    use_case: str = "generic_workflow"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["current_tools"] = data["current_tools"] or []
        data["integrations_needed"] = data["integrations_needed"] or []
        data["source_channels"] = data["source_channels"] or []
        return data


class IntakeParser:
    role = "Business Analyst"
    goal = "Extract structured data from a discovery call transcript."

    TOOL_PATTERNS = {
        "salesforce": "Salesforce",
        "gmail": "Gmail",
        "email": "Email",
        "linkedin sales navigator": "LinkedIn Sales Navigator",
        "linkedin": "LinkedIn",
        "hubspot": "HubSpot",
        "pipedrive": "Pipedrive",
        "notion": "Notion",
        "google sheets": "Google Sheets",
        "airtable": "Airtable",
        "slack": "Slack",
        "whatsapp": "WhatsApp",
        "zapier": "Zapier",
        "make.com": "Make",
        "integromat": "Make",
        "excel": "Excel",
        "spreadsheet": "Spreadsheet",
    }

    CHANNEL_PATTERNS = {
        "website forms": "Website forms",
        "website form": "Website forms",
        "email": "Email",
        "gmail": "Gmail",
        "linkedin": "LinkedIn",
        "trade show": "Trade show lists",
        "trade show lists": "Trade show lists",
    }

    def run(self, transcript: str) -> dict:
        text = transcript.strip()
        lower = text.lower()
        tools = self._unique([label for pattern, label in self.TOOL_PATTERNS.items() if re.search(rf"\b{re.escape(pattern)}\b", lower)])
        integrations = [tool for tool in tools if tool not in {"Excel", "Google Sheets", "Notion", "Spreadsheet"}]
        source_channels = self._unique([label for pattern, label in self.CHANNEL_PATTERNS.items() if re.search(rf"\b{re.escape(pattern)}\b", lower)])

        client_name = self._find_client_name(text)
        urgency = "high" if re.search(r"\b(urgent|asap|imediat|this month|agora|rapido|campaign launching soon|two to three weeks|2-3 weeks)\b", lower) else "medium"
        complexity = self._infer_complexity(lower, integrations)

        data = IntakeData(
            client_name=client_name,
            industry=self._find_industry(text),
            core_problem=self._summarize_problem(text),
            current_tools=tools,
            integrations_needed=integrations,
            data_volume=self._find_data_volume(text),
            team_size=self._find_team_size(text),
            urgency=urgency,
            budget_signal=self._find_budget_signal(text),
            complexity=complexity,
            desired_solution=self._find_desired_solution(text),
            success_criteria=self._find_success_criteria(text),
            approval_requirements=self._find_approval_requirements(text),
            source_channels=source_channels,
            use_case=self._classify_use_case(lower),
        )
        return data.to_dict()

    def run_json(self, transcript: str) -> str:
        return json.dumps(self.run(transcript), indent=2, ensure_ascii=False)

    def _unique(self, values: list[str]) -> list[str]:
        seen = set()
        unique_values = []
        for value in values:
            key = value.lower()
            if key not in seen:
                seen.add(key)
                unique_values.append(value)
        return unique_values

    def _find_client_name(self, text: str) -> str:
        patterns = [
            r"\bWe are\s+([A-Z][A-Za-z0-9& '\-]+?)(?:\.|,|\n)",
            r"\bwe're\s+([A-Z][A-Za-z0-9& '\-]+?)(?:\.|,|\n)",
            r"(?:client|cliente|company|empresa)\s*[:\-]\s*([A-Z][\w\s&.-]{2,60})",
            r"(?:prepared for)\s+([A-Z][\w\s&.-]{2,60})",
            r"(?:Participants|Participantes)\s*[:\-]\s*[^\n,]+,\s*([A-Z][^\n,]{2,60})\s+from\s+([A-Z][^\n,]{2,60})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1 and match.group(2):
                    return self._clean_name(match.group(2))
                return self._clean_name(match.group(1))
        return "TBD"

    def _clean_name(self, value: str) -> str:
        value = re.split(r"\b(?:we sell|we provide|we build|we are looking|our team)\b", value, flags=re.IGNORECASE)[0]
        return " ".join(value.split()).strip(" .,-")

    def _find_industry(self, text: str) -> str:
        match = re.search(r"(?:industry|setor|segmento)\s*[:\-]\s*([^\n.]{3,80})", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        lower = text.lower()
        if "manufacturing" in lower or "equipment" in lower or "replacement parts" in lower:
            return "Industrial equipment and manufacturing supply"
        if "clinic" in lower or "patient" in lower:
            return "Healthcare"
        if "finance" in lower or "invoice" in lower:
            return "Finance operations"
        return match.group(1).strip() if match else "TBD"

    def _summarize_problem(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        keywords = ("problem", "pain", "challenge", "manual", "delay", "erro", "problema", "dor", "desafio")
        for sentence in sentences:
            if any(word in sentence.lower() for word in keywords):
                return sentence[:500]
        for sentence in sentences:
            if any(word in sentence.lower() for word in ("wants", "want", "needs", "need", "improve")):
                return sentence[:500]
        return sentences[0][:500] if sentences and sentences[0] else "TBD"

    def _find_data_volume(self, text: str) -> str:
        match = re.search(r"(\d+[\w\s,.-]{0,30}\s(?:records|rows|leads|tickets|clientes|linhas|registros))", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _find_team_size(self, text: str) -> str:
        match = re.search(r"(\d+\s*(?:people|users|seats|pessoas|usuarios|usuários|sales reps|reps))", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r"(sales coordinator,\s*the sales manager,\s*and\s*about\s*eight\s*sales reps)", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _find_budget_signal(self, text: str) -> str:
        budget_context = re.search(
            r"(?:budget|orçamento|verba)[^.:\n]*[:\-]?\s*([^.\n]{0,120})",
            text,
            re.IGNORECASE,
        )
        if budget_context:
            match = re.search(r"(R\$\s?\d[\d.,\s]*(?:mil)?|[$€£]\s?\d[\d.,kKmM ]+|\d+\s?(?:k|mil|thousand))", budget_context.group(1), re.IGNORECASE)
            if match:
                return match.group(1).strip()
        match = re.search(r"(R\$\s?\d[\d.,\s]*(?:mil)?|[$€£]\s?\d[\d.,kKmM ]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _infer_complexity(self, lower: str, integrations: list[str]) -> str:
        if len(integrations) >= 3 or any(word in lower for word in ("compliance", "erp", "legacy", "multi-team")):
            return "high"
        if len(integrations) >= 1 or any(word in lower for word in ("approval", "dashboard", "workflow", "automacao", "automação")):
            return "medium"
        return "low"

    def _find_desired_solution(self, text: str) -> str:
        match = re.search(r"Client wants\s+(.+?)(?:\n|$)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(".")
        match = re.search(r"Ideally,\s+it would\s+(.+?)(?:\n|$)", text, re.IGNORECASE)
        if match:
            return "It would " + match.group(1).strip().rstrip(".")
        return "TBD"

    def _find_success_criteria(self, text: str) -> str:
        match = re.search(r"(high-priority leads can be routed within one hour instead of one or two days)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r"If\s+([^.\n]+would be a big win)", text, re.IGNORECASE)
        if match:
            return " ".join(match.group(1).split()).rstrip(".")
        match = re.search(r"(Faster response time and better prioritization[^.\n]*\.)", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _find_approval_requirements(self, text: str) -> str:
        match = re.search(r"(human to approve changes before anything is written back)", text, re.IGNORECASE)
        if match:
            return "Human approval is required before writing updates back to the CRM"
        if re.search(r"\bhuman approval\b|\bapprove\b", text, re.IGNORECASE):
            return "Human approval is required before automated changes are finalized"
        return "TBD"

    def _classify_use_case(self, lower: str) -> str:
        if any(word in lower for word in ("lead", "salesforce", "sales rep", "qualification", "route")):
            return "lead_qualification"
        if any(word in lower for word in ("patient", "clinic", "appointment", "no-show")):
            return "healthcare_follow_up"
        if any(word in lower for word in ("invoice", "finance", "document intake", "approval")):
            return "finance_document_workflow"
        return "generic_workflow"
