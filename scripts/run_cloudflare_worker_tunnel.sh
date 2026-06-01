#!/usr/bin/env bash
set -euo pipefail

cloudflared tunnel \
  --config /Users/thaynamartinsbarreiro/.cloudflared/discovery-agent-worker.yml \
  run
