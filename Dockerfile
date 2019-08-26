FROM python:3.7-alpine3.10
MAINTAINER Will v.stone@163.com
WORKDIR /workspace
COPY . .
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ -r requirements.txt && \
    mkdir test_case && \
    mkdir test_data && \
    mkdir data_template && \
    chmod +x api-tester.py
CMD top
