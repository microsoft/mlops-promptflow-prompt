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
from shared.config_utils import(load_yaml_config, get_flow_config)

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
        help="prompt_flow_config_name from config.yaml",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    args = parser.parse_args()

    config_data = load_yaml_config("./config/config.yaml")
    aml_config = config_data['aml_config']
    flow_config = get_flow_config(args.config_name, args.environment_name)

    experiment_type = flow_config['experiment_base_name']
    flow_standard_path = flow_config['stadard_flow_path']
    resource_group = flow_config['resource_group_name']
    workspace_name = flow_config['workspace_name']

    # Setup MLFLOW Experiment
    subscription_id = aml_config['susbcription_id']
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
