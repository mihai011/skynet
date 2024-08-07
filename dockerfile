FROM python:3.10

RUN pip install apache-flink[all] 'pulsar-client==3.5.0'
RUN apt update && apt install -y default-jre default-jdk
