"""Configuration utils to load config from yaml/json."""
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import yaml


class MLOpsConfig():
    """MLopsConfig Class."""

    _raw_config: Any

    def __init__(self, environemnt: str = 'pr', config_path: Path = './config/config.yaml'):
        """Intialize MLConfig with yaml config data."""
        self.config_path = config_path
        self._environment = environemnt
        self._flow_name = None
        load_dotenv()
        with open(config_path, 'r', encoding='utf-8') as stream:
            self._raw_config = yaml.safe_load(os.path.expandvars(stream.read()))

    def __getattr__(self, __name: str) -> Any:
        """Get values for top level keys in configuration."""
        return self._raw_config[__name]

    def get_flow_config(self, flow_name: str) -> Dict:
        """Get the flow configuration for given flow name and environment."""
        flowconfig_name = f'{flow_name}_{self._environment}'
        if flowconfig_name in self.flow_configs:
            self._flow_name = flow_name
            return self.flow_configs[flowconfig_name]

    def get_deployment_config(self, flow_name: str, deployment_type: str) -> Dict:
        """Get the pipeline configuration for given pipeline name and environment."""
        deploymentconfig_name = f"{flow_name}_{deployment_type}_{self._environment}"
        if deploymentconfig_name in self.deployment_configs:
            return self.deployment_configs[deploymentconfig_name]


class DatasetsConfig():
    """Datasets Configuration Class."""
    _raw_config: Any

    def __init__(self, environemnt: str = 'pr', config_path: Path = './config/data_config.yaml'):
        """Intialize MLConfig with yaml config data."""
        self.config_path = config_path
        self._environment = environemnt
        load_dotenv()
        with open(config_path, 'r', encoding='utf-8') as stream:
            self._raw_config = yaml.safe_load(os.path.expandvars(stream.read()))

    def __getattr__(self, __name: str) -> Any:
        """Get values for top level keys in configuration."""
        return self._raw_config[__name]
    
    def get_dataset_config(self, name: str) -> Dict:
        """Get the dataset config for a given dataset name."""
        dataset_config = None
        datasets_config = self.datasets
        dataset_config = next((dataset for dataset in datasets_config if dataset['name'] == name), None)
        return dataset_config


if __name__ == "__main__":
    mlconfig = MLOpsConfig()
    print(mlconfig.aistudio_config)
    print(mlconfig.aoai_config)
    flow_config = mlconfig.get_flow_config(flow_name="yaml_basic_flow")
    print(flow_config)

    datasetconfig = DatasetsConfig()
    print(datasetconfig.datasets)
    print(datasetconfig.get_dataset_config("basic_flow"))
