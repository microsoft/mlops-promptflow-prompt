"""This is MLOps utility module to execute evaluation flow locally using a single line of data."""
import mlflow
import os
import argparse
import json
from dotenv import load_dotenv
from promptflow import PFClient
from mlops.common.mlflow_tools import (
    generate_experiment_name,
    generate_run_name,
    set_mlflow_uri,
)


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given standard flow locally on a single line of data."""
    experiment_type = ""
    flow_standard_path = ""
    subscription_id = None
    resource_group = None
    workspace_name = None

    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--config_name",
        type=str,
        required=True,
        help="PROMPT_FLOW_CONFIG_NAME from model_config.json",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="ENV_NAME from model_config.json",
    )
    args = parser.parse_args()

    config_file = open("./config/model_config.json")
    config_data = json.load(config_file)

    for el in config_data["flows"]:
        if "PROMPT_FLOW_CONFIG_NAME" in el and "ENV_NAME" in el:
            if (
                el["PROMPT_FLOW_CONFIG_NAME"] == args.config_name
                and el["ENV_NAME"] == args.environment_name
            ):
                experiment_type = el["EXPERIMENT_BASE_NAME"]
                flow_standard_path = el["STANDARD_FLOW_PATH"]
                resource_group = el["RESOURCE_GROUP_NAME"]
                workspace_name = el["WORKSPACE_NAME"]

    # Setup MLFLOW Experiment
    load_dotenv()

    subscription_id = os.environ.get("SUBSCRIPTION_ID")

    set_mlflow_uri(subscription_id, resource_group, workspace_name)

    experiment_name = generate_experiment_name(experiment_type)
    mlflow.set_experiment(experiment_name)

    # Start the experiment
    with mlflow.start_run(run_name=generate_run_name()):
        pf_client = PFClient()

        # Using default input
        # inputs = {"<flow_input_name>": "<flow_input_value>"}  # The inputs of the flow.

        flow_result = pf_client.test(flow=flow_standard_path)
        print(f"Flow outputs: {flow_result}")
        mlflow.log_dict(flow_result, "output.json")


if __name__ == "__main__":
    main()
