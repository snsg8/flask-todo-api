FROM mcr.microsoft.com/devcontainers/python:dev-3.12

WORKDIR app
COPY requirements.txt .

RUN pip install -r requirements.txt

