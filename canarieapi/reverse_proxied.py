#!/usr/bin/env python
# coding:utf-8
"""
Middleware for reverse proxy.

This module implements a middleware that makes the Flask application work
seamlessly behind a reverse proxy.
"""

from typing import Any, Callable, Dict

from flask import Response


class ReverseProxied(object):
    """
    Class which implements a middleware so :mod:`Flask` can be used behind a reverse proxy.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    def __call__(self, environ: Dict[str, str], start_response: Callable) -> Response:
        script_name = environ.get("HTTP_X_SCRIPT_NAME", None)

        if script_name is not None:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]

            if path_info.startswith(script_name):
                path_info = path_info[len(script_name):]
                environ["PATH_INFO"] = path_info

        scheme = environ.get("HTTP_X_SCHEME", None)
        if scheme is not None:
            environ["wsgi_url_scheme"] = scheme

        return self.app(environ, start_response)
