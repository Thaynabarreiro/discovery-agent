# Manual Mode SOP

## Objective

Process a pasted transcript or transcript file and generate the client proposal PDF plus the engineering spec Markdown.

## Accepted Inputs

- Plain text pasted into the terminal.
- Path to a `.txt` or `.md` transcript file.

## Processing Steps

1. Normalize the transcript text.
2. Run `IntakeParser` to extract structured business context.
3. Run `SolutionArchitect` with optional RAG search over `knowledge_base/`.
4. Run `ScopeEstimator` to define phases, acceptance criteria, limitations, and environment variables.
5. Run `ProposalDrafter` to produce client-facing and engineering-facing content.
6. Generate:
   - `output/client_proposal_YYYY-MM-DD_HH-MM.pdf`
   - `output/engineering_spec_YYYY-MM-DD_HH-MM.md`
7. Attempt GitHub upload if git and GitHub CLI are configured.

## Ambiguous or Incomplete Text

- Preserve uncertainty as open questions.
- Do not invent client credentials, budgets, or exact dates.
- If key facts are missing, use `TBD` in engineering outputs and plain executive language in the proposal.
- Keep generated timelines relative, never fixed to calendar dates.

## Expected Outputs

- A polished client proposal PDF with no technical stack details.
- An editable Markdown engineering spec with framework rationale, phases, risks, and env vars.
