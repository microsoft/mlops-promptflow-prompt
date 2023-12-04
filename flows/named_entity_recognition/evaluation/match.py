"""The tool implements a step that allows to compare ground truth to an answer."""
from promptflow import tool
from typing import List


@tool
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
