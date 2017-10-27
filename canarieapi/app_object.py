"""
This module serves the purpose of centralizing the state object of Flask in a single place.
"""

import logging
# -- Standard lib ------------------------------------------------------------
import sys
# -- 3rd party modules -------------------------------------------------------
from flask import Flask
from os import environ

# -- Project specific --------------------------------------------------------
import default_configuration
from reverse_proxied import ReverseProxied


APP = Flask(__name__)
formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] %(name)s : %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
APP.logger.addHandler(ch)
APP.logger.setLevel(logging.DEBUG)

# Handle Reverse Proxy setups
APP.wsgi_app = ReverseProxied(APP.wsgi_app)

# Config
APP.config.from_object(default_configuration)
if 'CANARIE_API_CONFIG_FN' in environ:
    APP.config.from_envvar('CANARIE_API_CONFIG_FN')
    APP.logger.info('Loading custom configuration from "{0}"'.format(environ['CANARIE_API_CONFIG_FN']))
else:
    APP.logger.info('Using default configuration')