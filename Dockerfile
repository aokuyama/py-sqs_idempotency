FROM python:3.8.12-slim-buster
ENV PYTHONIOENCODING utf-8
RUN pip install boto3
