# syntax=docker/dockerfile:1
FROM centos:7
RUN yum -y update
RUN yum -y install python3
COPY . .
RUN pip install -y requirements.txt
CMD ["python3", "server.py"]
