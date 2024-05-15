
from promptflow import tool

from autogen import AssistantAgent
from connection_utils import CustomConnection
from tools import register_tools

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def planner_tool(connection: CustomConnection, system_message: str, question: str) -> str:

    config_list_gpt4 = [{
        "model": connection.configs["aoai_model_gpt4"],
        "api_key": connection.secrets["aoai_api_key"],
        "base_url": connection.configs["aoai_base_url"],
        "api_type": "azure",
        "api_version": connection.configs["aoai_api_version"]
    }]

    planner = AssistantAgent(
        name="PLANNER",
        description="""
        An agent expert in creating a step-by-step execution plan to solve the user's request.
        """,
        system_message=system_message,
        code_execution_config=False,
        llm_config={
            "config_list": config_list_gpt4,
            "temperature": 0,
            "timeout": 120,
            "cache_seed": None
        }
    )

    register_tools(planner)

    planner_reply = planner.generate_reply(messages=[{"content": question, "role": "user"}])
    planner_reply = planner_reply.replace("```json", "").replace("```", "").strip()

    return planner_reply
