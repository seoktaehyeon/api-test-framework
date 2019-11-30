FROM python:3.7-alpine3.10
MAINTAINER Will v.stone@163.com
COPY . /tmp
RUN cd /tmp && \
    python setup.py install
WORKDIR /workspace
CMD top
