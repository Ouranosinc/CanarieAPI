"""
This module serves the purpose of centralizing the state object of Flask in a single place.
"""

# -- Standard lib ------------------------------------------------------------
from os import environ

# -- 3rd party modules -------------------------------------------------------
from flask import Flask

# -- Project specific --------------------------------------------------------
import default_configuration
from reverse_proxied import ReverseProxied


APP = Flask(__name__)

# Handle Reverse Proxy setups
APP.wsgi_app = ReverseProxied(APP.wsgi_app)

# Config
APP.config.from_object(default_configuration)
if 'CANARIE_API_CONFIG_FN' in environ:
    APP.config.from_envvar('CANARIE_API_CONFIG_FN')
