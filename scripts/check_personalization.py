from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader


REQUIRED_TERMS = [
    "Atlas Industrial Supply",
    "Salesforce",
    "lead score",
    "sales rep",
    "human approval",
]

FORBIDDEN_TERMS = [
    "turns call notes into a client-ready proposal",
    "client-ready proposal generated from each call",
    "discovery call transcripts",
    "Discovery notes become",
    "document-generation layer that produces both an executive proposal",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_personalization.py <output_dir>")
        return 2

    output_dir = Path(sys.argv[1])
    pdf_path = output_dir / "client_proposal.pdf"
    spec_path = output_dir / "engineering_spec.md"
    pm_path = output_dir / "pm_call_review.md"

    missing_files = [str(path) for path in (pdf_path, spec_path, pm_path) if not path.exists()]
    if missing_files:
        print("Missing generated files:")
        print("\n".join(missing_files))
        return 1

    pdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages)
    combined = "\n".join([pdf_text, spec_path.read_text(encoding="utf-8"), pm_path.read_text(encoding="utf-8")])
    lower_combined = combined.lower()

    failures = []
    for term in REQUIRED_TERMS:
        if term.lower() not in lower_combined:
            failures.append(f"Required term missing: {term}")
    for term in FORBIDDEN_TERMS:
        if term.lower() in lower_combined:
            failures.append(f"Generic/internal phrase found: {term}")
    if "under 1 hour" not in lower_combined and "within one hour" not in lower_combined:
        failures.append("Expected one-hour routing outcome is missing.")

    if failures:
        print("Personalization check failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    print("Personalization check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
