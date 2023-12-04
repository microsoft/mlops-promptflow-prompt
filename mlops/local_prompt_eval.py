"""This is MLOps utility module to execute evaluation flow locally."""
import mlflow
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
        help="PROMPT_FLOW_CONFIG_NAME from model_config.json",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="ENV_NAME from model_config.json",
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

    config_file = open("./config/model_config.json")
    config_data = json.load(config_file)

    for el in config_data["flows"]:
        if "PROMPT_FLOW_CONFIG_NAME" in el and "ENV_NAME" in el:
            if (
                el["PROMPT_FLOW_CONFIG_NAME"] == args.config_name
                and el["ENV_NAME"] == args.environment_name
            ):
                experiment_type = el["EXPERIMENT_BASE_NAME"]
                flow_eval_path = el["EVALUATION_FLOW_PATH"]
                data_eval_path = el["EVAL_DATA_PATH"]
                resource_group = el["RESOURCE_GROUP_NAME"]
                workspace_name = el["WORKSPACE_NAME"]
                eval_column_mapping = el["EVAL_COLUMN_MAPPING"]

    # Setup MLFLOW Experiment
    load_dotenv()

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
