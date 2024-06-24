"""This module contains a few utility methods that allows us to generate names for \
    for experiments and runs."""
import subprocess
import os
import uuid


def generate_experiment_name(experiment_type: str):
    """
    Generate a unique experiment name based on the current branch name as well as an input parameter.

    Parameters:
     experiment_type (str): a prefix of the experiment name that usually contains the pipeline name \
        that helps to generate own experiment name for each pipeline in the repository.

    Returns:
        string: experiment name according to the pattern
    """
    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD", shell=True, universal_newlines=True
        ).strip()

    git_branch = git_branch.split("/")[-1]

    return f"{experiment_type}_{git_branch}"


def generate_run_name(experiment_type: str):
    """
    Generate a run name using build_id from the environment or autogenerated guid and run_ as a prefix.

    Returns:
        string: a unique run name
    """
    build = os.environ.get("BUILD_BUILDID")

    if build is None:
        build = f"local_{uuid.uuid4().hex}"

    return f"run_{experiment_type}_{build}"
