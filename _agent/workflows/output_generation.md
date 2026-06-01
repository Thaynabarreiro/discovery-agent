# Output Generation SOP

## Objective

Generate a client-safe proposal PDF and an engineering-ready Markdown spec from the final agent outputs.

## Client Proposal Rules

- Use executive plain English.
- Do not mention stack, frameworks, APIs, models, API keys, or environment variables.
- Focus on business outcome, timeline, deliverables, and next steps.
- Use `templates/client_proposal.html` and WeasyPrint.
- Target one A4 page, allowing two pages if the content requires it.

## Engineering Spec Rules

- Use pure Markdown.
- Include the exact framework and stack decisions table.
- Justify each technical choice based on the transcript and RAG results.
- Include measurable acceptance criteria.
- Include env var names and owners, never values.
- Keep open questions as checkboxes.

## PDF Generation

1. Render the HTML template with proposal content.
2. Write a temporary HTML file under `output/`.
3. Convert it to PDF with WeasyPrint.
4. If WeasyPrint fails, save the HTML fallback and print a clear terminal warning.

## Markdown Generation

1. Build Markdown from the structured engineering payload.
2. Save to `output/engineering_spec_YYYY-MM-DD_HH-MM.md`.
3. Keep all content editable and GitHub/Notion friendly.

## GitHub Upload

1. Initialize git if needed.
2. Keep `.env`, `.chromadb/`, `output/`, and generated chunks out of git.
3. Commit with `discovery-agent: [client_name] - [date]`.
4. If no remote exists, create one with GitHub CLI.
5. If a remote exists, push to `origin main`.
6. Print the repository URL.
