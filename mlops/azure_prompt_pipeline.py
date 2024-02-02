"""This is MLOps utility module to execute standard flow in Azure ML using automatic cluster."""
import argparse
import os
from shared.config_utils import MLOpsConfig
from shared.flow_utils import prepare_and_execute_std_flow


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given standard flow in Azure ML."""
    experiment_type = ""
    flow_standard_path = ""
    data_standard_path = ""
    column_mapping = ""
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
        "--output_file", type=str, required=False, help="A file to save run ids"
    )
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environemnt=args.environment_name)
    aml_config = mlops_config.aml_config
    flow_config = mlops_config.get_flow_config(flow_name=args.config_name)

    experiment_type = flow_config['experiment_base_name']
    flow_standard_path = flow_config['standard_flow_path']
    data_standard_path = flow_config['data_path']
    column_mapping = flow_config['column_mapping']
    subscription_id = aml_config['subscription_id']
    resource_group = aml_config['resource_group_name']
    workspace_name = aml_config['workspace_name']

    # override subscription id from args
    if args.subscription_id:
        subscription_id = args.subscription_id

    build_id = os.environ.get("BUILD_BUILDID")

    if build_id is None:
        build_id = "local"

    prepare_and_execute_std_flow(
        subscription_id,
        resource_group,
        workspace_name,
        # runtime_name,
        column_mapping,
        build_id,
        flow_standard_path,
        experiment_type,
        args.output_file,
        data_standard_path,
    )


if __name__ == "__main__":
    main()
