# -- Standard lib ------------------------------------------------------------
import copy
import json
import logging
import os

# -- 3rd party ---------------------------------------------------------------
import jsonschema

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.logparser import parse_log
from canarieapi.monitoring import monitor

# The schema that must be respected by the config
with open(os.path.join(os.path.dirname(__file__), "schema.json"), mode="r", encoding="utf-8") as schema_file:
    CONFIGURATION_SCHEMA = json.load(schema_file)


def validate_config_schema(update_db: bool, run_jobs: bool = True) -> None:
    config = APP.config
    logger: logging.Logger = APP.logger

    logger.info("Testing configuration...")

    configuration_schema = copy.deepcopy(CONFIGURATION_SCHEMA)
    if config.get("PARSE_LOGS", True):
        configuration_schema["definitions"]["service_description_schema"]["required"].append("stats")
        configuration_schema["definitions"]["platform_description_schema"]["required"].append("stats")
    try:
        jsonschema.validate(config, configuration_schema)
    except jsonschema.ValidationError as exc:
        raise jsonschema.ValidationError(f"The configuration is invalid : {exc!s}")

    if run_jobs:
        monitor(update_db=update_db)

        if config.get("PARSE_LOGS", True):
            access_log_fn = config["DATABASE"]["access_log"]
            route_invocations = {}
            file_checked = 0
            try:
                route_stats = parse_log(access_log_fn)
            except IOError:
                logger.warning("Unable to read logs from %s", access_log_fn)
            else:
                for route, value in route_stats.items():
                    route_invocations[route] = route_invocations.get(route, 0) + value["count"]

            for route, invocs in route_invocations.items():
                if invocs > 0:
                    logger.info("Found %s invocations to route %s in %s log files", invocs, route, file_checked)
                else:
                    logger.warning("Found no invocations to route %s in %s log files", route, file_checked)
            if not route_invocations:
                logger.warning("Found no invocations at all in %s log files", file_checked)
    logger.info("Tests completed!")
