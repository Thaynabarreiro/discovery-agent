#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up -d
echo "n8n is starting at http://localhost:5678"
echo "Import workflow: n8n/workflows/discovery_agent_hybrid_workflow.json"
