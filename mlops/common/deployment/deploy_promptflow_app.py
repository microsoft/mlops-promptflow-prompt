import argparse
from promptflow import PFClient
from promptflow.entities import AzureOpenAIConnection
from promptflow._sdk._errors import ConnectionNotFoundError

def main():
    """Build a flow for further sharing or deployment."""
    parser = argparse.ArgumentParser("config_parameters")
    parser.add_argument("--source", type=str, required=True, help="Path to the flow source")
    parser.add_argument("--output", type=str, required=True, help="Path for output artifacts")
    parser.add_argument("--format", type=str, required=True, help="Format to build flow into")
    parser.add_argument("--variant", type=str, default="", help="Node & variant name in format of ${node_name.variant_name}")
    parser.add_argument("--verbose", action="store_true", help="Show more details for each step during build")
    parser.add_argument("--debug", action="store_true", help="Show debug information during build")

    args = parser.parse_args()

    pf = PFClient()

    pf.flow.build(
        source=args.source,
        output=args.output,
        format=args.format,
        variant=args.variant,
        verbose=args.verbose,
        debug=args.debug
    )

if __name__ == "__main__":
    main()
