"""This module contains a few utility methods that allows us to initialize MLFlow and generate names for \
    for experiments and runs."""
import subprocess
import os
import uuid
import mlflow
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential


def generate_experiment_name(experiment_type: str):
    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD", shell=True, universal_newlines=True
        ).strip()

    git_branch = git_branch.split("/")[-1]
    return f"{experiment_type}_{git_branch}"


def generate_run_name():
    build = os.environ.get("BUILD_BUILDID")

    if build is None:
        build = f"local_{uuid.uuid4().hex}"

    return f"run_{build}"


def set_mlflow_uri(subscription_id: str, resource_group: str, workspace_name: str):
    # If Azure ML parameters are not provided, use a local instance
    if (
        (subscription_id is not None)
        and (resource_group is not None)
        and (workspace_name is not None)
    ):
        ml_client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
        )

        mlflow_tracking_uri = ml_client.workspaces.get(
            ml_client.workspace_name
        ).mlflow_tracking_uri
        print(mlflow_tracking_uri)

        mlflow.set_tracking_uri(mlflow_tracking_uri)
