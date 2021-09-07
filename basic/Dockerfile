# syntax=docker/dockerfile:1
FROM centos:7
RUN yum -y update
RUN yum -y install python3
COPY . .
WORKDIR system
CMD ["python3", "main.py"]
