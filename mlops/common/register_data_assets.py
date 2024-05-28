"""
This module is designed to register data assets in an AI Studio environment.

It utilizes the Azure AI MLClient from the Azure Machine Learning SDK to interact with Azure resources.

The script reads a configuration file to identify and register datasets in AI Studio.
It supports operations like creating or updating
data assets and retrieving the latest version of these assets.
"""
import argparse
import json
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from mlops.common.config_utils import MLOpsConfig


def main():
    """Register all datasets from the config file."""
    config = MLOpsConfig()

    ml_client = MLClient(
        DefaultAzureCredential(),
        config.aistudio_config["subscription_id"],
        config.aistudio_config["resource_group_name"],
        config.aistudio_config["project_name"],
    )

    parser = argparse.ArgumentParser("register data assets")

    parser.add_argument(
        "--data_config_path", type=str, help="data config file path", required=True
    )

    args = parser.parse_args()

    data_config_path = args.data_config_path

    config_file = open(data_config_path)
    data_config = json.load(config_file)

    for elem in data_config["datasets"]:
        data_path = elem["DATA_PATH"]
        dataset_desc = elem["DATASET_DESC"]
        dataset_name = elem["DATASET_NAME"]

        aml_dataset = Data(
            path=data_path,
            type=AssetTypes.URI_FILE,
            description=dataset_desc,
            name=dataset_name,
        )

        ml_client.data.create_or_update(aml_dataset)

        aml_dataset_unlabeled = ml_client.data.get(
            name=dataset_name, label="latest"
        )

        print(aml_dataset_unlabeled.id)


if __name__ == "__main__":
    main()
