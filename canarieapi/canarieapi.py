#!/usr/bin/env python
# coding:utf-8

# N.B. : Some of these docstrings are written in reSTructured format so that
# Sphinx can use them directly with fancy formatting.

# In the context of a REST application, this module must be loaded first as it
# is the one that instantiates the Flask Application on which other modules
# will depend.

"""
This module defines the generic REST API for platforms and services as defined by
the CANARIE API specification. See :
https://collaboration.canarie.ca/elgg/discussion/view/3664/research-software-api-documentation
"""


# -- Standard lib ------------------------------------------------------------
import collections
import datetime
import logging

# -- 3rd party ---------------------------------------------------------------
from flask import render_template
from flask import jsonify

# -- Project specific --------------------------------------------------------
from utility_rest import set_html_as_default_response
from utility_rest import get_canarie_api_response
from utility_rest import validate_route
from utility_rest import get_config
from utility_rest import get_api_title
from utility_rest import make_error_response
from utility_rest import request_wants_json
from utility_rest import AnyIntConverter
from app_object import APP


START_UTC_TIME = datetime.datetime.utcnow()

# REST requests required by CANARIE
CANARIE_API_VALID_REQUESTS = ['doc',
                              'releasenotes',
                              'support',
                              'source',
                              'tryme',
                              'license',
                              'provenance',
                              'factsheet']

CANARIE_API_TYPE = ['service',
                    'platform']

# HTML errors for which the application provides a custom error page
HANDLED_HTML_ERRORS = [400, 404, 405, 500, 503]
HANDLED_HTML_ERRORS_STR = ", ".join(map(str, HANDLED_HTML_ERRORS))

# Map an error handler for each handled HTML error
# Errors handled here are the ones that occur internally in the application
#
# The loop replace the following code for each handled html error
# @APP.errorhandler(400)
# def page_not_found_400(some_error):
#     return handle_error(400, str(some_error))
#
# For the lambda syntax see the following page explaining the requirement for
# status_code_copy=status_code
# http://stackoverflow.com/questions/938429/scope-of-python-lambda-functions-
# and-their-parameters/938493#938493
for status_code in HANDLED_HTML_ERRORS:
    APP.error_handler_spec[None][status_code] = \
        lambda more_info, status_code_copy = status_code: \
        make_error_response(html_status=status_code_copy,
                            html_status_response=str(more_info))


@APP.errorhandler(Exception)
def handle_exceptions(exception_instance):
    """
    Generate error response for raised exceptions.

    :param exception_instance: Exception instance.
    """
    logger = logging.getLogger(__name__)
    logger.debug(u"Generating error response for the exception {e}".
                 format(e=repr(exception_instance)))
    logger.exception(exception_instance)
    if APP.debug:
        logger.info(u"In debug mode, re-raising exception")
        raise
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(exception_instance).__name__, exception_instance.args)
    return make_error_response(html_status=400,
                               html_status_response=message)


# -- Flask routes ------------------------------------------------------------
APP.url_map.converters['any_int'] = AnyIntConverter




@APP.route("/")
def home():
    def parse_config(name, api_type, conf):
        hostname = APP.config['MY_SERVER_NAME']
        requests = sorted(['info', 'stats'] + conf.get('redirect', {}).keys())
        content = [(request, '{hostname}/{name}/{api_type}/{request}'
            .format(hostname=hostname, name=name, api_type=api_type, request=request))
                   for request in requests]
        return collections.OrderedDict(content)

    config = APP.config
    content = dict(platforms={name: parse_config(name, 'platform', p) for name, p in config['PLATFORMS'].items()},
                   services={name: parse_config(name, 'service', s) for name, s in config['SERVICES'].items()})
    return render_template('home.html', Main_Title='Canarie API', Title="Home", Content=content)

@APP.route("/<any_int(" + HANDLED_HTML_ERRORS_STR + "):status_code_str>")
def extern_html_error_handler(status_code_str):
    """
    Handle errors that occur externally provided that Apache is configured so
    that it uses this route for handling errors.

    For this add this line for each handled html errors in the Apache
    configuration::

       ErrorDocument 400 <Rest root>/400
    """
    return make_error_response(html_status=int(status_code_str))


@APP.route("/<route_name>/<any(" + ",".join(CANARIE_API_TYPE) + "):api_type>/info")
def information(route_name, api_type):
    """
    Info route required by CANARIE
    """

    # JSON is used by default but the Canarie API requires html as default
    set_html_as_default_response()

    validate_route(route_name, api_type)

    info_categories = ['name',
                       'synopsis',
                       'version',
                       'institution',
                       'releaseTime',
                       'researchSubject',
                       'supportEmail']

    if api_type == 'service':
        info_categories.append('category')

    config = get_config(route_name, api_type).get('info', {})
    info = []
    for category in info_categories:
        cat = config.get(category, '')
        info.append((category, cat))
    tags = config.get('tags', '')
    info.append(('tags', tags.split(',')))

    info = collections.OrderedDict(info)

    if request_wants_json():
        return jsonify(info)
    return render_template('default.html', Main_Title=get_api_title(route_name, api_type), Title="Info", Tags=info)


@APP.route("/<route_name>/<any(" + ",".join(CANARIE_API_TYPE) + "):api_type>/stats")
def stats(route_name, api_type):
    """
    Stats route required by CANARIE
    """

    # JSON is used by default but the Canarie API requires html as default
    set_html_as_default_response()

    validate_route(route_name, api_type)

    service_stats = {
        'lastReset': START_UTC_TIME.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'invocations': 0}

    if request_wants_json():
        return jsonify(service_stats)

    return render_template('default.html', Main_Title=get_api_title(route_name, api_type), Title="Stats", Tags=service_stats)



@APP.route("/<route_name>/<any(" + ",".join(CANARIE_API_TYPE) + "):api_type>/<any(" +
           ",".join(CANARIE_API_VALID_REQUESTS) + "):api_request>")
def simple_requests_handler(route_name, api_type, api_request='home'):
    """
    #Handle simple requests required by CANARIE
    """

    # JSON is used by default but the Canarie API requires html as default
    set_html_as_default_response()

    return get_canarie_api_response(route_name, api_type, api_request)



if __name__ == "__main__":
    port = 5000
    APP.debug = False
    APP.run(port=port)
