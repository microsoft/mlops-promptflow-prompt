import mlflow
import os
import argparse
import json
from dotenv import load_dotenv
from promptflow import PFClient
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from mlops.common.generate_mlflow_names import generate_experiment_name, generate_run_name

def main():

    experiment_type = ""
    flow_standard_path=""
    data_standard_path=""
    subscription_id = None
    resource_group = None
    workspace_name = None

    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument("--config_name", type=str, required=True, help="PROMPT_FLOW_CONFIG_NAME from model_config.json")
    parser.add_argument("--environment_name", type=str, required=True, help="ENV_NAME from model_config.json")
    parser.add_argument('--visualize', default=False, action='store_true')
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run ids"
    )
    args = parser.parse_args()

    config_file = open("./config/model_config.json")
    config_data = json.load(config_file)

    for el in config_data["flows"]:
        if "PROMPT_FLOW_CONFIG_NAME" in el and "ENV_NAME" in el:
            if el["PROMPT_FLOW_CONFIG_NAME"]==args.config_name and el["ENV_NAME"]==args.environment_name:
                experiment_type = el["EXPERIMENT_BASE_NAME"]
                flow_standard_path = el["STANDARD_FLOW_PATH"]
                data_standard_path = el["DATA_PATH"]
                resource_group = el["RESOURCE_GROUP_NAME"]
                workspace_name = el["WORKSPACE_NAME"]

    # Setup MLFLOW Experiment
    load_dotenv()

    subscription_id = os.environ.get("SUBSCRIPTION_ID")

    # If Azure ML parameters are not provided, use a local instance
    if (subscription_id is not None) and (resource_group is not None) and (workspace_name is not None):
        ml_client = MLClient(credential=DefaultAzureCredential(),
                             subscription_id=subscription_id, 
                             resource_group_name=resource_group,
                             workspace_name=workspace_name)

        mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
        print(mlflow_tracking_uri)

        mlflow.set_tracking_uri(mlflow_tracking_uri)

    experiment_name = generate_experiment_name(experiment_type)
    mlflow.set_experiment(experiment_name)

    load_dotenv()

    # Start the experiment
    with mlflow.start_run(run_name=generate_run_name()) as run:

        run_ids = []

        # Get a pf client to manage runs
        pf = PFClient()

        run_instance = pf.run( 
            flow=flow_standard_path,
            data=data_standard_path
        )

        pf.stream(run_instance)

        run_ids.append(run_instance.name)

        df_result = None
        
        if run_instance.status == "Completed" or run_instance.status == "Finished":
            mlflow.log_table(data=pf.get_details(run_instance), artifact_file="details.json")
            mlflow.log_metrics(pf.runs.get_metrics(run_instance))
        else:
            mlflow.set_tag("LOG_STATUS", "FAILED")
            raise Exception("Sorry, exiting job with failure..")

        if args.output_file is not None:
            with open(args.output_file, "w") as out_file:
                out_file.write(str(run_ids))

        print(str(run_ids))
        if args.visualize is True:
            pf.runs.visualize(run_instance)


if __name__ == '__main__':
    main()