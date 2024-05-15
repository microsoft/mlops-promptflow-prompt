"""The module contains a tool that evaluation flow is using as a logging step."""
from promptflow.core import tool
from typing import List
from promptflow import log_metric


@tool
def log_metrics(match_counts: List[dict]):
    """
    Log exact match and partial match numbers.

    Parameters:
      match_count (list<dict>): a list of matching details for each pair answer-ground truth

    Returns:
        Dictionary: returns exact_match_rate and partial_match_rate
    """
    exact_match_rate = sum([m["exact_match"] for m in match_counts]) / len(match_counts)
    partial_match_rate = sum([m["partial_match"] for m in match_counts]) / len(
        match_counts
    )

    log_metric(key="exact_match_rate", value=exact_match_rate)
    log_metric(key="partial_match_rate", value=partial_match_rate)
    print("exact_match_rate: ", exact_match_rate)
    print("partial_match_rate: ", partial_match_rate)

    return {
        "exact_match_rate": exact_match_rate,
        "partial_match_rate": partial_match_rate,
    }
