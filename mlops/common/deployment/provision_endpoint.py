
import json
import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint
)
from azure.identity import DefaultAzureCredential


parser = argparse.ArgumentParser("provision_endpoints")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id", required=True)
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group", required=True)
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name", required=True)
parser.add_argument("--realtime_deployment_config", type=str, help="file path of realtime config")
#parser.add_argument("--run_id", type=str, help="AML run id for model generation", required=True)
parser.add_argument("--build_id", type=str, help="Azure DevOps build id for deployment", required=True)
parser.add_argument("--environment_name",type=str,help="environment name (e.g. dev, test, prod)", required=True)
args = parser.parse_args()




build_id = args.build_id


real_config = args.realtime_deployment_config
environment_name = args.environment_name

ml_client = MLClient(
    DefaultAzureCredential(), args.subscription_id, args.resource_group_name, args.workspace_name
)


config_file = open(real_config)
endpoint_config = json.load(config_file)
for elem in endpoint_config['real_time']:
    if 'ENDPOINT_NAME' in elem and 'ENV_NAME' in elem:
        if environment_name == elem['ENV_NAME']:
            endpoint_name = elem["ENDPOINT_NAME"]
            endpoint_desc = elem["ENDPOINT_DESC"]
            endpoint = ManagedOnlineEndpoint(
                name=endpoint_name,
                description=endpoint_desc,
                auth_mode="key",
                tags={"build_id": build_id},
            )

            ml_client.online_endpoints.begin_create_or_update(endpoint=endpoint).result()
