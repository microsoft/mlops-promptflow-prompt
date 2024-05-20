"""Evaluator that matching a response dictionary to ground truth one using a basic comparison."""
from typing import List


class MatchEvaluator:
    """Basic evaluator example."""

    def __init__(self):
        """Initialize the object of the class."""
        pass

    def __call__(self, *, response: str, ground_truth: str, **kwargs):
        """Calculate te metric using a single response and associated ground truth."""
        exact_match = 0
        partial_match = 0

        parts = ground_truth.split(",")
        cleaned_parts = [part.strip(' \t."') for part in parts]
        entities = [part for part in cleaned_parts if len(part) > 0]

        if self.is_match(
            response, entities, ignore_case=True, ignore_order=True, allow_partial=False
        ):
            exact_match = 1

        if self.is_match(
            response, entities, ignore_case=True, ignore_order=True, allow_partial=True
        ):
            partial_match = 1

        return {
            "exact_match": exact_match,
            "partial_match": partial_match
        }

    def is_match(
        self,
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
