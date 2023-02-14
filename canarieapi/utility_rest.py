#!/usr/bin/env python
# coding:utf-8

"""
REST API utilities.

This module is a collection of utility functions used mainly by the rest_route
module and which are placed here to keep the rest_route module as clean as possible.
"""


# -- Standard lib ------------------------------------------------------------
import configparser
import http.client
import os
import re
import sqlite3
from typing import Dict, List, Optional, Tuple, Union
from typing_extensions import Literal, TypeAlias

# -- 3rd party ---------------------------------------------------------------
from flask import Response, current_app, g, jsonify, redirect, render_template, request
from werkzeug.datastructures import MIMEAccept
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.routing import BaseConverter, Map

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP

APIType = Literal["platform", "service"]
_JSON: TypeAlias = "JSON"
JSON = Union[Dict[str, Union[Dict[str, _JSON], List[_JSON], _JSON, float, int, str, bool, None]], _JSON]


def request_wants_json() -> bool:
    """
    Check if the request type is of type JSON.

    The default mimetype */* is interpreted as JSON.
    """

    # Best will be JSON if it's in accepted mimetypes and
    # has a quality greater or equal to HTML.
    # For */* both JSON and HTML will have the same quality so JSON still win
    choices = ["application/json", "text/html"]
    best = request.accept_mimetypes.best_match(choices)
    return request.args.get("f", "").lower() == "json" or best == "application/json"


def set_html_as_default_response() -> None:
    """
    Set the default response Media-Type, with fallback to JSON.

    By default, if the accepted mimetypes contains */*, JSON format will be used.
    By calling this function, the */* mimetype will be changed explicitly into
    text/html so that it becomes the mimetype used by default.
    This is useful for automatically rendering HTML by web browsers that do not
    provide explicitly the desired mimetype.
    """

    # Best will be HTML if it's in accept mimetypes and
    # has a quality greater or equal to JSON.
    # For */* both JSON and HTML will have the same quality so HTML still wins
    best = request.accept_mimetypes.best_match(["text/html",
                                                "application/json"])
    # Replace any */* by HTML so that JSON isn't picked by default
    if best == "text/html":
        accept = MIMEAccept([("text/html", request.accept_mimetypes["text/html"])])
        request.accept_mimetypes = accept  # noqa


def get_config(route_name: str, api_type: APIType) -> JSON:
    """
    Return the config for the particular service/platform associated with the given route name.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :raises: Exception if the route is unknown
    """
    try:
        conf = APP.config[api_type.upper() + "S"]
    except KeyError:
        raise BadRequest(f"The request has been made for an unknown type: [{api_type}]")
    try:
        return conf[route_name]
    except KeyError:
        raise NotFound(f"The request has been made for a {api_type} that is not supported: [{route_name}]")


def validate_route(route_name: str, api_type: APIType) -> None:
    """
    Check if the route name is a value amongst known services/platforms in the configuration.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :raises: Exception if the route is unknown
    """
    get_config(route_name, api_type)


def get_api_title(route_name: str, api_type: APIType) -> str:
    """
    Get the API title to be shown in rendered html page.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :returns: An API title
    """

    title = api_type.capitalize()
    try:
        name = get_config(route_name, api_type)["info"]["name"]
        title = f"{title}: {name}"
    except Exception:
        pass
    return title


def get_canarie_api_response(route_name, api_type, api_request):
    """
    Provide a valid response for the CANARIE API request based on the service route.

    :param route_name: Route name of the service/platform coming from the URL e.g. :
                          ['pavics', 'node', 'bias', etc.]
    :param api_type: Api type of the route which must be one of platform or service
    :param api_request: The request specified in the URL
    :returns: A valid HTML response
    """

    # Factsheet is not part of the service API, so it's expected that the config will not be found
    if api_type == "service" and api_request == "factsheet":
        return make_error_response(http_status=404)

    try:
        cfg_val = get_config(route_name, api_type)["redirect"][api_request]
        if cfg_val.find("http") == 0:
            return redirect(cfg_val)
    except KeyError:
        pass

    msg = (
        f"The {api_type} does not provide in its configuration file a "
        f"valid source for the CANARIE request {api_request}"
    )
    raise configparser.Error(msg)


def make_error_response(
    http_status: Optional[int] = None,
    http_status_response: Optional[str] = None,
) -> Tuple[Union[Response, str], int]:
    """
    Make an error response based on the request type and given information.

    :param http_status: HTTP status
    :param http_status_response: Standard message associated with a status
                code. Obtained via :py:data:`http.client.responses` if not
                provided.
    """
    if http_status is None or http_status < 100:
        http_status = 500

    # If the status response is None use the one provide by http.client
    if http_status_response is None:
        http_status_response = http.client.responses[http_status]
    # Else, check if http_status_response already contains the HTML status code
    else:
        match = re.search("^([0-9]*):? *(.*)$", http_status_response)
        if match and match.group(1) == str(http_status):
            # In which case it is removed from the response
            http_status_response = match.group(2)

    if request_wants_json():
        response = {
            "status": http_status,
            "description": http_status_response
        }
        return jsonify(response), http_status

    html_response_header = f"{http_status} : {http_status_response}"
    template = render_template("error.html",
                               Main_Title="Canarie API",
                               Title="Error",
                               html_response=html_response_header)
    return template, http_status


def get_db() -> sqlite3.Connection:
    """
    Get a connection to an existing database.

    If the database does not exist, create a connection to local sqlite3 file.
    If the local sqlite3 file doesn't exist, initialize it using a schema.
    """
    database = getattr(g, "_database", None)
    if database is None:
        APP.logger.info("Database not defined. Establishing connection...")

        database_fn = APP.config["DATABASE"]["filename"]
        APP.logger.debug("Using configured filename: [%s]", database_fn)
        if not os.path.isabs(database_fn):
            database_fn = os.path.join(APP.root_path, database_fn)
        database_fn = os.path.abspath(database_fn)

        APP.logger.debug("Setup database connection with filename: [%s]", database_fn)
        db_exists = os.path.isfile(database_fn)  # must resolve before connect otherwise file already created
        try:
            database = g._database = sqlite3.connect(database_fn)
        except Exception as exc:
            APP.logger.error(
                "Error [%s] occurred during database connection with filename: [%s].",
                str(exc), database_fn, exc_info=exc
            )
            APP.logger.debug("Reraise for error reporting.")
            raise

        APP.logger.debug("Initialize database with filename: [%s]", database_fn)
        if not db_exists:
            try:
                init_db(database)
            except Exception as exc:
                APP.logger.error(
                    "Error [%s] occurred during database initialization with filename: [%s].",
                    str(exc), database_fn, exc_info=exc
                )
                APP.logger.debug("Closing database.")
                database.close()
                APP.logger.debug("Deleting database filename (reset for recreation): [%s].", database_fn)
                os.remove(database_fn)
                APP.logger.debug("Reraise for error reporting.")
                raise

    return database


def init_db(database: sqlite3.Connection) -> None:
    """
    Initialize a database from a schema.
    """
    APP.logger.debug("Initializing database")
    with current_app.app_context():
        dbs_fn = "database_schema.sql"
        if os.path.isabs(dbs_fn):
            schema_fn = dbs_fn
        else:
            schema_fn = os.path.join(APP.root_path, dbs_fn)

        APP.logger.debug("Using schema filename : %s", schema_fn)
        with current_app.open_resource(schema_fn, mode="r") as schema_f:
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

    Since it would parse as float 1,2 and 3.
    """

    def __init__(self, mapping: Map, *items: Union[int, str]) -> None:
        BaseConverter.__init__(self, mapping)
        # Start by enforcing that x is an integer then convert it to string
        self.regex = f"(?:{'|'.join([str(int(x)) for x in items])})"
