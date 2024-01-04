import subprocess
import sys

def run_integration_test(config_name, environment_name, subscription_id, output_file):
    try:
        # Define the MLOps pipeline command
        pipeline_command = [
            sys.executable,
            '-m',
            'mlops.local_prompt_pipeline',
            '--config_name', config_name,
            '--environment_name', environment_name,
            '--subscription_id', subscription_id,
            '--output_file', output_file
        ]

        # Run the MLOps pipeline
        subprocess.run(pipeline_command, check=True)

        # TODO: Add assertions

        print("Integration test passed!")

    except subprocess.CalledProcessError as e:
        print(f"Integration test failed with error: {e}")
        sys.exit(1)