FROM nginx
LABEL description="CanarieAPI: Self describing REST service for Canarie registry."
LABEL maintainer="David Byrns <david.byrns@crim.ca>, Francis Charette-Migneault <francis.charette-migneault@crim.ca>"
LABEL vendor="Ouranosinc, CRIM"
LABEL version="0.4.0"

ENV PKG_DIR=/opt/local/src/CanarieAPI
WORKDIR ${PKG_DIR}

# Add logparser cron job in the cron directory
ADD canarieapi-cron /etc/cron.d/canarieapi-cron
RUN chmod 0644 /etc/cron.d/canarieapi-cron

# Install dependencies
COPY canarieapi/__init__.py canarieapi/__meta__.py ${PKG_DIR}/canarieapi/
COPY requirements.txt setup.* README.rst HISTORY.rst ${PKG_DIR}/
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        python3-dev \
        python3-pip \
        cron \
        vim \
        sqlite3 \
	&& ln -s $(which pip3) /usr/local/bin/pip \
    && pip install --no-cache-dir --upgrade pip setuptools gunicorn gevent \
    && pip install --no-cache-dir --upgrade -r ${PKG_DIR}/requirements.txt \
    && pip install --no-cache-dir -e ${PKG_DIR}

# Install package
COPY ./ ${PKG_DIR}/
RUN pip install --no-dependencies -e ${PKG_DIR}

# cron job will inherit the current user environment
# start cron service
# start nginx service
# start gunicorn
CMD env >> /etc/environment \
    && cron \
    && gunicorn \
        -b 0.0.0.0:2000 \
        --workers 1 \
        --log-level=DEBUG \
        --timeout 30 \
        --daemon \
        -k gevent \
        canarieapi.wsgi \
    && nginx \
        -g "daemon off;"
