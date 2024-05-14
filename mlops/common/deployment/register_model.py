"""This module implements Prompt flow folder registration as a model in Azure ML model repository."""
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential
from shared.config_utils import MLOpsConfig

def register_model(
    subscription_id,
    resource_group_name,
    workspace_name,
    model_name,
    build_id,
    model_path,
    model_type,
    output_file,
):
    """
    Register a flow folder as a model in Azure ML model repository.

    Parameters:
      subscription_id (string): a subsription id where Azure ML workspace is located
      resource_group (string): a resource group name where Azure ML workspace is located
      workspace_name (string): Azure ML workspace name
      model_name (string): a model name to register
      build_id (string): a build id to assign as a tag
      model_path (string): a path to the flow folder
      model_type (string): a type of the model to assign
      output_file (string): an optional output file to store the model version
    """
    print(f"Model name: {model_name}")

    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    model = Model(
        name=model_name,
        path=model_path,
        stage="Production",
        description=f"{model_type} model registered for prompt flow deployment",
        properties={"azureml.promptflow.source_flow_id": model_type},
        tags={"build_id": build_id},
    )

    model_info = ml_client.models.create_or_update(model)

    if output_file is not None:
        with open(output_file, "w") as out_file:
            out_file.write(str(model_info.version))


def main():
    """Collect command string parameters and pass them to the register_model method."""
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
        "--subscription_id",
        type=str,
        required=False,
        help="(optional) subscription id to find Azure ML workspace to store mlflow logs",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=False,
        help="A file to save run model version",
    )
    args = parser.parse_args()

    mlconfig = MLOpsConfig(environemnt=args.environment_name)
    aml_config = mlconfig.aml_config
    flow_config = mlconfig.get_flow_config(flow_name=args.config_name)

    subscription_id = aml_config['subscription_id']
    resource_group = aml_config['resource_group_name']
    workspace_name = aml_config['workspace_name']

    experiment_type = flow_config['experiment_base_name']
    model_base_name = flow_config['model_base_name']
    standard_flow_path = flow_config['standard_flow_path']

    # flow_eval_path = flow_config['evaluation_flow_path']
    # data_eval_path = flow_config['eval_data_path']
    # eval_column_mapping = flow_config['eval_column_mapping']

    args = parser.parse_args()

    register_model(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.model_base_name, #experiment_type
        args.build_id,
        args.standard_flow_path,
        args.experiment_type,
        args.output_file,
    )


if __name__ == "__main__":
    main()
