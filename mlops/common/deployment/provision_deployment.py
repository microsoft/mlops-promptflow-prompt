
import json
import argparse

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineDeployment,
    Environment, BuildContext
)
from azure.identity import DefaultAzureCredential

def provision_deployment(
        subscription_id,
        resource_group_name,
        workspace_name,
        model_name,
        model_version,
        build_id,
        env_type,
        real_config
):

    print(f"Model name: {model_name}")

    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group_name, workspace_name
    )

    model = ml_client.models.get(model_name, model_version)

    config_file = open(real_config)
    endpoint_config = json.load(config_file)
    for elem in endpoint_config['real_time']:
        if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
            if env_type == elem['ENV_NAME']:
                endpoint_name = elem["ENDPOINT_NAME"]
                deployment_name = elem["DEPLOYMENT_NAME"]
                deployment_docker_file_path = elem["DEPLOYMENT_DOCKER_FILE_PATH"]
                deployment_vm_size = elem["DEPLOYMENT_VM_SIZE"]
                deployment_instance_count = elem["DEPLOYMENT_INSTANCE_COUNT"]
                deployment_desc = elem["DEPLOYMENT_DESC"]
                environment_variables = dict(elem["ENVIRONMENT_VARIABLES"])
                environment_variables["PRT_CONFIG_OVERRIDE"] = f"deployment.subscription_id={subscription_id},deployment.resource_group={resource_group_name},deployment.workspace_name={workspace_name},deployment.endpoint_name={endpoint_name},deployment.deployment_name={deployment_name}"

                environment = Environment(
                    build=BuildContext(path=deployment_docker_file_path, dockerfile_path="docker/Dockerfile"),
                    inference_config = {
                        "liveness_route": {
                            "path" : "/health",
                            "port": "8080"
                        },
                    "readiness_route": {
                            "path" : "/health",
                            "port": "8080"
                        },
                    "scoring_route": {
                            "path" : "/score",
                            "port": "8080"
                        },
                    }
                )

                blue_deployment = ManagedOnlineDeployment(
                    name=deployment_name,
                    endpoint_name=endpoint_name,
                    model=model,
                    description=deployment_desc,
                    environment=environment,
                    instance_type=deployment_vm_size,
                    instance_count=deployment_instance_count,
                    environment_variables = dict(environment_variables),
                    tags={"build_id": build_id}
                )

                ml_client.online_deployments.begin_create_or_update(blue_deployment).result()
            
            

def main():
    parser = argparse.ArgumentParser("provision_deployment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
    parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
    parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
    parser.add_argument("--model_name", type=str, help="registered model name to be deployed", required=True)
    parser.add_argument("--model_version", type=str, help="registered model version to be deployed", required=True)
    parser.add_argument("--build_id", type=str, help="Azure DevOps build id for deployment", required=True)
    parser.add_argument("--env_type", type=str, help="env name (dev, test, prod) for deployment", required=True)
    parser.add_argument("--realtime_deployment_config", type=str, help="file path of realtime config")

    args = parser.parse_args()

    provision_deployment(
         args.subscription_id,
         args.resource_group_name,
         args.workspace_name,
         args.model_name,
         args.model_version,
         args.build_id,
         args.env_type,
         args.realtime_deployment_config

    )

if __name__ ==  '__main__':
      main()