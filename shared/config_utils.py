"""Configuration utils to load config from yaml/json."""
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import yaml


class MLopsConfig():
    """MLopsConfig"""
    _configuration_data: Any
    _aml_config: Any
    _aoai_config: Any
    _acs_config: Any
    _flow_configs: Any
    _deployment_config: Any

    def __init__(self, **data: Any):
        self._raw_config = data
        if "aml_config" in data:
            self._aml_config = data['aml_config']
        if "acs_config" in data:
            self._acs_config = data['acs_config']
        if "aoai_config" in data:
            self._aoai_config = data['aoai_config']
        if "flow_configs" in data:
            self._flow_configs = data['flow_configs']
        if "deployment_configs" in data:
            self._deployment_config = data['deployment_configs']

    @property
    def configuration_data(self):
        """configuration data dictionary"""
        return self._configuration_data

    @property
    def aml_config(self):
        """Azure ML workspace configuration data"""
        # Load from environment variables if not specified in yaml file
        if self._aml_config['subscription_id'] is None and "SUBSCRIPTION_ID" in os.environ.keys():
            self._aml_config['subscription_id'] = os.environ.get("SUBSCRIPTION_ID")
        if self._aml_config['resource_group_name'] is None and "RESOURCE_GROUP_NAME" in os.environ.keys():
            self._aml_config['resource_group_name'] = os.environ.get("RESOURCE_GROUP_NAME")
        if self._aml_config['workspace_name'] is None and "WORKSPACE_NAME" in os.environ.keys():
            self._aml_config['workspace_name'] = os.environ.get("WORKSPACE_NAME")
        return self._aml_config

    @property
    def aoai_config(self):
        """Azure OpenAI configuration data"""
        # Load from environment variables if not specified in yaml file
        if self._aoai_config['aoai_api_base'] is None and "AOAI_BASE_ENDPOINT" in os.environ.keys():
            self._aoai_config['aoai_api_base'] = os.environ.get("AOAI_BASE_ENDPOINT")

        if self._aoai_config['aoai_api_key'] is None and "AOAI_API_KEY" in os.environ.keys():
            self._aoai_config['aoai_api_key'] = os.environ.get("AOAI_API_KEY")
        return self._aoai_config

    @property
    def acs_config(self):
        """Azure Cognititive Services configuration data"""
        # Load from environment variables if not specified in yaml file
        if self._aoai_config['aoai_api_base'] is None and "AOAI_BASE_ENDPOINT" in os.environ.keys():
            self._aoai_config['aoai_api_base'] = os.environ.get("AOAI_BASE_ENDPOINT")

        if self._aoai_config['aoai_api_key'] is None and "AOAI_API_KEY" in os.environ.keys():
            self._aoai_config['aoai_api_key'] = os.environ.get("AOAI_API_KEY")
        return self._acs_config

    @property
    def flow_configs(self):
        """Flow Configurations data"""
        return self._flow_configs

    @property
    def deployment_config(self):
        """Deployment configuraton"""
        return self._deployment_config

    def get_flow_config(self, env: str, flow_name: str) -> Dict:
        """Get the flow configuration for given flow name and environment."""
        flowconfig_name = f'{flow_name}_{env}'
        if flowconfig_name in self._flow_configs:
            return self._flow_configs[flowconfig_name]


def load_yaml_config(config_path: Path = './config/config.yaml') -> MLopsConfig:
    """Read configuration from yaml file."""
    load_dotenv()
    config = {}
    with open(config_path, 'r') as stream:
        try:
            # config = yaml.safe_load(os.path.expandvars(stream.read()))
            config = yaml.safe_load(stream.read())
            mlops_config = MLopsConfig(**config)
            return mlops_config
        except yaml.YAMLError as err:
            print(err)


if __name__ == "__main__":
    mlconfig = load_yaml_config()
    print(mlconfig.aml_config)
    print(mlconfig.get_flow_config("pr", "named_entity_recognition"))
