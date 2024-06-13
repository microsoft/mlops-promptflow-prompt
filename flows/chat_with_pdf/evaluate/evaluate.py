"""Evaluation flow for yaml_basic_flow."""
import argparse
from pprint import pprint
from promptflow.evals.evaluate import evaluate
from mlops.common.config_utils import MLOpsConfig
from promptflow.core import AzureOpenAIModelConfiguration
from promptflow.evals.evaluators import RelevanceEvaluator, CoherenceEvaluator
from src.evaluators.match_evaluator import MatchEvaluator
from flows.chat_with_pdf.evaluate.flow_wrapper import ChatWithPdfFlowWrapper
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
    flow_config = mlops_config.get_flow_config(flow_name="chat_with_pdf")

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=mlops_config.aoai_config["aoai_api_base"],
        api_key=mlops_config.aoai_config["aoai_api_key"],
        azure_deployment=flow_config["CHAT_MODEL_DEPLOYMENT_NAME"],
    )

    coherence_eval = CoherenceEvaluator(model_config=model_config)
    relevance_eval = RelevanceEvaluator(model_config=model_config)
    match_eval = MatchEvaluator()

    data_eval_path = flow_config["eval_data_path"]

    aistudio_config = mlops_config.aistudio_config
    openai_config = mlops_config.aoai_config

    flow = ChatWithPdfFlowWrapper(flow_config, openai_config)

    results = evaluate(
        evaluation_name=generate_experiment_name("chat_with_pdf"),
        data=data_eval_path,
        target=flow,
        evaluators={
            "match_eval": match_eval,
            "coherence_eval": coherence_eval,
            "relevance_eval": relevance_eval,
        },
        evaluator_config={
            "match_eval": {
                "response": "${target.answer}",
                "ground_truth": "${data.groundtruth}",
            },
            "coherence_eval": {
                "answer": "${target.answer}",
                "question": "${data.question}",
            },
            "relevance_eval": {
                "answer": "${target.answer}",
                "context": "${data.context}",
                "question": "${data.question}",
            },
        },
        azure_ai_project={
            "subscription_id": aistudio_config["subscription_id"],
            "resource_group_name": aistudio_config["resource_group_name"],
            "project_name": aistudio_config["project_name"],
        },
    )

    pprint(results)


if __name__ == "__main__":
    main()
