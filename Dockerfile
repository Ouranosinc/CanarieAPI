FROM ubuntu:16.04
MAINTAINER David Byrns

RUN apt-get update && apt-get install -y \
	build-essential \
	python-dev \
	python-pip

RUN pip install --upgrade pip setuptools
RUN pip install gunicorn

COPY requirements.txt /opt/local/src/CanarieAPI/requirements.txt
RUN pip install -r /opt/local/src/CanarieAPI/requirements.txt
COPY ./ /opt/local/src/CanarieAPI/
RUN pip install /opt/local/src/CanarieAPI/

ENV PORT=2000

ENTRYPOINT exec gunicorn -b 0.0.0.0:$PORT /opt/local/src/CanarieAPI/canarieapi/canarieapi.wsgi