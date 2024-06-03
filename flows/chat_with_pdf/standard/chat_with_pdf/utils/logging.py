"""Log anything."""
import os


def log(message: str):
    """Log message."""
    verbose = os.environ.get("VERBOSE", "false")
    if verbose.lower() == "true":
        print(message, flush=True)
