.. :changelog:

CHANGES
=======

`Unreleased <https://github.com/Ouranosinc/CanarieAPI/tree/master>`_ (latest)
------------------------------------------------------------------------------------

.. **ADD LIST ITEMS WITH NEW CHANGES AND REMOVE THIS COMMENT**

* No changes yet.

`1.0.0 <https://github.com/Ouranosinc/CanarieAPI/tree/1.0.0>`_ (2023-08-29)
------------------------------------------------------------------------------------

* Separate the application, cron job, and proxy (nginx) into separate containers so that they can be run independently.
* Add option to independently enable/disable the ``parse_logs`` cron job by setting the ``PARSE_LOGS`` configuration
  option to ``True``.
* Do not handle log rotation for nginx anymore. Nginx should handle this on its own.
* Made default port 2000 everywhere (not just in docker).
* Replace Docker image reference ``nginx:bullseye`` by ``nginx:stable-bullseye`` which gets updated more often,
  for latest security vulnerability fixes.

`0.7.2 <https://github.com/Ouranosinc/CanarieAPI/tree/0.7.2>`_ (2023-04-19)
------------------------------------------------------------------------------------

* Minor CSS adjustments to allow platform links to display on a single line if the monitor viewport is sufficient.

`0.7.1 <https://github.com/Ouranosinc/CanarieAPI/tree/0.7.1>`_ (2023-04-14)
------------------------------------------------------------------------------------

* Remove unnecessary packages installed in Docker image to reduce security issues.
* Update flagged Python packages with minimal versions to resolve known security issues.

`0.7.0 <https://github.com/Ouranosinc/CanarieAPI/tree/0.7.0>`_ (2023-04-14)
------------------------------------------------------------------------------------

* Add a retry function decorator for database operations to handle rare occurrences where the database could have been
  improperly initialized. In case of relevant database issue, the operation is retried after running the initialization.
* Add more logging entries to help debug error causes and relevant database operations that lead to them if applicable.
* Avoid unnecessary creation of a database connection simply to close it when performing teardown request cleanup.
  This occurred at least 3 times for each HTML requests because of UI static file requests retrieved for display.
  Also, avoids the unnecessary verbose logging of opening, finding and closing this unused database connection.

`0.6.0 <https://github.com/Ouranosinc/CanarieAPI/tree/0.6.0>`_ (2023-03-22)
------------------------------------------------------------------------------------

* Add better table formatted HTML rendering from the stats endpoints even when a monitoring error of an underlying
  endpoint occurs to allow better readability of the cause of error.
* Add cached database logging entry to facilitate debugging.

`0.5.1 <https://github.com/Ouranosinc/CanarieAPI/tree/0.5.1>`_ (2023-02-16)
------------------------------------------------------------------------------------

* Fix ``Dockerfile`` to setup ``CanarieAPI`` accessible from anywhere to avoid ``canarieapi-cron`` failure unless
  explicit ``PYTHONPATH`` was specified. Avoids unresolved package location with ``ImportError``/``ModuleNotFoundError``
  when calling the ``logparser`` and ``monitoring`` scripts.
* Add ``CanarieAPI`` import validation with ``test-docker`` to ensure package is properly installed and accessible
  from anywhere in the Docker image.

`0.5.0 <https://github.com/Ouranosinc/CanarieAPI/tree/0.5.0>`_ (2023-02-15)
------------------------------------------------------------------------------------

* Support query parameter ``f=json`` as alternate method to HTTP ``Accept`` header to provide JSON responses.
* Support additional ``request`` parameters, formats and validations for arguments provided to monitoring services and
  platform definitions loaded from the configuration. New parameters include ``timeout``, ``proxies``, ``stream``,
  ``verify``, ``cert`` and ``allow_redirects`` all supported by ``requests.request`` method and compatible as JSON.
* Refactor ``canarieapi.test`` into ``canarieapi.schema`` and rename ``test_config`` to ``validate_config_schema``
  to better represent their intended use.
* Move Python-based configuration schema to ``schema.json`` file to allow reference by external validators.
* Add multiple linting validations with Makefile targets.
* Add minimal tests with GitHub Actions CI integration.
* Fix database global reference not being reused causing connection recreation on each database query.
* Drop support of end-of-life Python 2.7, 3.5 and 3.6.

`0.4.4 <https://github.com/Ouranosinc/CanarieAPI/tree/0.4.4>`_ (2023-02-01)
------------------------------------------------------------------------------------

* Fix ``Flask`` requirements and expected configurations to setup the web application.
* Fix broken example URL in ``canarieapi/default_configuration.py``.
* Fix linting and variable name shadowing within scoped or built-in context.

`0.4.3 <https://github.com/Ouranosinc/CanarieAPI/tree/0.4.3>`_ (2020-05-01)
------------------------------------------------------------------------------------
* Fix ``Dockerfile`` with symlink python => python3
* Fix how ``default_configuration`` is imported by ``app_object.py``

`0.4.2 <https://github.com/Ouranosinc/CanarieAPI/tree/0.4.2>`_ (2020-03-27)
------------------------------------------------------------------------------------

* Fix missed header title in ``0.4.0`` that also had an hardcoded ``Ouranosinc`` mention.
  The browser tab will now also use the ``SERVER_MAIN_TITLE`` value if provided in configuration.
* Use full URL reference to issues in this changelog for easier access in documentation and on GitHub.

`0.4.1 <https://github.com/Ouranosinc/CanarieAPI/tree/0.4.1>`_ (2020-03-20)
------------------------------------------------------------------------------------

* Fix ``Dockerfile`` setup with Python 3.
* Fix imports to use the package ``canarieapi`` module.

`0.4.0 <https://github.com/Ouranosinc/CanarieAPI/tree/0.4.0>`_ (2020-03-18)
------------------------------------------------------------------------------------

* Provide parameter to update server title.
* Update configurations mismatching with existing tag versions.
* Update documentation for setup, installation and execution of the application.
* Add DevOps utilities using ``Makefile``.
* Drop Python 2 support.

`0.3.5 <https://github.com/Ouranosinc/CanarieAPI/tree/0.3.5>`_ (2017-11-09)
------------------------------------------------------------------------------------

* Fix bug in monitoring introduced in previous version.

`0.3.4 <https://github.com/Ouranosinc/CanarieAPI/tree/0.3.4>`_ (2017-11-09) and prior
-------------------------------------------------------------------------------------

* [TODO] missing details

`0.1.0 <https://github.com/Ouranosinc/CanarieAPI/tree/0.1.0>`_ (2017-10-12)
------------------------------------------------------------------------------------

* First structured release.
