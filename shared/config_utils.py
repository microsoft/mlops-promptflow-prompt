"""Configuration utils to load config from yaml/json."""
import os
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv
import yaml


def load_yaml_config(config_path: Path) -> Dict:
    """Read configuration from yaml file."""
    load_dotenv()
    config = {}
    with open(config_path, 'r') as stream:
        try:
            # config = yaml.safe_load(os.path.expandvars(stream.read()))
            config = yaml.safe_load(stream.read())
        except yaml.YAMLError as err:
            print(err)
    return config


def get_aoai_config(raw_config: Dict) -> Dict:
    """Get the Azure OpenAI configuration from config map."""
    aoai_config = raw_config['aoai_config']

    # Load from environment variables if not specified in yaml file
    if aoai_config['aoai_api_base'] is None and "AOAI_BASE_ENDPOINT" in os.environ.keys():
        aoai_config['aoai_api_base'] = os.environ.get("AOAI_BASE_ENDPOINT")

    if aoai_config['aoai_api_key'] is None and "AOAI_API_KEY" in os.environ.keys():
        aoai_config['aoai_api_key'] = os.environ.get("AOAI_API_KEY")
    return aoai_config


def get_acs_config(raw_config: Dict) -> Dict:
    """Get the Azure Cognitive configuration from config map."""

    acs_config = raw_config['acs_config']

    # Load from environment variables if not specified in yaml file
    if acs_config['acs_api_base'] is None and "ACS_BASE_ENDPOINT" in os.environ.keys():
        acs_config['acs_api_base'] = os.environ.get("ACS_BASE_ENDPOINT")

    if acs_config['acs_api_key'] is None and "ACS_API_KEY" in os.environ.keys():
        acs_config['acs_api_key'] = os.environ.get("ACS_API_KEY")

    return acs_config


def get_aml_config(raw_config: Dict) -> Dict:
    """Get the Azure ML workspace configuration from config map."""

    aml_config = raw_config['aml_config']

    # Load from environment variables if not specified in yaml file
    if aml_config['subscription_id'] is None and "SUBSCRIPTION_ID" in os.environ.keys():
        aml_config['subscription_id'] = os.environ.get("SUBSCRIPTION_ID")
    if aml_config['resource_group_name'] is None and "RESOURCE_GROUP_NAME" in os.environ.keys():
        aml_config['resource_group_name'] = os.environ.get("RESOURCE_GROUP_NAME")
    if aml_config['workspace_name'] is None and "WORKSPACE_NAME" in os.environ.keys():
        aml_config['workspace_name'] = os.environ.get("WORKSPACE_NAME")

    return aml_config


def get_flow_config(env: str, flow_name: str, raw_config: Dict) -> Dict:
    """Get the flow configuration for given flow name and environment."""
    flow_config = {}
    config_name = f'{flow_name}_{env}'
    flow_configs = raw_config['flow_configs']
    if config_name in flow_configs:
        flow_config = flow_configs[config_name]

    return flow_config
