"""Evaluation flow for yaml_basic_flow."""
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from mlops.common.config_utils import MLOpsConfig
from src.evaluators.match_evaluator import MatchEvaluator
from flows.yaml_basic_flow.evaluate.flow_wrapper import StandardFlowWrapper
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
    flow_config = mlops_config.get_flow_config(flow_name="yaml_basic_flow")

    matchevaluator = MatchEvaluator()

    data_eval_path = flow_config['eval_data_path']
    flow_standard_path = flow_config["standard_flow_path"]
    aoai_deployment = flow_config["deployment_name"]

    aistudio_config = mlops_config.aistudio_config
    openai_config = mlops_config.aoai_config

    flow = StandardFlowWrapper(flow_standard_path, flow_config["connection_name"], aoai_deployment, openai_config)

    results = evaluate(
        evaluation_name=generate_experiment_name("yaml_basic_flow"),
        data=data_eval_path,
        target=flow,
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
