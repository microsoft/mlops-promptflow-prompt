"""This is MLOps utility module to execute evaluation flow locally."""
import argparse
import mlflow
from promptflow import PFClient
from mlops.common.mlflow_tools import (
    generate_experiment_name,
    generate_run_name,
    set_mlflow_uri,
)
from shared.config_utils import (load_yaml_config, get_aml_config, get_flow_config)


def main():
    """Collect command line arguments and configuration file parameters to invoke \
        a given evaluation flow locally."""
    experiment_type = ""
    flow_eval_path = ""
    data_eval_path = ""
    eval_column_mapping = ""
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
        "--run_id", type=str, required=True, help="Rund ID of a run to evaluate"
    )
    parser.add_argument(
        "--subscription_id",
        type=str,
        required=False,
        help="(optional) subscription id to find Azure ML workspace to store mlflow logs",
    )
    args = parser.parse_args()

    config_data = load_yaml_config("./config/config.yaml")
    aml_config = get_aml_config(config_data)
    flow_config = get_flow_config(env=args.environment_name, flow_name=args.config_name, raw_config=config_data)

    experiment_type = flow_config['experiment_base_name']
    flow_eval_path = flow_config['evaluation_flow_path']
    data_eval_path = flow_config['eval_data_path']
    eval_column_mapping = flow_config['eval_column_mapping']
    subscription_id = aml_config['subscription_id']
    resource_group = aml_config['resource_group_name']
    workspace_name = aml_config['workspace_name']

    # Setup MLFLOW Experiment
    if args.subscription_id:
        subscription_id = args.subscription_id

    set_mlflow_uri(subscription_id, resource_group, workspace_name)

    experiment_name = f"{generate_experiment_name(experiment_type)}_eval"
    mlflow.set_experiment(experiment_name)

    # Start the experiment
    with mlflow.start_run(run_name=generate_run_name()):
        # Get a pf client to manage runs
        pf = PFClient()

        base_run = pf.runs.get(args.run_id)

        # run the flow with exisiting run
        run_instance = pf.run(
            flow=flow_eval_path,
            data=data_eval_path,
            run=base_run,
            column_mapping=eval_column_mapping,  # map the url field from the data to the url input of the flow
        )

        # stream the run until it's finished
        pf.stream(run_instance)

        if run_instance.status == "Completed" or run_instance.status == "Finished":
            mlflow.log_table(
                data=pf.get_details(run_instance), artifact_file="details.json"
            )
            mlflow.log_metrics(pf.runs.get_metrics(run_instance))
        else:
            mlflow.set_tag("LOG_STATUS", "FAILED")
            raise Exception("Sorry, exiting job with failure..")


if __name__ == "__main__":
    main()
