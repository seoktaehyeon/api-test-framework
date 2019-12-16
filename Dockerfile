FROM python:3.7-alpine3.10
MAINTAINER Will v.stone@163.com
COPY . /tmp
RUN cd /tmp && \
    pip install -r requiemnts.txt && \
    python setup.py install
WORKDIR /workspace
