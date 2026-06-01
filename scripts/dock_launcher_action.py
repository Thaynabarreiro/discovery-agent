#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


N8N_BASE_URL = os.getenv("DISCOVERY_AGENT_N8N_BASE_URL", "https://n8n.moveai.pro")
START_URL = f"{N8N_BASE_URL.rstrip('/')}/webhook/discovery-agent/start"
STOP_URL = f"{N8N_BASE_URL.rstrip('/')}/webhook/discovery-agent/stop"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "test"])
    parser.add_argument("--client-name", default="")
    parser.add_argument("--session-type", default="Discovery Call")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--transcript-path", default="")
    args = parser.parse_args()

    if args.action == "start":
        payload = {
            "client_name": args.client_name,
            "session_type": args.session_type,
            "mode": "live",
            "push_to_github": False,
        }
        print(_post_json(START_URL, payload))
    elif args.action == "stop":
        payload = {"session_id": args.session_id, "push_to_github": False}
        print(_post_json(STOP_URL, payload))
    else:
        transcript = Path(args.transcript_path).read_text(encoding="utf-8", errors="ignore")
        payload = {"mode": "manual", "transcript": transcript, "push_to_github": False}
        print(_post_json(START_URL, payload))


def _post_json(url: str, payload: dict) -> str:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DiscoveryAgentLauncher/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        return f"Request failed: {exc}. Make sure n8n and the local worker are running."


if __name__ == "__main__":
    main()
