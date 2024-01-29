
import json
import os
from typing import IO, AnyStr, Dict, Optional, Union, List, Any
from os import PathLike
from pathlib import Path
from dotenv import load_dotenv
import yaml


def read_json_config(config_path: str, env: str) -> Dict:
    with open(config_path, 'r') as json_conf:
        conf = json.load(json_conf)
        return conf

def load_yaml_config(config_path: Path) -> Dict:
    load_dotenv()
    config = {}
    with open(config_path, 'r', encoding='utf-8') as stream:
        try:
            config = yaml.safe_load(os.path.expandvars(stream.read()))
        except yaml.YAMLError as err:
            print(err)   
    return config

def get_aoai_config(raw_config: Dict) -> Dict:
    return raw_config['aoai_config']

def get_acs_config(raw_config: Dict) -> Dict:
    return raw_config['acs_config']

def get_aml_config(raw_config: Dict) -> Dict:
    return raw_config['aml_config']

def get_flow_config(env: str, flow_name: str, raw_config: Dict) -> Dict:
    flow_config = {}
    config_name = f'{flow_name}_{env}'
    flow_configs = raw_config['flow_configs']
    if config_name in flow_configs:
        flow_config = flow_configs[config_name]

    return flow_config