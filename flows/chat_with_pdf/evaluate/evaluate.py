"""Evaluation flow for yaml_basic_flow."""
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from mlops.common.config_utils import MLOpsConfig
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.evals.evaluators import RelevanceEvaluator, CoherenceEvaluator
from src.evaluators.match_evaluator import MatchEvaluator
from flows.chat_with_pdf.evaluate.flow_wrapper import StandardFlowWrapper
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
    flow_config = mlops_config.get_flow_config(flow_name="yaml_chat_with_pdf")

    model_config = AzureOpenAIModelConfiguration(
                azure_endpoint=mlops_config.aoai_config['aoai_api_base'],
                api_key=mlops_config.aoai_config['aoai_api_key'],
                azure_deployment=mlops_config.aoai_config['aoai_deployment_name']
            )
    
    coherence_eval = CoherenceEvaluator(model_config=model_config)
    relevance_eval = RelevanceEvaluator(model_config=model_config)
    matchevaluator = MatchEvaluator()

    data_eval_path = flow_config['eval_data_path']
    print("data_eval_path:", data_eval_path)
    flow_standard_path = flow_config["standard_flow_path"]
    print("flow_standard_path:", flow_standard_path)
    aoai_deployment = flow_config["CHAT_MODEL_DEPLOYMENT_NAME"]
    print("aoai_deployment:", aoai_deployment)

    aistudio_config = mlops_config.aistudio_config
    openai_config = mlops_config.aoai_config

    flow = StandardFlowWrapper(flow_standard_path, flow_config["connection_name"], aoai_deployment, openai_config)

    results = evaluate(
        evaluation_name=generate_experiment_name("yaml_chat_with_pdf"),
        data=data_eval_path,
        target=flow,
        evaluators={
            "matchevaluator": matchevaluator,
            "coherence_eval": coherence_eval,
            "relevance_eval": relevance_eval
        },
        evaluator_config={
            "matchevaluator": {
                "response": "${target.answer}",
                "ground_truth": "${data.groundtruth}"
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
