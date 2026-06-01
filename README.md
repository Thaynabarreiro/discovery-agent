# Discovery Agent

Discovery Agent is a Python 3.11+ project that follows the WAT architecture:

- **Workflows**: SOPs in `_agent/workflows/`
- **Agents**: CrewAI-backed coordination in `_agent/agents/`
- **Tools**: deterministic Python scripts in `_agent/tools/`

It captures or receives a discovery call transcript and generates:

1. `client_proposal.pdf` for the client
2. `engineering_spec.md` for the engineering team

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with your API keys. For live call capture on macOS, install:

```bash
brew install switchaudio-osx
```

Install BlackHole 2ch separately and make sure it appears as an audio input device.

## Run

```bash
python main.py
```

The default pipeline uses deterministic local Python classes so you can test the project before every API is configured. `_agent/agents/crew.py` provides the CrewAI orchestration layer for production-style coordination with the configured model.

CrewAI runs when `ENABLE_CREWAI=true` is present in `.env`. It runs after a transcript is available and before PDF/Markdown generation. If CrewAI fails because of a dependency, model name, or provider issue, the deterministic pipeline continues and prints a warning.

## CrewAI AMP / Studio Deployment

This project includes `pyproject.toml` and `_agent/crew_entrypoint.py` so CrewAI AMP can detect and run it as a deployable crew.

Local login and deploy flow:

```bash
source .venv/bin/activate
crewai login
crewai deploy create
crewai deploy status
```

Required environment variables for AMP:

```env
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
CHROMA_PERSIST_DIR=.chromadb
DEFAULT_MODEL=anthropic/claude-sonnet-4-6
GITHUB_REPO_NAME=discovery-agent
ENABLE_CREWAI=true
ENABLE_GITHUB_UPLOAD=false
```

For AMP deployment, keep `ENABLE_GITHUB_UPLOAD=false` unless the deployed runtime should push generated artifacts back to GitHub.

## What You Need To Provide

- `ANTHROPIC_API_KEY` for Claude generation.
- `OPENAI_API_KEY` for Whisper transcription in live mode.
- Any client system credentials required by the generated engineering spec.
- GitHub CLI authentication if you want automatic repository creation and push:

```bash
gh auth login
```

## Notes

- `output/` and `.chromadb/` are intentionally ignored by git.
- If `knowledge_base/` is empty, RAG search will warn and the agents will continue without case references.
