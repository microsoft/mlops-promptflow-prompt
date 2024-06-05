from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_home():
    return {"message": "helloworld"}

@app.get("/function_basic_flow")
def function_basic_flow():
    return {"message": "You've hit the function_basic_flow endpoint"}

@app.get("/class_basic_flow")
def class_basic_flow():
    return {"message": "You've hit the class_basic_flow endpoint"}

@app.get("/yaml_basic_flow")
def yaml_basic_flow():
    return {"message": "You've hit the yaml_basic_flow endpoint"}