FROM ubuntu:16.04
MAINTAINER David Byrns

RUN apt-get update && apt-get install -y \
	build-essential \
	python-dev \
	python-pip

RUN pip install --upgrade pip setuptools
RUN pip install gunicorn gevent

COPY requirements.txt /opt/local/src/CanarieAPI/requirements.txt
RUN pip install -r /opt/local/src/CanarieAPI/requirements.txt
COPY ./ /opt/local/src/CanarieAPI/
RUN pip install /opt/local/src/CanarieAPI/

EXPOSE 2000

WORKDIR /opt/local/src/CanarieAPI/canarieapi
CMD ["gunicorn", "-b", "0.0.0.0:2000", "--workers", "4", "--log-level=DEBUG", "--timeout", "30", "-k", "gevent", "wsgi"]