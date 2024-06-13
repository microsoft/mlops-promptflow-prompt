"""Executor node of the plan_and_execute flow."""
import os
import concurrent.futures
import json
from flows.class_plan_and_execute.standard.multiprocressed_agents import (
    MultiProcessedUserProxyAgent as UserProxyAgent,
)
from flows.class_plan_and_execute.standard.multiprocressed_agents import (
    MultiProcessedAssistantAgent as AssistantAgent,
)


class Executor:
    """Executor agent."""

    def __init__(self):
        """Initialize the executor agent."""
        self.config_list = [
            {
                "model": os.getenv("aoai_model_gpt35"),
                "api_key": os.getenv("aoai_api_key"),
                "base_url": os.getenv("aoai_base_url"),
                "api_type": "azure",
                "api_version": os.getenv("aoai_api_version"),
            }
        ]

        self.executor = UserProxyAgent(
            name="EXECUTOR",
            description=(
                "An agent that acts as a proxy for the user and executes the "
                "suggested function calls from PLANNER."
            ),
            code_execution_config=False,
            llm_config={
                "config_list": self.config_list,
                "timeout": 60,
                "cache_seed": None,
            },
            human_input_mode="NEVER",
        )

        # register_tools(self.executor)

    def _llm_tool(self, request, context, config_list):
        """Define the internal auxiliary LLM agent for the executor."""
        llm_assistant = AssistantAgent(
            name="LLM_ASSISTANT",
            description=(
                "An agent expert in answering requests by analyzing and "
                "extracting information from the given context."
            ),
            system_message=(
                "Given a request and optionally some context with potentially "
                "relevant information to answer it, analyze the context and "
                "extract the information needed to answer the request. Then, "
                "create a sentence that answers the request. You must strictly "
                "limit your response to only what was asked in the request."
            ),
            code_execution_config=False,
            llm_config={
                "config_list": config_list,
                "timeout": 60,
                "temperature": 0.3,
                "cache_seed": None,
            },
        )

        llm_assistant.clear_history()

        message = f"""
        Request:
        {request}

        Context:
        {context}
        """
        try:
            reply = llm_assistant.generate_reply(
                messages=[{"content": message, "role": "user"}]
            )
            return reply
        except Exception as e:
            return f"Error: {str(e)}"

    def _substitute_dependency(
        self, id, original_argument_value, dependency_value, config_list
    ):
        """Substitute dependencies in the execution plan."""
        instruction = (
            "Extract the entity name or fact from the dependency value in a way "
            "that makes sense to use it to substitute the variable #E in the "
            "original argument value. Do not include any other text in your "
            "response, other than the entity name or fact extracted."
        )

        context = f"""
        original argument value:
        {original_argument_value}

        dependency value:
        {dependency_value}

        extracted fact or entity:

        """

        return self._llm_tool(instruction, context, config_list)

    def _has_unresolved_dependencies(self, item, resolved_ids, plan_ids):
        """Check for unresolved dependencies in a plan step."""
        try:
            args = json.loads(item["function"]["arguments"])
        except json.JSONDecodeError:
            return False

        for arg in args.values():
            if isinstance(arg, str) and any(
                ref_id
                for ref_id in plan_ids
                if ref_id not in resolved_ids and ref_id in arg
            ):
                return True
        return False

    def _submit_task(self, item_id, item, thread_executor, executor_agent, futures):
        """Submit a task for execution."""
        arguments = item["function"]["arguments"]
        future = thread_executor.submit(
            executor_agent.execute_function,
            {"name": item["function"]["name"], "arguments": arguments},
        )
        futures[item_id] = future

    def _update_and_submit_task(
        self,
        item_id,
        item,
        thread_executor,
        executor_agent,
        futures,
        results,
        config_list,
    ):
        """Update the arguments of a task with dependency results and submit it for execution."""
        updated_arguments = json.loads(item["function"]["arguments"])
        for arg_key, arg_value in updated_arguments.items():
            if isinstance(arg_value, str):
                for res_id, res in results.items():
                    if arg_key == "context":
                        arg_value = arg_value.replace(res_id, res["content"])
                    else:
                        arg_value = arg_value.replace(
                            res_id,
                            self._substitute_dependency(
                                res_id, arg_value, res["content"], config_list
                            ),
                        )
                    updated_arguments[arg_key] = arg_value
        future = thread_executor.submit(
            executor_agent.execute_function,
            {
                "name": item["function"]["name"],
                "arguments": json.dumps(updated_arguments),
            },
        )
        futures[item_id] = future

    def _submit_ready_tasks(
        self,
        plan_ids,
        resolved_ids,
        futures,
        results,
        thread_executor,
        executor_agent,
        config_list,
    ):
        """Submit plan tasks that have all dependencies resolved and are ready to be executed."""
        for next_item_id, next_item in plan_ids.items():
            if (
                next_item_id not in resolved_ids
                and next_item_id not in futures
                and not self._has_unresolved_dependencies(
                    next_item, resolved_ids, plan_ids
                )
            ):
                self._update_and_submit_task(
                    next_item_id,
                    next_item,
                    thread_executor,
                    executor_agent,
                    futures,
                    results,
                    config_list,
                )

    def _process_done_future(
        self,
        future,
        futures,
        results,
        resolved_ids,
        plan_ids,
        thread_executor,
        executor_agent,
        config_list,
    ):
        """Process a completed future and trigger the submission of ready tasks."""
        item_id = next((id for id, f in futures.items() if f == future), None)
        if item_id:
            _, result = future.result()
            results[item_id] = result
            resolved_ids.add(item_id)
            del futures[item_id]
            self._submit_ready_tasks(
                plan_ids,
                resolved_ids,
                futures,
                results,
                thread_executor,
                executor_agent,
                config_list,
            )

    def execute_plan_parallel(self, plan):
        """Execute the plan in parallel."""
        plan = plan["Functions"]
        plan_ids = {item["id"]: item for item in plan}
        results = {}
        resolved_ids = set()
        futures = {}

        with concurrent.futures.ThreadPoolExecutor() as thread_executor:
            for item_id, item in plan_ids.items():
                if not self._has_unresolved_dependencies(item, resolved_ids, plan_ids):
                    self._submit_task(
                        item_id, item, thread_executor, self.executor, futures
                    )

            while futures:
                done, _ = concurrent.futures.wait(
                    futures.values(), return_when=concurrent.futures.FIRST_COMPLETED
                )
                for future in done:
                    self._process_done_future(
                        future,
                        futures,
                        results,
                        resolved_ids,
                        plan_ids,
                        thread_executor,
                        self.executor,
                        self.config_list,
                    )

        result_str = "\n".join(
            [f"{key} = {value['content']}" for key, value in results.items()]
        )
        return result_str
