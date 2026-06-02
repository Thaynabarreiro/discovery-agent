from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def extract_discovery_date(transcript: str) -> str:
    patterns = [
        r"\bDate\s*[:\-]\s*(\d{4}-\d{2}-\d{2})",
        r"\bDiscovery Date\s*[:\-]\s*(\d{4}-\d{2}-\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def slugify(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    clean = re.sub(r"-+", "-", clean).strip("-")
    return clean or "client"


def artifact_prefix(client_name: str, discovery_date: str) -> str:
    return f"{discovery_date}_{slugify(client_name)}"


def artifact_output_dir(client_name: str, discovery_date: str, base_dir: str = "output") -> Path:
    return Path(base_dir) / artifact_prefix(client_name, discovery_date)
