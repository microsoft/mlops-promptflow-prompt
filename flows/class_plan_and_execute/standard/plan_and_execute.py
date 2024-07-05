"""Implement plan_and_execute flow as a class."""
import json
import sys
import os
from typing import Any
from autogen.agentchat import register_function
from promptflow.tracing import start_trace
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from planner import Planner  # noqa: E402
from executor import Executor  # noqa: E402
from solver import Solver  # noqa: E402
from tools import (  # noqa: E402
    tool_descriptions,
    _web_tool,
    _llm_tool,
    _wikipedia_tool,
    _math_tool,
)


class PlanAndExecute:
    """Implement the flow."""

    def web_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the web_tool function."""
        return _web_tool(*args, **kwargs)

    def llm_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the llm_tool function."""
        return _llm_tool(*args, **kwargs)

    def wikipedia_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the wikipedia_tool function."""
        return _wikipedia_tool(*args, **kwargs)

    def math_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the math_tool function."""
        return _math_tool(*args, **kwargs)

    wrapper_mapping = {
        "web_tool": web_tool,
        "llm_tool": llm_tool,
        "wikipedia_tool": wikipedia_tool,
        "math_tool": math_tool,
    }

    def __init__(
        self, planner_system_message_path: str, solver_system_message_path: str
    ):
        """Initialize the environment."""
        start_trace(collection="plan_and_execute")
        self.planner = Planner(system_message_path=planner_system_message_path)
        self.executor = Executor()
        self.solver = Solver(system_message_path=solver_system_message_path)

        self.initialized = False

    def __call__(self, *, question: str, **kwargs):
        """Invoke the flow for a single request."""
        if not self.initialized:
            for tool_name, wrapper in self.wrapper_mapping.items():
                register_function(
                    wrapper,
                    caller=self.planner.planner,
                    executor=self.executor.executor,
                    description=tool_descriptions[tool_name]["function"],
                )
            self.initialized = True

        plan = self.planner.generate_plan(question=question)
        execution = self.executor.execute_plan_parallel(plan=plan)
        response = self.solver.generate_response(question=question, results=execution)
        plan_json = json.loads(plan)
        number_of_steps = len(plan_json["Plan"])

        return {
            "plan": plan,
            "steps": execution,
            "answer": response,
            "number_of_steps": number_of_steps,
        }
