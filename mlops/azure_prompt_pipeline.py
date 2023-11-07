import json
import argparse
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
    column_mapping,
    build_id,
    standard_flow_path,
    experiment_name,
    output_file,
    standard_data_path,
):
    pf = PFClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    run = Run(
        flow=standard_flow_path,
        data=standard_data_path,
        # runtime=runtime,
        name=generate_run_name(),
        display_name=generate_run_name(),
        column_mapping=column_mapping,
        tags={"build_id": build_id},
    )

    run._experiment_name = generate_experiment_name(experiment_name)

    pipeline_job = pf.runs.create_or_update(run, stream=True)

    df_result = None

    if pipeline_job.status == "Completed" or pipeline_job.status == "Finished":  # 4
        print("job completed")
    else:
        raise Exception("Sorry, exiting job with failure..")

    if output_file is not None:
        with open(output_file, "w") as out_file:
            out_file.write(pipeline_job.name)
    print(pipeline_job.name)


def main():
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
        required=True,
        help="Subscription id where Azure ML is located",
    )
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
                # runtime_name = el["RUNTIME_NAME"]

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
        column_mapping,
        build_id,
        flow_standard_path,
        experiment_type,
        args.output_file,
        data_standard_path,
    )


if __name__ == "__main__":
    main()
