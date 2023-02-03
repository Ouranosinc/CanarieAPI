# -- Standard lib ------------------------------------------------------------

# -- 3rd party ---------------------------------------------------------------
import jsonschema

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.logparser import LOG_BACKUP_COUNT, parse_log
from canarieapi.monitoring import monitor

# The schema that must be respected by the config
CONFIGURATION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Config",
    "description": "Canarie API Configuration file schema",
    "type": "object",
    "required": ["MY_SERVER_NAME", "DATABASE", "SERVICES", "PLATFORMS"],
    "properties": {
        "MY_SERVER_NAME": {
            "description": "Root url from where the Canarie API is served",
            "type": "string"
        },
        "DATABASE": {
            "description": "Parameters about database and its data source",
            "type": "object",
            "required": ["filename", "access_log", "log_pid"],
            "additionalProperties": False,
            "properties": {
                "filename": {
                    "description": "Filename of the database",
                    "type": "string"
                },
                "access_log": {
                    "description": "NGINX log file location",
                    "type": "string"
                },
                "log_pid": {
                    "description": "NGINX pid file location",
                    "type": "string"
                }
            }
        },
        "SERVICES": {
            "description": "Services to be served by the Canarie API",
            "type": "object",
            "minItems": 0,
            "patternProperties": {
                ".*": {"$ref": "#/definitions/service_description_schema"}
            }
        },
        "PLATFORMS": {
            "description": "Platforms to be served by the Canarie API",
            "type": "object",
            "minItems": 0,
            "patternProperties": {
                ".*": {"$ref": "#/definitions/platform_description_schema"}
            }
        }
    },
    "definitions": {
        "service_description_schema": {
            "description": "Describe a service",
            "type": "object",
            "required": ["info", "stats", "redirect", "monitoring"],
            "additionalProperties": False,
            "properties": {
                "info": {"$ref": "#/definitions/service_info_schema"},
                "stats": {"$ref": "#/definitions/stats_schema"},
                "redirect": {"$ref": "#/definitions/service_redirect_schema"},
                "monitoring": {"$ref": "#/definitions/monitoring_schema"}
            }
        },
        "platform_description_schema": {
            "description": "Describe a platform",
            "type": "object",
            "required": ["info", "stats", "redirect", "monitoring"],
            "additionalProperties": False,
            "properties": {
                "info": {"$ref": "#/definitions/platform_info_schema"},
                "stats": {"$ref": "#/definitions/stats_schema"},
                "redirect": {"$ref": "#/definitions/platform_redirect_schema"},
                "monitoring": {"$ref": "#/definitions/monitoring_schema"}
            }
        },
        "service_info_schema": {
            "description": "Parameters required by the route /info of the Canarie API",
            "type": "object",
            "required": [
                "name",
                "synopsis",
                "version",
                "institution",
                "releaseTime",
                "researchSubject",
                "supportEmail",
                "tags",
                "category"
            ],
            "maxProperties": 9,
            "properties": {
                "tags": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                }
            },
            "additionalProperties": {
                "type": "string"
            }
        },
        "platform_info_schema": {
            "description": "Parameters required by the route /info of the Canarie API",
            "type": "object",
            "required": [
                "name",
                "synopsis",
                "version",
                "institution",
                "releaseTime",
                "researchSubject",
                "supportEmail",
                "tags"
            ],
            "maxProperties": 8,
            "properties": {
                "tags": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                }
            },
            "additionalProperties": {
                "type": "string"
            }
        },
        "stats_schema": {
            "description": "Parameters used to count service invocations",
            "type": "object",
            "required": ["method", "route"],
            "additionalProperties": False,
            "properties": {
                "method": {
                    "description": "Regex describing the request method to count",
                    "type": "string"
                },
                "route": {
                    "description": "Regex describing the request route to count",
                    "type": "string"
                }
            }
        },
        "service_redirect_schema": {
            "description": "List of redirection for most of the Canarie API requests",
            "type": "object",
            "required": ["doc", "releasenotes", "support", "source", "tryme", "licence", "provenance"],
            "maxProperties": 7,
            "additionalProperties": {
                "type": "string"
            }
        },
        "platform_redirect_schema": {
            "description": "List of redirection for most of the Canarie API requests",
            "type": "object",
            "required": ["doc", "releasenotes", "support", "source", "tryme", "licence", "provenance", "factsheet"],
            "maxProperties": 8,
            "additionalProperties": {
                "type": "string"
            }
        },
        "monitoring_schema": {
            "description": "List of components needing to be monitored to consider a service / platform functional",
            "type": "object",
            "minItems": 0,
            "patternProperties": {
                ".*": {"$ref": "#/definitions/monitoring_component_schema"}
            }
        },
        "monitoring_component_schema": {
            "description": "Component needing to be monitored to consider a service / platform functional",
            "type": "object",
            "required": ["request"],
            "additionalProperties": False,
            "properties": {
                "request": {
                    "description": "Describe the request to be done to the component",
                    "type": "object",
                    "required": ["url"],
                    "additionalProperties": False,
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string"},
                        "params": {"type": "object"},
                        "headers": {"type": "object"},
                        "data": {"type": "object"},
                        "json": {"type": "object"}
                    }
                },
                "response": {
                    "description": "Describe the required response",
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "status_code": {"type": "integer"},
                        "text": {"type": "string"},
                    }
                }
            }
        }
    }
}


def validate_config_schema(update_db):
    # type: (bool) -> None
    config = APP.config
    logger = APP.logger

    logger.info("Testing configuration...")
    try:
        jsonschema.validate(config, CONFIGURATION_SCHEMA)
    except jsonschema.ValidationError as e:
        raise Exception("The configuration is invalid : {0}".format(str(e)))

    monitor(update_db=update_db)

    access_log_fn = config["DATABASE"]["access_log"]
    route_invocations = {}
    file_checked = 0
    for i in range(0, min(10, LOG_BACKUP_COUNT)):
        fn = access_log_fn + (".{0}".format(i) if i > 0 else "")
        try:
            route_stats = parse_log(fn)
            for route, value in route_stats.items():
                route_invocations[route] = route_invocations.get(route, 0) + value["count"]
            file_checked += 1
        except IOError:
            break

    for route, invocs in route_invocations.items():
        if invocs > 0:
            logger.info("Found {0} invocations to route {1} in {2} log files".format(invocs, route, file_checked))
        else:
            logger.warn("Found no invocations to route {0} in {1} log files".format(route, file_checked))
    if not route_invocations:
        logger.warn("Found no invocations at all in {0} log files".format(file_checked))
    logger.info("Tests completed!")
