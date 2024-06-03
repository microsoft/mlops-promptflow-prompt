"""Evaluation flow for plan_and_execute flow."""
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from promptflow.core import AzureOpenAIModelConfiguration
from mlops.common.config_utils import MLOpsConfig
from src.evaluators.json_evaluator import JsonEvaluator
from src.evaluators.executor_evaluator import ExecutorEvaluator
from promptflow.evals.evaluators import GroundednessEvaluator, RelevanceEvaluator, SimilarityEvaluator
from flows.plan_and_execute.evaluate.flow_wrapper import PlanAndExecuteFlowWrapper
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
    flow_config = mlops_config.get_flow_config(flow_name="plan_and_execute")

    json_schema_path = flow_config["json_schema_path"]
    data_eval_path = flow_config['eval_data_path']
    flow_standard_path = flow_config["standard_flow_path"]

    aistudio_config = mlops_config.aistudio_config
    openai_config = mlops_config.aoai_config

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=openai_config["aoai_api_base"],
        api_key=openai_config["aoai_api_key"],
        api_version=openai_config["aoai_api_version"],
        azure_deployment=flow_config["deployment_name_gpt4"]
    )

    json_evaluator = JsonEvaluator(json_schema_path)
    executor_evaluator = ExecutorEvaluator()
    groundedness_evaluator = GroundednessEvaluator(model_config)
    relevance_evaluator = RelevanceEvaluator(model_config)
    similarity_evaluator = SimilarityEvaluator(model_config)

    connection_secrets = {
        "aoai_api_key": openai_config["aoai_api_key"],
        "bing_api_key": flow_config["bing_api_key"]
    }

    connection_configs = {
        "aoai_model_gpt4": flow_config["deployment_name_gpt4"],
        "aoai_model_gpt35": flow_config["deployment_name_gpt35"],
        "aoai_base_url": openai_config["aoai_api_base"],
        "aoai_api_version": flow_config["aoai_api_version"],
        "bing_endpoint": flow_config["bing_endpoint"]
    }

    flow = PlanAndExecuteFlowWrapper(
        flow_standard_path, flow_config["connection_name"],
        connection_secrets, connection_configs
    )

    results = evaluate(
        evaluation_name=generate_experiment_name("plan_and_execute"),
        data=data_eval_path,
        target=flow,
        evaluators={
            "json_evaluator": json_evaluator,
            "executor_evaluator": executor_evaluator,
            "groundedness_evaluator": groundedness_evaluator,
            "relevance_evaluator": relevance_evaluator,
            "similarity_evaluator": similarity_evaluator
        },
        evaluator_config={
            "json_evaluator": {
                "json_string": "${target.plan}"
            },
            "executor_evaluator": {
                "plan_steps_count": "${target.number_of_steps}",
                "result_string": "${target.steps}"
            },
            "groundedness_evaluator": {
                "response": "${target.answer}",
                "context": "${target.steps}"
            },
            "relevance_evaluator": {
                "question": "${data.question}",
                "response": "${target.answer}",
                "context": "${target.steps}"
            },
            "similarity_evaluator": {
                "question": "${data.question}",
                "answer": "${target.answer}",
                "ground_truth": "${data.answer}"
            }
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
