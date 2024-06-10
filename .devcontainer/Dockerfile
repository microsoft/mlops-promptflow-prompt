FROM mcr.microsoft.com/azureml/promptflow/promptflow-runtime:latest

# Initialize arguments
ARG USERNAME=vscode

ENV CONDA_ENVIRONMENT_PATH=/opt/miniconda/envs/promptflow-env
ENV CONDA_DEFAULT_ENVIRONMENT=$CONDA_ENVIRONMENT_PATH
ENV PATH $CONDA_DEFAULT_ENVIRONMENT/bin:$PATH

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

# Install Azure CLI
RUN sudo apt-get update \
    && sudo apt-get install -y gnupg software-properties-common \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash \
    && az config set extension.use_dynamic_install=yes_without_prompt \
    && az extension add -n ml

COPY ./requirements.txt .

RUN conda init bash \
    && conda create -n promptflow-env python=3.9.16 pip=23.0.1 -q -y \
    && conda run -n promptflow-env \
    && pip install -r requirements.txt \
    && conda clean -a -y

RUN echo "conda activate promptflow-env" >> /home/$USERNAME/.bashrc

# Copy FastAPI application
COPY ./app /home/$USERNAME/app

COPY ./flows/function_basic_flow/standard /home/$USERNAME/app/flow_code/function_basic_flow
COPY ./flows/class_basic_flow/standard /home/$USERNAME/app/flow_code/class_basic_flow
COPY ./flows/yaml_basic_flow/standard /home/$USERNAME/app/flow_code/yaml_basic_flow

WORKDIR /home/$USERNAME/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]