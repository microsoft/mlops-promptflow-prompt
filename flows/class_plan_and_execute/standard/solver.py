"""Solver node for the plan_and_execute flow."""
try:
    from flows.class_plan_and_execute.standard.multiprocressed_agents import (
    MultiProcessedAssistantAgent as AssistantAgent,
    )
except ImportError:
    from multiprocressed_agents import MultiProcessedAssistantAgent as AssistantAgent
import os
from promptflow.tracing import trace


class Solver:
    """Solver agent."""

    def __init__(self, system_message_path: str):
        """Initialize the solver agent."""
        self.config_list = [
            {
                "model": os.getenv("aoai_model_gpt4"),
                "api_key": os.getenv("aoai_api_key"),
                "base_url": os.getenv("aoai_base_url"),
                "api_type": "azure",
                "api_version": os.getenv("aoai_api_version"),
            }
        ]

        with open(system_message_path, "r") as file:
            system_message = file.read()

        self.solver = AssistantAgent(
            name="SOLVER",
            description="An agent expert in creating a final response to the user's request.",
            system_message=system_message,
            code_execution_config=False,
            llm_config={
                "config_list": self.config_list,
                "timeout": 60,
                "cache_seed": None,
            },
        )

    @trace
    def generate_response(self, question: str, results: str) -> str:
        """Generate a final response to the user's request."""
        solver_message = f"""
        Question:
        {question}

        Step results:
        {results}
        """

        return self.solver.generate_reply(
            messages=[{"content": solver_message, "role": "user"}]
        )
