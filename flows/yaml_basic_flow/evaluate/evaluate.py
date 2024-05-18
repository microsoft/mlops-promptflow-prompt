import os
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from promptflow.client import load_flow
from promptflow.entities import FlowContext
from promptflow.entities import AzureOpenAIConnection
from mlops.common.config_utils import MLOpsConfig
from src.evaluators.match_evaluator import MatchEvaluator
from mlops.common.naming_tools import generate_experiment_name



def main():

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
    flow_config = mlops_config.get_flow_config(flow_name="yaml_basic_flow")

    matchEvaluator = MatchEvaluator()

    data_eval_path = flow_config['eval_data_path']
    flow_standard_path = flow_config["standard_flow_path"]
    aoai_deployment = flow_config["deployment_name"]

    aistudio_config = mlops_config.aistudio_config
    openai_config = mlops_config.aoai_config

    connection = AzureOpenAIConnection(
        name=flow_config["connection_name"],
        api_key=openai_config["aoai_api_key"],
        api_base=openai_config["aoai_api_base"],
        api_type="azure",
        api_version=openai_config["aoai_api_version"],
    )

    flow = load_flow(flow_standard_path)
    flow.context = FlowContext(
        overrides={"nodes.NER_LLM.inputs.deployment_name": aoai_deployment},
        connections={"NER_LLM": {"connection": connection}}
    )

    results = evaluate(
        evaluation_name=generate_experiment_name("yaml_basic_flow"),
        data=data_eval_path,
        target=flow,
        evaluators={
            "matchevaluator": matchEvaluator,
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
