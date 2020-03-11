========
Usage
========

Create a custom ``canarieapi/configuration.py`` file similar to ``canarieapi/default_configuration.py`` and define
the environment variable ``CANARIE_API_CONFIG_FN`` pointing to it in order to use your desired configurations.

Run the ``CanarieAPI`` using ``gunicorn``::

    cd <CanarieAPI-root>/canarieapi
    ../bin/gunicorn -b 0.0.0.0:2000 --workers 1 --log-level=DEBUG --timeout 30 -k gevent wsgi

