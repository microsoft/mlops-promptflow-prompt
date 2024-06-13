FROM mcr.microsoft.com/azureml/promptflow/promptflow-runtime:latest

# Initialize arguments
ARG USERNAME=vscode

# Setup user for sudo
USER root

# Update apt-get, install sudo and create a non-root user
RUN apt-get update -y && apt-get install -y sudo \
    && useradd -m -s /bin/bash $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown -R $USERNAME:$USERNAME /opt/miniconda

#Use the non-root user
USER $USERNAME

# Install dependencies
WORKDIR /home/$USERNAME

COPY ./requirements.txt .

RUN pip install -r requirements.txt

# Copy FastAPI application
COPY /src/basic_flow_fastapi_app/main.py /home/$USERNAME/app/main.py

COPY /flows/function_basic_flow/standard /home/$USERNAME/app/function_basic_flow
COPY /flows/class_basic_flow/standard /home/$USERNAME/app/class_basic_flow
COPY /flows/yaml_basic_flow/standard /home/$USERNAME/app/yaml_basic_flow

WORKDIR /home/$USERNAME/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]