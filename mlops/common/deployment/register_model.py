

import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential

parser = argparse.ArgumentParser("register model")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
parser.add_argument("--model_name", type=str, help="registered model name to be deployed", required=True)
parser.add_argument("--build_id", type=str, help="Azure DevOps build id for deployment", required=True)
parser.add_argument("--env_type", type=str, help="env name (dev, test, prod) for deployment", required=True)
parser.add_argument("--model_path", type=str, help="file path of model files")
parser.add_argument("--model_type", type=str, help="model type")
parser.add_argument("--output_file", type=str, required=False, help="A file to save run model version")

args = parser.parse_args()


model_name = args.model_name
model_path = args.model_path

stage = args.env_type
model_type = args.model_type
build_id = args.build_id

output_file = args.output_file

print(f"Model name: {model_name}")

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)

model = Model(
    name = model_name,
    path = model_path,
    stage = "Production",
    description = f"{model_type} model registered for prompt flow deployment",
    properties={
        "azureml.promptflow.source_flow_id": model_type
    },
    tags={"build_id": build_id}

)

model_info = ml_client.models.create_or_update(model)

if output_file is not None:
    with open(output_file, "w") as out_file:
        out_file.write(str(model_info.version))



