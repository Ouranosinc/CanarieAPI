FROM python:3.11
LABEL description="CanarieAPI: Self describing REST service for Canarie registry."
LABEL maintainer="David Byrns <david.byrns@crim.ca>, Francis Charette-Migneault <francis.charette-migneault@crim.ca>"
LABEL vendor="Ouranosinc, CRIM"
LABEL version="0.7.2"

ENV PKG_DIR=/opt/local/src/CanarieAPI
WORKDIR ${PKG_DIR}

# Add logparser cron job in the cron directory
ADD docker/canarieapi-cron /etc/cron.d/canarieapi-cron
RUN chmod 0644 /etc/cron.d/canarieapi-cron

# Install dependencies
COPY canarieapi/__init__.py canarieapi/__meta__.py ${PKG_DIR}/canarieapi/
COPY requirements.txt setup.* README.rst CHANGES.rst ${PKG_DIR}/
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cron \
        sqlite3 \
    && pip install --no-cache-dir --upgrade pip setuptools gunicorn gevent \
    && pip install --no-cache-dir --upgrade -r ${PKG_DIR}/requirements.txt \
    && pip install --no-cache-dir -e ${PKG_DIR}

# Install package
COPY ./ ${PKG_DIR}/
RUN pip install --no-dependencies ${PKG_DIR}

# start gunicorn
CMD gunicorn \
    -b 0.0.0.0:2000 \
    --workers 1 \
    --log-level=DEBUG \
    --timeout 30 \
    -k gevent \
    canarieapi.wsgi
