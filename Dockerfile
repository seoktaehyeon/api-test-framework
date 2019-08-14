FROM python:3.7-alpine3.10
MAINTAINER Will v.stone@163.com
WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt
