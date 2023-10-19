import json
import datetime
import argparse
import pandas as pd
import os
from dotenv import load_dotenv
from promptflow.entities import Run
from azure.identity import DefaultAzureCredential
from promptflow.azure import PFClient
from mlops.common.mlflow_tools import generate_experiment_name, generate_run_name


def prepare_and_execute(
        subscription_id,
        resource_group_name,
        workspace_name,
        # runtime,
        build_id,
        eval_flow_path,
        experiment_name,
        data_config_path,
        run_id,
        eval_column_mapping
    ):

    pf = PFClient(DefaultAzureCredential(),subscription_id,resource_group_name,workspace_name)

    my_run = pf.runs.get(run_id)

    run = Run( 
        flow=eval_flow_path,
        data=data_config_path, 
        run=my_run, 
        column_mapping=eval_column_mapping,  
        # runtime=runtime,
        name=f"{generate_run_name()}_eval",
        display_name=f"{generate_run_name()}_eval",
        tags={"build_id": build_id}
    )
    run._experiment_name=f"{generate_experiment_name(experiment_name)}_eval"

    pipeline_job = pf.runs.create_or_update(run, stream=True)
        
    if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":
        print(pipeline_job.status)
    else:
        raise Exception("Sorry, exiting job with failure..")


def main():
    experiment_type = ""
    flow_eval_path = ""
    data_eval_path = ""
    eval_column_mapping = ""
    # runtime_name = ""
    subscription_id = None
    resource_group = None
    workspace_name = None

    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument("--config_name", type=str, required=True, help="PROMPT_FLOW_CONFIG_NAME from model_config.json")
    parser.add_argument("--environment_name", type=str, required=True, help="ENV_NAME from model_config.json")
    parser.add_argument("--subscription_id", type=str, required=True, help="Subscription id where Azure ML is located")
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
                # runtime_name = el["RUNTIME_NAME"]

    # Setup MLFLOW Experiment
    load_dotenv()

    subscription_id = args.subscription_id

    build_id = os.environ.get("BUILD_BUILDID")

    if build_id is None:
        build_id = "local"

    prepare_and_execute(
        subscription_id,
        resource_group,
        workspace_name,
        # runtime_name,
        build_id,
        flow_eval_path,
        experiment_type,
        data_eval_path,
        args.run_id,
        eval_column_mapping
    )


if __name__ ==  '__main__':
      main()
