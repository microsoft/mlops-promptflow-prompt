"""Evaluation flow for class_basic_flow."""
import os
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from mlops.common.config_utils import MLOpsConfig
from flows.class_basic_flow.standard.extract_entities import EntityExtraction
from src.evaluators.match_evaluator import MatchEvaluator
from mlops.common.naming_tools import generate_experiment_name


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

    os.environ["AZURE_OPENAI_API_KEY"] = openai_config["aoai_api_key"]
    os.environ["AZURE_OPENAI_API_VERSION"] = openai_config["aoai_api_version"]
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = aoai_deployment
    os.environ["AZURE_OPENAI_ENDPOINT"] = openai_config["aoai_api_base"]

    matchevaluator = MatchEvaluator()

    eval_dataset_config = mlops_config.get_dataset_config(name="basic_flow_eval")
    data_eval_path = eval_dataset_config['data_path']

    aistudio_config = mlops_config.aistudio_config
    print(aistudio_config["project_name"])

    results = evaluate(
        evaluation_name=generate_experiment_name("class_basic_flow"),
        data=data_eval_path,
        target=EntityExtraction,
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
