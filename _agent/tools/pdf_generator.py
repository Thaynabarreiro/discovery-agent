from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path


def generate_client_proposal(payload: dict, output_dir: str = "output") -> Path:
    now = datetime.now()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    proposal = payload["client_proposal"]
    template = Path("templates/client_proposal.html").read_text(encoding="utf-8")
    html = template.format(
        client_name=escape(proposal["client_name"]),
        date=now.strftime("%Y-%m-%d"),
        what_discussed="".join(f"<p>{escape(p)}</p>" for p in proposal["what_discussed"]),
        what_building=escape(proposal["what_building"]),
        highlight=escape(proposal["highlight"]),
        deliverables="".join(f"<li>{escape(item)}</li>" for item in proposal["deliverables"]),
        timeline="".join(f"<li>{escape(item)}</li>" for item in proposal["timeline"]),
        next_steps="".join(f"<li>{escape(item)}</li>" for item in proposal["next_steps"]),
    )

    html_path = out_dir / f"client_proposal_{now:%Y-%m-%d_%H-%M}.html"
    pdf_path = out_dir / f"client_proposal_{now:%Y-%m-%d_%H-%M}.pdf"
    html_path.write_text(html, encoding="utf-8")

    try:
        from weasyprint import HTML

        HTML(string=html, base_url=str(Path.cwd())).write_pdf(str(pdf_path))
        return pdf_path
    except Exception as exc:
        print(f"WeasyPrint failed: {exc}. HTML fallback saved at {html_path}")
        return html_path
