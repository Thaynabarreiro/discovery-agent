#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
"$PROJECT_DIR/scripts/build_dock_launcher.sh"

echo "Discovery Agent Launcher is installed at:"
echo "$HOME/Applications/Discovery Agent Launcher.app"
