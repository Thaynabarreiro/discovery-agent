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

    def to_dict(self) -> dict:
        data = asdict(self)
        data["current_tools"] = data["current_tools"] or []
        data["integrations_needed"] = data["integrations_needed"] or []
        return data


class IntakeParser:
    role = "Business Analyst"
    goal = "Extract structured data from a discovery call transcript."

    TOOL_PATTERNS = [
        "salesforce",
        "hubspot",
        "pipedrive",
        "notion",
        "google sheets",
        "airtable",
        "slack",
        "whatsapp",
        "zapier",
        "make",
        "excel",
    ]

    def run(self, transcript: str) -> dict:
        text = transcript.strip()
        lower = text.lower()
        tools = [tool.title() for tool in self.TOOL_PATTERNS if tool in lower]
        integrations = [tool for tool in tools if tool not in {"Excel", "Google Sheets", "Notion"}]

        client_name = self._find_client_name(text)
        urgency = "high" if re.search(r"\b(urgent|asap|imediat|this month|agora|rapido)\b", lower) else "medium"
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
        )
        return data.to_dict()

    def run_json(self, transcript: str) -> str:
        return json.dumps(self.run(transcript), indent=2, ensure_ascii=False)

    def _find_client_name(self, text: str) -> str:
        patterns = [
            r"(?:client|cliente|company|empresa)\s*[:\-]\s*([A-Z][\w\s&.-]{2,60})",
            r"(?:prepared for|para)\s+([A-Z][\w\s&.-]{2,60})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().rstrip(".")
        return "TBD"

    def _find_industry(self, text: str) -> str:
        match = re.search(r"(?:industry|setor|segmento)\s*[:\-]\s*([^\n.]{3,80})", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _summarize_problem(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        keywords = ("problem", "pain", "challenge", "manual", "delay", "erro", "problema", "dor", "desafio")
        for sentence in sentences:
            if any(word in sentence.lower() for word in keywords):
                return sentence[:500]
        return sentences[0][:500] if sentences and sentences[0] else "TBD"

    def _find_data_volume(self, text: str) -> str:
        match = re.search(r"(\d+[\w\s,.-]{0,30}\s(?:records|rows|leads|tickets|clientes|linhas|registros))", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _find_team_size(self, text: str) -> str:
        match = re.search(r"(\d+\s*(?:people|users|seats|pessoas|usuarios|usuários))", text, re.IGNORECASE)
        return match.group(1).strip() if match else "TBD"

    def _find_budget_signal(self, text: str) -> str:
        match = re.search(r"([$€£R]\$?\s?\d[\d.,kKmM ]+|\d+\s?(?:k|mil|thousand))", text)
        return match.group(1).strip() if match else "TBD"

    def _infer_complexity(self, lower: str, integrations: list[str]) -> str:
        if len(integrations) >= 3 or any(word in lower for word in ("compliance", "erp", "legacy", "multi-team")):
            return "high"
        if len(integrations) >= 1 or any(word in lower for word in ("approval", "dashboard", "workflow", "automacao", "automação")):
            return "medium"
        return "low"
