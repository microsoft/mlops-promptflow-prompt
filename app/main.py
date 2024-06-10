"""The FastAPI application."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/home")
def get_home():
    """Return an intial message."""
    return {"message": "Welcome to the home page!"}


@app.get("/function_basic_flow")
def function_basic_flow():
    """Return a message from the function_basic_flow endpoint."""
    return {"message": "Function_basic_flow endpoint"}


@app.get("/class_basic_flow")
def class_basic_flow():
    """Return a message from the class_basic_flow endpoint."""
    return {"message": "Class_basic_flow endpoint"}


@app.get("/yaml_basic_flow")
def yaml_basic_flow():
    """Return a message from the yaml_basic_flow endpoint."""
    return {"message": "Yaml_basic_flow endpoint"}
