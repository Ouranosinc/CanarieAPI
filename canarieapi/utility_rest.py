#!/usr/bin/env python
# coding:utf-8

"""
This module is a collection of utility functions used mainly by the rest_route
module and which are placed here to keep the rest_route module as clean as
possible.
"""


# -- Standard lib ------------------------------------------------------------
import configparser
import http.client
import re
from os import remove
from os import path

# -- 3rd party ---------------------------------------------------------------
from werkzeug.datastructures import MIMEAccept
from werkzeug.routing import BaseConverter
from flask import render_template
from flask import redirect
from flask import request
from flask import jsonify
from flask import g
from flask import current_app
import sqlite3

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP


def request_wants_json():
    """
    Check if the request type is of type JSON.

    The default mimetype */* is interpreted as JSON.
    """

    # Best will be JSON if it's in accepted mimetypes and
    # has a quality greater or equal to HTML.
    # For */* both JSON and HTML will have the same quality so JSON still win
    choices = ['application/json', 'text/html']
    best = request.accept_mimetypes.best_match(choices)
    return best == 'application/json'


def set_html_as_default_response():
    """
    By default, if the accepted mimetypes contains */*, JSON format will be
    used.

    By calling this function, the */* mimetype will be changed explicitly into
    text/html so that it becomes the mimetype used by default.
    """

    # Best will be HTML if it's in accept mimetypes and
    # has a quality greater or equal to JSON.
    # For */* both JSON and HTML will have the same quality so HTML still wins
    best = request.accept_mimetypes.best_match(['text/html',
                                                'application/json'])
    # Replace any */* by HTML so that JSON isn't picked by default
    if best == 'text/html':
        request.accept_mimetypes = \
            MIMEAccept([('text/html',
                         request.accept_mimetypes['text/html'])])


def get_config(route_name, api_type):
    """
        Return the config for the particular service/platform associated with the given route name.

        :param route_name: Route name of the service/platform coming from the URL e.g. :
                              ['pavics', 'node', 'bias', etc.]
        :param api_type: Api type of the route which must be one of platform or service
        :raises: Exception if the route is unknown
    """
    try:
        return APP.config[api_type.upper() + 'S'][route_name]
    except KeyError:
        raise Exception('The request has been made for a {api_type} that is not supported : {route}'
                        .format(api_type=api_type,
                                route=route_name))


def validate_route(route_name, api_type):
    """
    Check if the route name is a value amongst known services/platforms in the
    configuration.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :raises: Exception if the route is unknown
    """
    get_config(route_name, api_type)


def get_api_title(route_name, api_type):
    """
    Get the API title to be shown in rendered html page.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :returns: An API title
    """

    title = api_type.capitalize()
    try:
        name = get_config(route_name, api_type)['info']['name']
        title = name + ' ' + title
    except:
        pass
    return title


def get_canarie_api_response(route_name, api_type, api_request):
    """
    Provide a valid HTML response for the CANARIE API request based on the
    service_route.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :param api_request: The request specified in the URL
    :returns: A valid HTML response
    """

    # Factsheet is not part of the service API so it's expected that the config will not be found
    if api_type == 'service' and api_request == 'factsheet':
        return make_error_response(html_status=404)

    try:
        cfg_val = get_config(route_name, api_type)['redirect'][api_request]
        if cfg_val.find('http') == 0:
            return redirect(cfg_val)
    except KeyError:
        pass

    msg = ("The {0} does not provide in it's configuration file a "
           "valid source for the CANARIE request {1}".format(api_type, api_request))
    raise configparser.Error(msg)


def make_error_response(html_status=None,
                        html_status_response=None):
    """
    Make an error response based on the request type and given information.

    :param html_status: HTML status
    :param html_status_response: Standard message associated with a status
                code. Obtained via :py:data:`http.client.responses` if not
                provided.
    """

    # If the status response is None use the one provide by http.client
    if html_status_response is None:
        html_status_response = http.client.responses[html_status]
    # Else, check if html_status_response already contains the HTML status code
    else:
        match = re.search("^([0-9]*):? *(.*)$", html_status_response)
        if match and match.group(1) == str(html_status):
            # In which case it is removed from the response
            html_status_response = match.group(2)

    if request_wants_json():
        response = {
            'status': html_status,
            'description': html_status_response
        }
        return jsonify(response), html_status
    else:
        html_response_header = (u'{status} : {resp}'.format(status=html_status,
                                                            resp=html_status_response))

        template = render_template('error.html',
                                   Main_Title='Canarie API',
                                   Title='Error',
                                   html_response=html_response_header)
        return template, html_status


def get_db():
    """
    Get a connection to an existing database. If it does not exist, create a
    connection to local sqlite3 file.

    If the local sqlite3 file doesn't exist, initialize it using a schema.
    """
    database = getattr(g, '_stats_database', None)
    if database is None:
        d_fn = APP.config['DATABASE']['filename']
        if path.isabs(d_fn):
            database_fn = d_fn
        else:
            database_fn = path.join(APP.root_path, d_fn)

        APP.logger.debug(u"Using db filename : {0}".format(database_fn))
        if not path.exists(database_fn):
            database = g._database = sqlite3.connect(database_fn)
            try:
                init_db(database)
            except:
                database.close()
                remove(database_fn)
                raise
        else:
            database = g._database = sqlite3.connect(database_fn)

    return database


def init_db(database):
    """
    Initialize a database from a schema
    """
    APP.logger.info(u"Initializing database")
    with current_app.app_context():
        dbs_fn = 'database_schema.sql'
        if path.isabs(dbs_fn):
            schema_fn = dbs_fn
        else:
            schema_fn = path.join(APP.root_path, dbs_fn)

        APP.logger.debug(u"Using schema filename : {0}".format(schema_fn))
        with current_app.open_resource(schema_fn, mode='r') as schema_f:
            database.cursor().executescript(schema_f.read())
        database.commit()


class AnyIntConverter(BaseConverter):
    """
    Matches one of the items provided.

    Items must be integer and comma separated with a space to avoid confusion
    with floating point value in the parser.

    For example::

       1, 2, 3

    And not::

       1,2,3

    Since it would parse as float 1,2 and 3 .
    """

    def __init__(self, mapping, *items):
        BaseConverter.__init__(self, mapping)
        # Start by enforcing that x is an integer then convert it to string
        self.regex = '(?:%s)' % '|'.join([str(int(x)) for x in items])
