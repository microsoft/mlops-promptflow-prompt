import os
from dotenv import load_dotenv
from promptflow import PFClient
from promptflow.entities import AzureOpenAIConnection

def main():
    load_dotenv()

    # PFClient can help manage your runs and connections.
    pf = PFClient()

    try:
        conn_name = os.environ.get("AOAI_CONNECTION_NAME")
        conn = pf.connections.get(name=conn_name)
        print("using existing connection")
    except:
        connection = AzureOpenAIConnection(
            name=conn_name,
            api_key=os.environ.get("AOAI_API_KEY"),
            api_base=os.environ.get("AOAI_API_BASE"),
            api_type=os.environ.get("AOAI_API_TYPE"),
            api_version=os.environ.get("AOAI_API_VERSION"),
        )

        conn = pf.connections.create_or_update(connection)
        print("successfully created connection")

if __name__ == '__main__':
    main()