"""Evaluation flow for class_basic_flow."""
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from mlops.common.config_utils import MLOpsConfig
from flows.class_basic_flow.standard.extract_entities import EntityExtraction
from src.evaluators.match_evaluator import MatchEvaluator
from mlops.common.naming_tools import generate_experiment_name
from promptflow.client import PFClient
from promptflow.entities import AzureOpenAIConnection
from promptflow.core import AzureOpenAIModelConfiguration


def main():
    """Implement parameter reading and evaluation flow."""
    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environemnt=args.environment_name)
    flow_config = mlops_config.get_flow_config(flow_name="class_basic_flow")

    aoai_deployment = flow_config["deployment_name"]

    openai_config = mlops_config.aoai_config

    connection = AzureOpenAIConnection(
        name=flow_config["connection_name"],
        api_key=openai_config["aoai_api_key"],
        api_base=openai_config["aoai_api_base"],
        api_type="azure",
        api_version=openai_config["aoai_api_version"],
    )

    pf = PFClient()
    pf.connections.create_or_update(connection)

    # create the model config to be used in below flow calls
    config = AzureOpenAIModelConfiguration(
        connection=flow_config["connection_name"], azure_deployment=aoai_deployment
    )

    # Run the flow as a basic function call with no tracing
    obj_chat = EntityExtraction(model_config=config)

    matchevaluator = MatchEvaluator()

    data_eval_path = flow_config['eval_data_path']

    aistudio_config = mlops_config.aistudio_config
    print(aistudio_config["project_name"])

    results = evaluate(
        evaluation_name=generate_experiment_name("class_basic_flow"),
        data=data_eval_path,
        target=obj_chat,
        evaluators={
            "matchevaluator": matchevaluator,
        },
        evaluator_config={
            "matchevaluator": {
                "response": "${target.answer}",
                "ground_truth": "${data.results}"
            },
        },
        azure_ai_project={
            "subscription_id": aistudio_config["subscription_id"],
            "resource_group_name": aistudio_config["resource_group_name"],
            "project_name": aistudio_config["project_name"]
        }
    )

    pprint(results)


if __name__ == "__main__":
    main()
