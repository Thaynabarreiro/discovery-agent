from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class DiscoveryAgent:
    """Discovery call crew for CrewAI AMP / Studio deployment."""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def intake_parser(self) -> Agent:
        return Agent(config=self.agents_config["intake_parser"], verbose=True)  # type: ignore[index]

    @agent
    def solution_architect(self) -> Agent:
        return Agent(config=self.agents_config["solution_architect"], verbose=True)  # type: ignore[index]

    @agent
    def scope_estimator(self) -> Agent:
        return Agent(config=self.agents_config["scope_estimator"], verbose=True)  # type: ignore[index]

    @agent
    def proposal_drafter(self) -> Agent:
        return Agent(config=self.agents_config["proposal_drafter"], verbose=True)  # type: ignore[index]

    @task
    def intake_task(self) -> Task:
        return Task(config=self.tasks_config["intake_task"])  # type: ignore[index]

    @task
    def architecture_task(self) -> Task:
        return Task(config=self.tasks_config["architecture_task"])  # type: ignore[index]

    @task
    def scope_task(self) -> Task:
        return Task(config=self.tasks_config["scope_task"])  # type: ignore[index]

    @task
    def drafting_task(self) -> Task:
        return Task(config=self.tasks_config["drafting_task"], output_file="engineering_spec.md")  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
