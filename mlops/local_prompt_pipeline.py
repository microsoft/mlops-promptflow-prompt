"""This is MLOps utility module to execute standard flow locally."""
import argparse
import mlflow
from promptflow import PFClient
from mlops.common.mlflow_tools import (
    generate_experiment_name,
    generate_run_name,
    set_mlflow_uri,
)
from shared.config_utils import (load_yaml_config, get_flow_config)


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given standard flow locally."""
    experiment_type = ""
    flow_standard_path = ""
    data_standard_path = ""
    column_mapping = ""
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
    parser.add_argument(
        "--subscription_id",
        type=str,
        required=False,
        help="(optional) subscription id to find Azure ML workspace to store mlflow logs",
    )
    parser.add_argument("--visualize", default=False, action="store_true")
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run ids"
    )
    args = parser.parse_args()

    config_data = load_yaml_config("./config/config.yaml")
    aml_config = config_data['aml_config']
    flow_config = get_flow_config(env=args.environment_name, flow_name=args.config_name, raw_config=config_data)

    experiment_type = flow_config['experiment_base_name']
    flow_standard_path = flow_config['standard_flow_path']
    data_standard_path = flow_config['data_path']
    resource_group = flow_config['resource_group_name']
    workspace_name = flow_config['workspace_name']
    column_mapping = flow_config['column_mapping']
    subscription_id = aml_config['subscription_id']

    # Setup MLFLOW Experiment
    if args.subscription_id:
        subscription_id = args.subscription_id

    set_mlflow_uri(subscription_id, resource_group, workspace_name)

    experiment_name = generate_experiment_name(experiment_type)
    mlflow.set_experiment(experiment_name)

    # Start the experiment
    with mlflow.start_run(run_name=generate_run_name()):
        # Get a pf client to manage runs
        pf = PFClient()

        run_instance = pf.run(
            flow=flow_standard_path,
            data=data_standard_path,
            column_mapping=column_mapping,
        )

        pf.stream(run_instance)

        if run_instance.status == "Completed" or run_instance.status == "Finished":
            mlflow.log_table(
                data=pf.get_details(run_instance), artifact_file="details.json"
            )
            mlflow.log_metrics(pf.runs.get_metrics(run_instance))
        else:
            mlflow.set_tag("LOG_STATUS", "FAILED")
            raise Exception("Sorry, exiting job with failure..")

        if args.output_file is not None:
            with open(args.output_file, "w") as out_file:
                out_file.write(run_instance.name)

        print(run_instance.name)
        if args.visualize is True:
            pf.runs.visualize(run_instance)


if __name__ == "__main__":
    main()
