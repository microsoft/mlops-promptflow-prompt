from promptflow import tool, log_metric


@tool
def grade(groundtruth: str, prediction: str):
    return "Correct" if prediction.find(groundtruth)>=0 else "Incorrect"
