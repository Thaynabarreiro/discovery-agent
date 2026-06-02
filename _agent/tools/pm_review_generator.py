from __future__ import annotations

from pathlib import Path


def generate_pm_call_review(payload: dict, output_dir: str = "output") -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / "pm_call_review.md"

    spec = payload["engineering_spec"]
    intake = spec["intake"]
    architecture = spec["architecture"]
    scope = spec["scope"]
    decisions = {item["layer"]: item["chosen"] for item in architecture["decisions"]}
    if intake.get("use_case") == "lead_qualification":
        content = _lead_qualification_review(intake, architecture, scope, decisions)
        path.write_text(content, encoding="utf-8")
        return path

    content = f"""# PM Call Review - {intake.get('client_name', 'Client')}

## One-Paragraph PM Read

On this discovery call with {intake.get('client_name', 'the client')}, the PM should be able to sketch a working solution in real time: this is primarily a {decisions.get('Orchestration', 'agentic workflow')} problem with structured transcript intake, RAG over prior reference cases, and a document-generation layer that produces both an executive proposal and an engineering spec. The likely system shape is an agentic pipeline with specialized agents for intake parsing, solution architecture, scope estimation, and proposal drafting, supported by deterministic tools for transcription, retrieval, PDF rendering, Markdown generation, and repository upload. The relevant vector database is {decisions.get('Vector DB', 'a local vector store')}, used to retrieve similar delivery cases before architecture and scope decisions are finalized. The hard parts are reliable live audio capture, clean source-system access, messy lead or operational data, human approval rules, and integration limits; the easier parts are transcript ingestion, structured extraction, draft generation, and packaging the outputs into reusable templates. Based on the detected {intake.get('complexity', 'medium')} complexity, the current scope should be treated as {scope.get('timeline_summary', 'a phased pilot')}, with a first phase focused on proving the workflow on representative examples before expanding integrations.

## What The PM Should Be Able To Say Live

> This looks like a workflow automation and agentic document-generation problem. We can capture or receive the call transcript, extract structured business requirements, retrieve similar prior cases through RAG, and then coordinate specialist agents to produce the client proposal, engineering spec, and PM review. The first version should keep human approval around outbound messages and integrations, while proving that the handoff from discovery to delivery is reliable.

## Working Solution Sketch

| Layer | PM-Level Explanation | Proposed Choice |
|---|---|---|
| Trigger | How the process starts | Dock app or n8n webhook |
| Local worker | What runs on the Mac | Audio capture, Whisper transcription, PDF/Markdown generation |
| Agentic framework | How reasoning is organized | {decisions.get('Orchestration', 'CrewAI')} |
| Retrieval | How prior cases are referenced | RAG over reference cases |
| Vector database | Where embeddings are searched | {decisions.get('Vector DB', 'ChromaDB')} |
| LLM | What performs reasoning/drafting | {decisions.get('LLM', 'Claude Sonnet')} |
| Outputs | What the PM/client/team receives | Client PDF, engineering spec, PM review |

## Hard vs Easy

**Hard**
- Capturing live call audio reliably on the Mac.
- Confirming source-system API access and permissions.
- Handling messy spreadsheets, duplicate records, and unclear ownership.
- Defining human approval rules before any automated outbound action.
- Keeping client-facing documents free of technical jargon.

**Easier**
- Processing a pasted transcript or saved transcript file.
- Extracting structured requirements from the call.
- Retrieving similar cases from a small local knowledge base.
- Drafting repeatable proposal/spec outputs from templates.
- Saving artifacts with consistent naming.

## PM Follow-Up Questions

- [ ] Which system is the source of truth for leads, customers, or tickets?
- [ ] Which actions require human approval before automation?
- [ ] What data can be stored locally, and what must stay in client systems?
- [ ] Which integration must be in phase one, and which can wait?
- [ ] Who signs off on the generated client-facing proposal?
"""

    path.write_text(content, encoding="utf-8")
    return path


def _lead_qualification_review(intake: dict, architecture: dict, scope: dict, decisions: dict) -> str:
    client = intake.get("client_name", "Client")
    return f"""# PM Call Review - {client}

## One-Paragraph PM Read

On this discovery call, {client} is asking for an explainable inbound lead qualification system: new leads arrive from website forms, Gmail, LinkedIn, and trade show lists; the workflow enriches the company context, checks Salesforce history for similar won/lost accounts, scores the lead, explains why it received that priority, and recommends the right sales rep. This is a RAG plus agentic workflow problem: RAG retrieves comparable Salesforce opportunities and sales notes, ChromaDB is the pilot vector database, and {decisions.get('Orchestration', 'CrewAI')} coordinates specialized agents for intake, enrichment, retrieval, scoring, routing, and approval drafting. The PM should position the pilot around one measurable business outcome: high-priority leads move from two or three days of delay to routing within one hour, while Salesforce updates remain draft-only until a human approves them. The hard parts are Salesforce data quality, scoring calibration, source citations, rep routing rules, and LinkedIn/Gmail permissions; the easier parts are normalizing lead inputs, producing the first score explanation, creating Slack visibility, and generating draft CRM updates. Scope should stay at {scope.get('timeline_summary', '2-3 weeks')} for the pilot because Atlas has an upcoming campaign and needs trust before automation.

## What The PM Should Be Able To Say Live

> This is a lead qualification and routing workflow with retrieval over CRM history. We would use agents to separate the jobs: one agent normalizes the incoming lead, another enriches the company context, another retrieves similar Salesforce accounts, another scores the lead with an explanation, and another recommends the sales rep and prepares a draft CRM update. The first version should keep a human approval step so the team trusts the recommendation before anything is written back.

## Working Solution Sketch

| Layer | PM-Level Explanation | Proposed Choice |
|---|---|---|
| Trigger | How the process starts | New inbound lead or manual pilot upload |
| Source systems | Where lead and account context comes from | Salesforce, Gmail, LinkedIn Sales Navigator, Slack, spreadsheet/list imports |
| Agentic framework | How reasoning is organized | {decisions.get('Orchestration', 'CrewAI')} |
| Retrieval | How similar historical cases are found | RAG over Salesforce opportunities and sales notes |
| Vector database | Where embeddings are searched | {decisions.get('Vector DB', 'ChromaDB')} |
| LLM | What generates explanations and recommendations | {decisions.get('LLM', 'Claude Sonnet 4.6')} |
| Human approval | What prevents unsafe automation | Draft Salesforce update before write-back |
| Outputs | What users receive | Lead score, explanation, recommended sales rep, Slack summary, CRM draft |

## Hard vs Easy

**Hard**
- Cleaning Salesforce won/lost history enough for reliable similarity matching.
- Defining score thresholds that the coordinator, sales manager, and reps all trust.
- Showing source citations so the AI does not feel like a black-box score.
- Handling rep routing conflicts across territory, product category, and existing account ownership.
- Managing Gmail and LinkedIn permissions without over-expanding the pilot.

**Easier**
- Running the first pilot from pasted or exported lead samples.
- Normalizing lead messages and extracting urgency/equipment mentions.
- Producing a first score explanation from a deterministic rubric.
- Creating Slack summaries for manager visibility.
- Keeping Salesforce updates as drafts until approved.

## PM Follow-Up Questions

- [ ] Which Salesforce objects and fields contain the best opportunity, account, invoice, and sales-note history?
- [ ] What scoring thresholds define high, medium, and low priority?
- [ ] Which reps can receive routed leads, and what rules decide ownership?
- [ ] Which enrichment sources are approved for the pilot?
- [ ] Who approves the draft Salesforce update before it is written back?
"""
