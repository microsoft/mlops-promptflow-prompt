"""Planner node for the plan_and_execute flow."""
import os
from flows.class_plan_and_execute.standard.multiprocressed_agents import (
    MultiProcessedAssistantAgent as AssistantAgent,
)
import json
from promptflow.tracing import trace


class Planner:
    """Planner agent."""

    def __init__(self, system_message_path: str):
        """Initialize the planner agent."""
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

        self.planner = AssistantAgent(
            name="PLANNER",
            description="An agent expert in creating a step-by-step execution plan to solve the user's request.",
            system_message=system_message,
            code_execution_config=False,
            llm_config={
                "config_list": self.config_list,
                "temperature": 0,
                "timeout": 120,
                "cache_seed": None,
            },
        )

        # register_tools(self.planner)

    @trace
    def generate_plan(self, question: str) -> str:
        """Generate a step-by-step execution plan to solve the user's request."""
        planner_reply = self.planner.generate_reply(
            messages=[{"content": question, "role": "user"}]
        )
        planner_reply = planner_reply.replace("```json", "").replace("```", "").strip()
        try:
            plan = json.loads(planner_reply)
        except json.JSONDecodeError:
            plan = {}

        return plan
