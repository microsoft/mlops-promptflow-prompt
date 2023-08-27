from promptflow import PFClient

def main():
    pf_client = PFClient()

    # Test flow

    # Using default input
    # inputs = {"<flow_input_name>": "<flow_input_value>"}  # The inputs of the flow.

    flow_result = pf_client.test(flow="./flows/named_entity_recognition/flows/standard")
    print(f"Flow outputs: {flow_result}")

if __name__ == '__main__':
    main()