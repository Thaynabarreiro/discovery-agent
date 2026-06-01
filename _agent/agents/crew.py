from __future__ import annotations

import os


def build_discovery_crew(transcript: str):
    try:
        from crewai import Agent, Crew, Process, Task
    except Exception as exc:
        raise RuntimeError(f"CrewAI is not installed or could not be imported: {exc}") from exc

    model = os.getenv("DEFAULT_MODEL", "claude-sonnet-4-6")
    intake_agent = Agent(
        role="Business Analyst",
        goal="Extract structured business context from the transcript.",
        backstory="You turn messy discovery notes into reliable structured inputs.",
        llm=model,
    )
    architect_agent = Agent(
        role="AI Solutions Architect",
        goal="Define and justify the technical architecture for this case.",
        backstory="You choose pragmatic AI architecture based on complexity, risk, and delivery constraints.",
        llm=model,
    )
    estimator_agent = Agent(
        role="Technical Project Manager",
        goal="Estimate scope, phases, risks, acceptance criteria, and environment needs.",
        backstory="You convert technical ambiguity into measurable delivery plans.",
        llm=model,
    )
    drafter_agent = Agent(
        role="Client Communications Lead",
        goal="Draft final client-facing and engineering-facing content.",
        backstory="You communicate business value clearly while preserving technical depth for engineers.",
        llm=model,
    )

    tasks = [
        Task(description=f"Extract intake JSON from this transcript:\n\n{transcript}", expected_output="Valid intake JSON.", agent=intake_agent),
        Task(description="Define framework, model, vector DB, and infra decisions with specific rationale.", expected_output="Architecture decisions.", agent=architect_agent),
        Task(description="Estimate phases, acceptance criteria, limitations, watch points, infra cost, and env vars.", expected_output="Scope estimate.", agent=estimator_agent),
        Task(description="Draft content for client_proposal.pdf and engineering_spec.md.", expected_output="Final document content.", agent=drafter_agent),
    ]
    return Crew(agents=[intake_agent, architect_agent, estimator_agent, drafter_agent], tasks=tasks, process=Process.sequential)


def run_discovery_crew(transcript: str) -> str:
    crew = build_discovery_crew(transcript)
    result = crew.kickoff()
    return str(result)
