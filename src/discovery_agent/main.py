from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime

from discovery_agent.crew import DiscoveryAgent


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    inputs = {
        "transcript": (
            "Client: TBD. Transcript was not provided. Produce a draft with explicit open questions "
            "and placeholders for missing facts."
        ),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }
    return DiscoveryAgent().crew().kickoff(inputs=inputs)


def run_with_trigger():
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Provide JSON payload as the first argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON payload provided as argument.") from exc

    transcript = trigger_payload.get("transcript") or trigger_payload.get("text") or ""
    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "transcript": transcript,
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }
    return DiscoveryAgent().crew().kickoff(inputs=inputs)


def train():
    inputs = {"transcript": "Training transcript placeholder.", "current_date": datetime.now().strftime("%Y-%m-%d")}
    return DiscoveryAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)


def replay():
    return DiscoveryAgent().crew().replay(task_id=sys.argv[1])


def test():
    inputs = {"transcript": "Test transcript placeholder.", "current_date": datetime.now().strftime("%Y-%m-%d")}
    return DiscoveryAgent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
