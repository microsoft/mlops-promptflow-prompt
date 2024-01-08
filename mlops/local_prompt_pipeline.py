"""This is MLOps utility module to execute standard flow locally."""
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
        help="PROMPT_FLOW_CONFIG_NAME from model_config.json",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="ENV_NAME from model_config.json",
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
                data_standard_path = el["DATA_PATH"]
                resource_group = el["RESOURCE_GROUP_NAME"]
                workspace_name = el["WORKSPACE_NAME"]
                column_mapping = el["COLUMN_MAPPING"]

    # Setup MLFLOW Experiment
    load_dotenv()

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
        print(f"PromptFlow run instance created: {run_instance}")
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
            print(f"Current Working Directory: {os.getcwd()}")
            abs_output_file_path = os.path.abspath(args.output_file)
            print(f"Output file specified: {abs_output_file_path}")
            with open(args.output_file, "w") as out_file:
                out_file.write(run_instance.name)

        print(run_instance.name)
        if args.visualize is True:
            pf.runs.visualize(run_instance)


if __name__ == "__main__":
    main()
