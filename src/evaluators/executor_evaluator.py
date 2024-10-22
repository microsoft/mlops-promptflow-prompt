"""Evaluator that validates the output of plan execution steps against an expected number of steps and step format."""
import re


class ExecutorEvaluator:
    """Evaluator example for the Executor node in the plan_and_execute flow."""

    def __init__(self):
        """Initialize the evaluator."""
        pass

    def __call__(self, plan_steps_count, result_string):
        """
        Validate whether the result string follows the expected format.

        :param plan_steps_count: The number of plan steps expected in the result.
        :param result_string: The multi-line result string to validate.
        :return: The list 'missing_steps' listing any missing step IDs.
        """
        step_pattern = re.compile(r"^#E(\d+) = .+", re.MULTILINE)
        found_steps = step_pattern.findall(result_string)

        # Convert found steps to a set of integers
        found_steps = set(map(int, found_steps))

        # Expected steps based on plan_steps_count
        expected_steps = set(range(1, int(plan_steps_count) + 1))

        # Determine missing steps
        missing_steps = expected_steps - found_steps

        return {"missing_steps": list(missing_steps)}
