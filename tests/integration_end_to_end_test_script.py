import argparse 

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

if __name__ == "__main__":
    main()
