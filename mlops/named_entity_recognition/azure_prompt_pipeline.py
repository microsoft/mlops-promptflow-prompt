import json
import time
import yaml
import datetime
from promptflow.entities import Run
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from promptflow.azure import PFClient
import argparse
from promptflow.entities import AzureOpenAIConnection


def are_dictionaries_similar(dict1, old_runs):
    for old_run in old_runs:
        set1 = {frozenset(dict(old_run).items()) }
        set2 = {frozenset(dict1.items()) }
        if set1 == set2:
            return True
    
    return False

def prepare_and_execute(
        subscription_id,
        resource_group_name,
        workspace_name,
        runtime,
        connection_name,
        deployment_name,
        build_id,
        standard_flow_path,
        stage,
        experiment_name,
        model_name,
        output_file,
        data_config_path,
        data_purpose
    ):

    ml_client = MLClient(DefaultAzureCredential(),subscription_id,resource_group_name,workspace_name)

    pf = PFClient(DefaultAzureCredential(),subscription_id,resource_group_name,workspace_name)

    flow = standard_flow_path
    dataset_name = None
    config_file = open(data_config_path)
    data_config = json.load(config_file)
    for elem in data_config['datasets']:
        if 'DATA_PURPOSE' in elem and 'ENV_NAME' in elem:
            if stage == elem['ENV_NAME'] and data_purpose == elem['DATA_PURPOSE']:
                dataset_name = elem["DATASET_NAME"]

    data = ml_client.data.get(name=dataset_name,label='latest')

    data_id = f"azureml:{data.name}:{data.version}" # added
    print(data_id) # added

    run_ids = []

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run = Run( 
        flow=flow,
        data=data_id,
        runtime=runtime,
        name=f"{experiment_name}_{timestamp}",
        display_name=f"{experiment_name}_{timestamp}",
        environment_variables={
            "key1": "value1"
        },
        column_mapping={"text": "${data.text}", "entity_type": "${data.entity_type}"},
        tags={"build_id": build_id},
    )

    pipeline_job = pf.runs.create_or_update(run, stream=True)
    run_ids.append(pipeline_job.name)

    df_result = None
        
    if pipeline_job.status == "Completed" or pipeline_job.status == "Finished": # 4
        print("job completed")
        df_result = pf.get_details(pipeline_job)
        run_details = pf.runs.get_metrics(pipeline_job.name)
        print(df_result.head(10))
        print("done")
    else:
        raise Exception("Sorry, exiting job with failure..")

    if output_file is not None:
        with open(output_file, "w") as out_file:
            out_file.write(str(run_ids))
    print(str(run_ids))

def main():
    parser = argparse.ArgumentParser("prompt_exprimentation")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--runtime_name", type=str, help="prompt flow runtime time"
    )
    parser.add_argument(
        "--connection_name", type=str, help="connection name to LLM"
    )
    parser.add_argument(
        "--deployment_name", type=str, help="LLM Model deployment name"
    )
    parser.add_argument(
        "--build_id",
        type=str,
        help="Unique identifier for Azure DevOps pipeline run",
    )
    parser.add_argument(
        "--stage",
        type=str,
        help="execution and deployment environment. e.g. dev, prod, test",
    )
    parser.add_argument(
        "--experiment_name", type=str, help="Job execution experiment name"
    )
    parser.add_argument(
        "--standard_flow_path", type=str, help="Job execution experiment name"
    )
    parser.add_argument(
        "--model_name", type=str, default="Name used for registration of model"
    )
    parser.add_argument(
        "--data_purpose", type=str, help="data to be registered identified by purpose"
    )

    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run ids"
    )
    parser.add_argument("--data_config_path", type=str, required=True, help="data config path")

    args = parser.parse_args()

    prepare_and_execute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.runtime_name,
        args.connection_name,
        args.deployment_name,
        args.build_id,
        args.standard_flow_path,
        args.stage,
        args.experiment_name,
        args.model_name,
        args.output_file,
        args.data_config_path,
        args.data_purpose
    )


if __name__ ==  '__main__':
      main()
