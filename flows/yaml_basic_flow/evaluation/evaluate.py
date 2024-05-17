"""Evaluation component for named_entity_recognition flow."""
import argparse
from azure.ai.generative.evaluate import evaluate
from azure.ai.resources.client import AIClient
from azure.identity import DefaultAzureCredential
from typing import List
from promptflow.client import PFClient
from mlops.common.config_utils import MLOpsConfig
from mlops.common.naming_tools import (
    generate_experiment_name,
)


def main():
    """Evaluate named_entity_recognition flow."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="pr, dev or any other supported environment",
    )
    parser.add_argument(
        "--run_id", type=str, required=True, help="Rund ID of a run to evaluate"
    )
    args = parser.parse_args()

    mlconfig = MLOpsConfig(environemnt=args.environment_name)
    aml_config = mlconfig.aml_config

    subscription_id = aml_config['subscription_id']
    resource_group = aml_config['resource_group_name']
    project_name = aml_config['project_name']

    # Create Azure AI Studio client
    ai_client = AIClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        project_name=project_name,
        credential=DefaultAzureCredential(),
    )

    pf = PFClient()

    base_run = pf.runs.get(args.run_id)

    flow_name = "named_entity_recognition"

    flow_config = mlconfig.get_flow_config(flow_name=flow_name)

    experiment_base_name = flow_config['experiment_base_name']
    data_eval_path = flow_config['eval_data_path']
    eval_column_mapping = flow_config['eval_column_mapping']

    experiment_name = f"{generate_experiment_name(experiment_base_name)}_eval"

    # Run evaluation
    result = evaluate(
        evaluation_name=experiment_name,
        target=base_run,
        data=data_eval_path,
        task_type="qa",
        data_mapping=eval_column_mapping,
        metrics_list=[match],
        tracking_uri=ai_client.tracking_uri,
    )

    print(f"Metric summary:\n{result.metrics_summary}")
    print(f"Studio url: {result.studio_url}")


def match(answer: List[str], ground_truth: List[str]):
    """
    Return a dictionary that contains information about matched/partially matched answers.

    Parameters:
      answer (list<str>): a list of answers from LLM
      ground_truth (list<str>): a list of expected answers - ground truth

    Returns:
        dictionary: the list of elements are exact_match, partial_match, answer and ground_truth
    """
    exact_match = 0
    partial_match = 0

    if is_match(
        answer, ground_truth, ignore_case=True, ignore_order=True, allow_partial=False
    ):
        exact_match = 1

    if is_match(
        answer, ground_truth, ignore_case=True, ignore_order=True, allow_partial=True
    ):
        partial_match = 1

    return {
        "exact_match": exact_match,
        "partial_match": partial_match,
        "answer": answer,
        "ground_truth": ground_truth,
    }


def is_match(
    answer: List[str],
    ground_truth: List[str],
    ignore_case: bool,
    ignore_order: bool,
    allow_partial: bool,
) -> bool:
    """
    Return boolean value that shows if an answer matches the expected answer.

    Parameters:
      answer (list<str>): a list of answers from LLM
      ground_truth (list<str>): a list of expected answers - ground truth
      ignore_case (bool): set to True if cases should be ignored
      ignore_order (bool): set to True if the order of elements should be ignored
      allow_partial (bool): set to True if partial answer should be counted

    Returns:
        Boolean: returns True if the answer matches the ground truth
    """
    if ignore_case:
        answer = [a.lower() for a in answer]
        ground_truth = [g.lower() for g in ground_truth]

    if ignore_order:
        answer.sort()
        ground_truth.sort()

    if allow_partial:
        x = [a for a in answer if a in ground_truth]
        return x == answer

    return answer == ground_truth


if __name__ == "__main__":
    main()
