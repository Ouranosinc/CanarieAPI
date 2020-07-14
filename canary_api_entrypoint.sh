#!/usr/bin/env bash

env >> /etc/environment \
    && cron \
    && gunicorn \
        -b 0.0.0.0:2000 \
        --workers 1 \
        --log-level=DEBUG \
        --timeout 30 \
        --daemon \
        -k gevent \
        canarieapi.wsgi \
    && service nginx start \
    && /postgres-docker-entrypoint.sh postgres && "$@"