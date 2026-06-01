# Discovery Agent Hybrid Process Logic

## Simple Continuity

```mermaid
flowchart LR
  A["1. Discovery Agent Launcher"] --> B["2. n8n receives webhook"]
  B --> C["3. Cloudflare Tunnel routes to Mac"]
  C --> D["4. Local FastAPI worker"]
  D --> E{"5. Input mode"}
  E --> F["Live: BlackHole/sounddevice/Whisper"]
  E --> G["Transcript: file or pasted text"]
  F --> H["6. CrewAI crew runs agents"]
  G --> H
  H --> I["7. RAG searches ChromaDB"]
  I --> J["8. Agents produce scope and content"]
  J --> K["9. PDF, engineering spec, PM review"]
```

## Agentic Framework Vocabulary

| Component | Agentic Term | What It Means Here |
|---|---|---|
| Dock app | Human trigger / UI shell | A small macOS launcher that starts or stops the workflow. |
| n8n | Orchestrator | Coordinates systems, webhooks, notifications, retries, and storage. |
| Local worker | Runtime worker | A Python service on the Mac that can access local audio devices and files. |
| Audio capture | Deterministic tool | Non-LLM code that records chunks from the selected audio input. |
| Whisper | Transcription tool | Converts audio chunks into text. |
| Transcript buffer | Shared state | Accumulates transcribed text during the call. |
| CrewAI | Agentic framework | Coordinates specialist agents and exposes traces/observability. |
| Crew | Multi-agent workflow | The group of agents working sequentially on the transcript. |
| Agent | Role-based reasoning unit | A specialized role such as IntakeParser or SolutionArchitect. |
| Task | Work unit | A specific instruction assigned to an agent. |
| RAG | Retrieval-augmented generation | Finds similar cases before generating architecture/scope decisions. |
| Vector DB | Embedding search store | ChromaDB locally, persisted in `.chromadb/`, using local sentence-transformer embeddings. |
| Artifact generator | Deterministic output tool | Creates PDF, Markdown spec, and PM review files. |
| Human approval | Human-in-the-loop | The PM/client reviews outputs before sharing or implementation. |

## CrewAI Agents

| Agent | Role | What It Does |
|---|---|---|
| IntakeParser | Business Analyst | Extracts client name, industry, core problem, current tools, integrations, urgency, budget signal, and complexity from the transcript. |
| SolutionArchitect | AI Solutions Architect | Chooses the architecture, framework, model strategy, and technical rationale for the specific case. Uses RAG context from ChromaDB. |
| ScopeEstimator | Technical Project Manager | Turns complexity into phases, timeline, acceptance criteria, limitations, watch points, production costs, and required environment variables. |
| ProposalDrafter | Client Communications Lead | Drafts the executive proposal content and the engineering-ready Markdown content. |

## RAG / Vector DB

The RAG layer uses **ChromaDB** as the local persistent vector database. Documents in `knowledge_base/` are chunked, embedded with `sentence-transformers/all-MiniLM-L6-v2`, and searched for the top similar cases. The SolutionArchitect uses those retrieved cases as grounding context before recommending architecture and scope.

## Why n8n + CrewAI Together

n8n is better for process automation: webhooks, triggers, storage, retries, notifications, and integration routing.

CrewAI is better for agentic reasoning: specialist agents, tasks, traces, LLM calls, and structured analysis.

The local Mac is necessary for live call capture because BlackHole, microphone/input routing, and local audio permissions live on the computer.
