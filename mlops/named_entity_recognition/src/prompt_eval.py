import json
import time
import yaml
import datetime
import ast
import os
from promptflow.entities import Run
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from promptflow.azure import PFClient
import argparse
from promptflow.entities import AzureOpenAIConnection
import pandas as pd

def prepare_and_execute(subscription_id,
        resource_group_name,
        workspace_name,
        runtime,
        build_id,
        standard_flow_path,
        eval_flow_path,
        stage,
        experiment_name,
        model_name,
        output_file,
        data_config_path,
        run_id,
        data_purpose
    ):

    ml_client = MLClient(DefaultAzureCredential(),subscription_id,resource_group_name,workspace_name)

    pf = PFClient(ml_client)
    
    flow = eval_flow_path
    standard_flow = standard_flow_path
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
    standard_flow_file = f"{standard_flow}/flow.dag.yaml"

    with open(standard_flow_file, "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    default_variants = []
    for node_name, node_data in yaml_data.get("node_variants", {}).items():
        node_variant_mapping = {}
        default_variant = node_data['default_variant_id']
        node_variant_mapping[node_name] = default_variant
        default_variants.append(node_variant_mapping)

    dataframes = []
    metrics = []

    run_ids = ast.literal_eval(run_id)
    for flow_run in run_ids:
        my_run = pf.runs.get(flow_run)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pipeline_job = pf.run(
            flow=flow,
            data=data_id, 
            run=my_run, 
            column_mapping={
                "ground_truth": "${data.results}",
                "entities": "${run.outputs.entities}",
            },  
            runtime=runtime,
            name=f"{experiment_name}_eval_{timestamp}",
            display_name=f"{experiment_name}_eval_{timestamp}",
            tags={"build_id": build_id},
            stream=True

        )
        df_result = None
        
        if pipeline_job.status == "Completed" or pipeline_job.status == "Finished": # 4
            print(pipeline_job.status)
            df_result = pf.get_details(pipeline_job)
            metric_variant = pf.get_metrics(pipeline_job)

            dataframes.append(df_result)
            metrics.append(metric_variant)
          
            print(json.dumps(metrics, indent=4))
            print(df_result.head(10))
        else:
            raise Exception("Sorry, exiting job with failure..")

    combined_results_df = pd.concat(dataframes, ignore_index=True)
    combined_metrics_df = pd.DataFrame(metrics)
    
    combined_results_df.to_csv("./reports/combined_results_ds.csv")
    combined_metrics_df.to_csv("./reports/combined_metrics_ds.csv")
    
    styled_df = combined_results_df.style.apply(lambda x: ['width: {}ch'.format(max(len(str(val)) for val in x)), 'min-width: 150px'], axis=0)
    html_table = styled_df.render()
    with open('reports/formatted_dataframe_output.html', 'w') as f:
        f.write(html_table)
    
    html_table_metrics = combined_metrics_df.to_html(index=False)
    with open('reports/formatted_dataframe_metrics.html', 'w') as f:
        f.write(html_table_metrics)


def column_widths(column):
    max_length = max(column.astype(str).apply(len))
    return f'width: {max_length}em;'

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
        "--eval_flow_path", type=str, help="Job execution experiment name"
    )
    parser.add_argument(
        "--model_name", type=str, default="Name used for registration of model"
    )
    parser.add_argument("--data_purpose", type=str, help="data to be registered identified by purpose", required=True)

    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run ids"
    )
    parser.add_argument("--data_config_path", type=str, required=True, help="data config path")
    parser.add_argument("--run_id", type=str, required=True, help="run ids")
    args = parser.parse_args()

    prepare_and_execute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.runtime_name,
        args.build_id,
        args.standard_flow_path,
        args.eval_flow_path,
        args.stage,
        args.experiment_name,
        args.model_name,
        args.output_file,
        args.data_config_path,
        args.run_id,
        args.data_purpose
    )


if __name__ ==  '__main__':
      main()
