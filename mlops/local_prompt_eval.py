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
    flow_eval_path = ""
    data_eval_path = ""
    eval_column_mapping = ""
    subscription_id = None
    resource_group = None
    workspace_name = None

    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument("--config_name", type=str, required=True, help="PROMPT_FLOW_CONFIG_NAME from model_config.json")
    parser.add_argument("--environment_name", type=str, required=True, help="ENV_NAME from model_config.json")
    parser.add_argument("--run_id", type=str, required=True, help="Rund ID of a run to evaluate")
    args = parser.parse_args()

    config_file = open("./config/model_config.json")
    config_data = json.load(config_file)

    for el in config_data["flows"]:
        if "PROMPT_FLOW_CONFIG_NAME" in el and "ENV_NAME" in el:
            if el["PROMPT_FLOW_CONFIG_NAME"]==args.config_name and el["ENV_NAME"]==args.environment_name:
                experiment_type = el["EXPERIMENT_BASE_NAME"]
                flow_eval_path = el["EVALUATION_FLOW_PATH"]
                data_eval_path = el["EVAL_DATA_PATH"]
                resource_group = el["RESOURCE_GROUP_NAME"]
                workspace_name = el["WORKSPACE_NAME"]
                eval_column_mapping = el["EVAL_COLUMN_MAPPING"]

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

    experiment_name = f"{generate_experiment_name(experiment_type)}_eval"
    mlflow.set_experiment(experiment_name)
    
    # Start the experiment
    with mlflow.start_run(run_name=generate_run_name()) as run:

        # Get a pf client to manage runs
        pf = PFClient()

        base_run = pf.runs.get(args.run_id)

        # run the flow with exisiting run
        run_instance = pf.run(
            flow=flow_eval_path,
            data=data_eval_path,
            run=base_run,
            column_mapping=eval_column_mapping  # map the url field from the data to the url input of the flow
        )

        # stream the run until it's finished
        pf.stream(run_instance)

        if run_instance.status == "Completed" or run_instance.status == "Finished":
            mlflow.log_table(data=pf.get_details(run_instance), artifact_file="details.json")
            mlflow.log_metrics(pf.runs.get_metrics(run_instance))
        else:
            mlflow.set_tag("LOG_STATUS", "FAILED")
            raise Exception("Sorry, exiting job with failure..")

if __name__ == '__main__':
    main()