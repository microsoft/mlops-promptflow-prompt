import subprocess
import os
import uuid

def generate_experiment_name(experiment_type: str):

    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD",
            shell=True,
            universal_newlines=True).strip()
        
    return f"{experiment_type}_{git_branch}"

def generate_run_name():
    build = os.environ.get("BUILD_BUILDID")

    if build is None:
        build = f"local_{uuid.uuid4().hex}"

    return f"run_{build}"
