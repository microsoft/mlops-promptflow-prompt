import os
import json
from promptflow.client import load_flow
from mlops.common.config_utils import MLOpsConfig


class YamlBasicFlowEvaluator:
    def __init__(self):
        pass

    def __call__(self, *, response: str, ground_truth: str, execution_time: float, **kwargs):
        response =  self._flow(response=response, ground_truth=ground_truth)
        sql_similarity =  json.loads(response)
        compare = int(response==ground_truth)
        execution_time_seconds = execution_time
        
        return {"sql_similarity.score": sql_similarity.get("score"), "sql_similarity.explanation" : sql_similarity.get("explanation"), "compare": compare, "execution_time": execution_time_seconds}