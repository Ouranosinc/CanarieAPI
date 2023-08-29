========
Usage
========

Create a custom ``canarieapi/configuration.py`` file similar to ``canarieapi/default_configuration.py`` and define
the environment variable ``CANARIE_API_CONFIG_FN`` pointing to it in order to use your desired configurations.

Run the ``CanarieAPI`` using ``gunicorn``::

    cd <CanarieAPI-root>/canarieapi
    ../bin/gunicorn -b 0.0.0.0:2000 --workers 1 --log-level=DEBUG --timeout 30 -k gevent wsgi


Run the monitoring and/or the log parsing task as cron jobs.

To run the log parsing job, add the following to a crontab file::

    * * * * * python3 -c 'from canarieapi import logparser; logparser.cron_job()' 2>&1

The log parsing job requires that a nginx reverse proxy service is running and the ``DATABASE["access_log"]``
variable is set in the ``canarieapi/configuration.py`` script.

To run the the monitoring job, add the following to a crontab file::

    * * * * * python3 -c 'from canarieapi import monitoring; monitoring.cron_job()' 2>&1
