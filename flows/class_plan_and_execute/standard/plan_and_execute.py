"""Implement plan_and_execute flow as a class."""
from flows.class_plan_and_execute.standard.planner import Planner
from flows.class_plan_and_execute.standard.executor import Executor
from flows.class_plan_and_execute.standard.solver import Solver
from flows.class_plan_and_execute.standard.tools import (
    tool_descriptions,
    _web_tool,
    _llm_tool,
    _wikipedia_tool,
    _math_tool,
)
from typing import Any
from autogen.agentchat import register_function


class PlanAndExecute:
    """Implement the flow."""

    # tool wrappers for the agents
    # need to be staticmethod to have _name attribute

    @staticmethod
    def web_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the web_tool function."""
        return _web_tool(*args, **kwargs)

    @staticmethod
    def llm_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the llm_tool function."""
        return _llm_tool(*args, **kwargs)

    @staticmethod
    def wikipedia_tool(*args: Any, **kwargs: Any) -> Any:
        """Wrap the wikipedia_tool function."""
        return _wikipedia_tool(*args, **kwargs)

    @staticmethod
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
        number_of_steps = len(plan["Plan"])

        return {
            "plan": plan,
            "steps": execution,
            "answer": response,
            "number_of_steps": number_of_steps,
        }
