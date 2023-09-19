import json
import datetime
import ast
import argparse
import pandas as pd
from promptflow.entities import Run
from azure.identity import DefaultAzureCredential
from promptflow.azure import PFClient


def prepare_and_execute(subscription_id,
        resource_group_name,
        workspace_name,
        runtime,
        build_id,
        eval_flow_path,
        stage,
        experiment_name,
        data_config_path,
        run_id,
        data_purpose
    ):

    pf = PFClient(DefaultAzureCredential(),subscription_id,resource_group_name,workspace_name)
    
    flow = eval_flow_path
    dataset_name = None
    config_file = open(data_config_path)
    data_config = json.load(config_file)
    for elem in data_config['datasets']:
        if 'DATA_PURPOSE' in elem and 'ENV_NAME' in elem:
            if stage == elem['ENV_NAME'] and data_purpose == elem['DATA_PURPOSE']:
                dataset_name = elem["DATASET_NAME"]

    data = pf.ml_client.data.get(name=dataset_name,label='latest')

    data_id = f"azureml:{data.name}:{data.version}" # added
    print(data_id) # added

    dataframes = []
    metrics = []

    run_ids = ast.literal_eval(run_id)
    for flow_run in run_ids:
        my_run = pf.runs.get(flow_run)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run = Run( 
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
            tags={"build_id": build_id}

        )
        run._experiment_name=f"{experiment_name}_eval"

        pipeline_job = pf.runs.create_or_update(run, stream=True)

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
        args.eval_flow_path,
        args.stage,
        args.experiment_name,
        args.data_config_path,
        args.run_id,
        args.data_purpose
    )


if __name__ ==  '__main__':
      main()
