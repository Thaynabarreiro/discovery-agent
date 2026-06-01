#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Discovery Agent Launcher"
APP_PATH="$HOME/Applications/$APP_NAME.app"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$HOME/Applications"

osascript_source=$(mktemp)
cat > "$osascript_source" <<'APPLESCRIPT'
set actionChoice to choose from list {"Start Live Call", "Stop Live Call", "Run Test Transcript"} with prompt "Discovery Agent" default items {"Start Live Call"}
if actionChoice is false then return
set actionChoice to item 1 of actionChoice

if actionChoice is "Start Live Call" then
  set clientName to text returned of (display dialog "Client/company name:" default answer "")
  set sessionType to choose from list {"Discovery Call", "Interview", "Internal Meeting", "Other"} with prompt "Session type:" default items {"Discovery Call"}
  if sessionType is false then return
  set sessionType to item 1 of sessionType
  set response to do shell script "__PYTHON__ __SCRIPT__ start --client-name " & quoted form of clientName & " --session-type " & quoted form of sessionType
  display dialog response buttons {"OK"} default button "OK"
else if actionChoice is "Stop Live Call" then
  set sessionId to text returned of (display dialog "Paste session_id from the start response:" default answer "")
  set response to do shell script "__PYTHON__ __SCRIPT__ stop --session-id " & quoted form of sessionId
  display dialog response buttons {"OK"} default button "OK"
else
  set transcriptPath to POSIX path of (choose file with prompt "Choose a transcript .txt file")
  set response to do shell script "__PYTHON__ __SCRIPT__ test --transcript-path " & quoted form of transcriptPath
  display dialog response buttons {"OK"} default button "OK"
end if
APPLESCRIPT

python_path="$PROJECT_DIR/.venv/bin/python"
script_path="$PROJECT_DIR/scripts/dock_launcher_action.py"
python3 - "$osascript_source" "$python_path" "$script_path" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
text = path.read_text()
text = text.replace("__PYTHON__", sys.argv[2]).replace("__SCRIPT__", sys.argv[3])
path.write_text(text)
PY

osacompile -o "$APP_PATH" "$osascript_source"
rm "$osascript_source"

echo "Created $APP_PATH"
echo "Drag it to the Dock, or run: open '$APP_PATH'"
