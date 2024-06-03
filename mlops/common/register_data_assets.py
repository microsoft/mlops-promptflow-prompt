"""
This module is designed to register data assets in an AI Studio environment.

It utilizes the Azure AI MLClient from the Azure Machine Learning SDK to interact with Azure resources.

The script reads a configuration file to identify and register datasets in AI Studio.
It supports operations like creating or updating
data assets and retrieving the latest version of these assets.
"""
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from mlops.common.config_utils import MLOpsConfig, DatasetsConfig
from typing import Dict
import logging


def register_data_asset(ml_client: MLClient, config: Dict) -> Data:
    """Create or update data asset in AML workspace for a given dataset configuration."""
    aml_dataset = Data(
        path=config['data_path'],
        type=AssetTypes.URI_FILE,
        description=config['dataset_desc'],
        name=config['dataset_name'],
    )
    return ml_client.data.create_or_update(aml_dataset)


def check_data_asset_registered(ml_client: MLClient, dataset_name: str) -> bool:
    """Check if a specified datset is registered."""
    try:
        data_items = ml_client.data.list(name=dataset_name)
        data_items_count = sum(1 for _ in data_items)
        if data_items_count:
            return True
    except Exception as e:
        logging.debug(f"data asset not found: {e}")
    return False


def main():
    """Register all datasets from the config file."""
    config = MLOpsConfig()
    datasets_config = DatasetsConfig().datasets

    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aistudio_config["subscription_id"],
        config.aistudio_config["resource_group_name"],
        config.aistudio_config["project_name"],
    )
    
    for dataset_config in datasets_config:
        dataset_name = dataset_config['dataset_name']
        print(f'Registering {dataset_name}')
        register_data_asset(ml_client=ml_client, config=dataset_config)
        aml_dataset_unlabeled = ml_client.data.get(
            name=dataset_name, label="latest"
        )
        print(aml_dataset_unlabeled)
        print(check_data_asset_registered(ml_client=ml_client, dataset_name=dataset_name))


if __name__ == "__main__":
    main()
