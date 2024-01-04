import subprocess
import sys

# def run_integration_test(config_name, environment_name, subscription_id, output_file):
#     try:
#         # Define the MLOps pipeline command
#         pipeline_command = [
#             sys.executable,
#             '-m',
#             'mlops.local_prompt_pipeline',
#             '--config_name', config_name,
#             '--environment_name', environment_name,
#             '--subscription_id', subscription_id,
#             '--output_file', output_file
#         ]

#         # Run the MLOps pipeline
#         subprocess.run(pipeline_command, check=True)

#         # TODO: Add assertions

#         print("Integration test passed!")

#     except subprocess.CalledProcessError as e:
#         print(f"Integration test failed with error: {e}")
#         sys.exit(1)
def main():
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument("--config_name", type=str, required=True, help="PROMPT_FLOW_CONFIG_NAME from model_config.json")
    parser.add_argument("--environment_name", type=str, required=True, help="ENV_NAME from model_config.json")
    parser.add_argument("--run_id", type=str, required=True, help="Run ID of a run to evaluate")
    parser.add_argument("--subscription_id", type=str, required=False, help="(optional) subscription id to find Azure ML workspace to store mlflow logs")
    args = parser.parse_args()
    
    print(f"Config Name: {args.config_name}")
    print(f"Environment Name: {args.environment_name}")
    print(f"Run ID: {args.run_id}")
    print(f"Subscription ID: {args.subscription_id}")
    
    # evaluate_run(
    #     config_name=args.config_name,
    #     environment_name=args.environment_name,
    #     run_id=args.run_id,
    #     subscription_id=args.subscription_id
    # )

if __name__ == "__main__":
    main()
