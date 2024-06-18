"""The script shows deployment process flows into AzureML Online endpoint."""
import argparse
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model, Environment, BuildContext
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from mlops.common.config_utils import MLOpsConfig


def main():
    """Implement deployment for a given flow using parameters from config.yaml."""
    # Config parameters
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument(
        "--environment_name",
        type=str,
        required=True,
        help="env_name from config.yaml",
    )
    parser.add_argument(
        "--flow_type",
        type=str,
        required=True,
        help="flow type to deploy",
    )
    args = parser.parse_args()

    mlops_config = MLOpsConfig(environment=args.environment_name)
    deployment_config = mlops_config.get_deployment_config(args.flow_type, "online")
    flow_config = mlops_config.get_flow_config(flow_name=args.flow_type)
    aistudio_config = mlops_config.aistudio_config

    credential = DefaultAzureCredential()

    client = MLClient(
        subscription_id=aistudio_config["subscription_id"],
        resource_group_name=aistudio_config["resource_group_name"],
        workspace_name=aistudio_config["project_name"],
        credential=credential,
    )

    try:
        endpoint = client.online_endpoints.get(deployment_config["endpoint_name"])

    except Exception:
        endpoint = ManagedOnlineEndpoint(
            name=deployment_config["endpoint_name"],
            description=deployment_config["endpoint_desc"],
            properties={
                "enforce_access_to_default_secret_stores": "enabled"  # secret injection support
            }
        )

    env_vars = {
        "PROMPTFLOW_RUN_MODE": "serving",
        "PROMPTFLOW_SERVING_ENGINE": "fastapi",
        "PRT_CONFIG_OVERRIDE": f"deployment.subscription_id={aistudio_config['subscription_id']},"
        f"deployment.resource_group={aistudio_config['resource_group_name']},"
        f"deployment.workspace_name={aistudio_config['project_name']},"
        f"deployment.endpoint_name={deployment_config['endpoint_name']},"
        f"deployment.deployment_name={deployment_config['deployment_name']}"
    }
    # additional flow specific variables
    env_vars.update(deployment_config["environment_variables"])

    deployment = ManagedOnlineDeployment(
        name=deployment_config["deployment_name"],
        description=deployment_config["deployment_desc"],
        endpoint_name=deployment_config["endpoint_name"],
        app_insights_enabled=True,
        model=Model(
            name=args.flow_type,
            path=flow_config["standard_flow_path"]  # path to promptflow folder
        ),
        environment=Environment(
            build=BuildContext(
                path=flow_config["standard_flow_path"],
            ),
            inference_config={
                "liveness_route": {
                    "path": "/health",
                    "port": 8080,
                },
                "readiness_route": {
                    "path": "/health",
                    "port": 8080,
                },
                "scoring_route": {
                    "path": "/score",
                    "port": 8080,
                },
            },
        ),

        instance_type=deployment_config["deployment_vm_size"],
        instance_count=deployment_config["deployment_instance_count"],
        environment_variables=env_vars
    )

    client.begin_create_or_update(endpoint).result()

    client.begin_create_or_update(deployment).result()

    endpoint.traffic = {deployment_config["deployment_name"]: deployment_config["deployment_traffic_allocation"]}
    client.begin_create_or_update(endpoint).result()


if __name__ == "__main__":
    main()
