#FROM python39:latest
FROM python:3.8.13-alpine3.15
MAINTAINER nanjozy/javcapture
COPY dist/lib /data
WORKDIR /data/
RUN pip3 install greenlet --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple;\
    pip3 install gevent --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple;\
    pip3 install gunicorn --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple;\
    pip3 install -r requirements.txt --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple;
VOLUME /data/data/
EXPOSE 5004
CMD /bin/sh
ENTRYPOINT gunicorn --config /data/gunicorn_cfg.py entry_web:app