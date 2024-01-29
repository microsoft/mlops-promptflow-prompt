"""This is MLOps utility module to execute evaluation flow in Azure ML using automatic cluster."""
import json
import argparse
import os
from dotenv import load_dotenv
from promptflow.entities import Run
from azure.identity import DefaultAzureCredential
from promptflow.azure import PFClient
from mlops.common.mlflow_tools import generate_experiment_name, generate_run_name
from shared.config_utils import(load_yaml_config, get_flow_config)
from shared.flow_utils import prepare_and_execute_eval_flow

def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given evaluation flow in Azure ML."""
    experiment_type = ""
    flow_eval_path = ""
    data_eval_path = ""
    eval_column_mapping = ""
    # runtime_name = ""
    subscription_id = None
    resource_group = None
    workspace_name = None

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
    parser.add_argument(
        "--subscription_id",
        type=str,
        required=True,
        help="Subscription id where Azure ML is located",
    )
    parser.add_argument(
        "--run_id", type=str, required=True, help="Rund ID of a run to evaluate"
    )
    args = parser.parse_args()

    config_data = load_yaml_config("./config/config.yaml")
    aml_config = config_data['aml_config']
    flow_config = get_flow_config(args.config_name, args.environment_name)

    experiment_type = flow_config['experiment_base_name']
    flow_eval_path = flow_config['evaluation_flow_path']
    data_eval_path = flow_config['eval_data_path']
    resource_group = flow_config['resource_group_name']
    workspace_name = flow_config['workspace_name']
    eval_column_mapping = flow_config['eval_column_mapping']
    subscription_id = aml_config['subscription_id']

    # Setup MLFLOW Experiment
    if args.subscription_id:
        subscription_id = args.subscription_id

    build_id = os.environ.get("BUILD_BUILDID")

    if build_id is None:
        build_id = "local"

    prepare_and_execute_eval_flow(
        subscription_id,
        resource_group,
        workspace_name,
        # runtime_name,
        build_id,
        flow_eval_path,
        experiment_type,
        data_eval_path,
        args.run_id,
        eval_column_mapping,
    )


if __name__ == "__main__":
    main()
