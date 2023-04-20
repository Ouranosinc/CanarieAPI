# -- Standard lib ------------------------------------------------------------
import json
import logging
import os

# -- 3rd party ---------------------------------------------------------------
import jsonschema

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.logparser import LOG_BACKUP_COUNT, parse_log
from canarieapi.monitoring import monitor

# The schema that must be respected by the config
with open(os.path.join(os.path.dirname(__file__), "schema.json"), mode="r", encoding="utf-8") as schema_file:
    CONFIGURATION_SCHEMA = json.load(schema_file)


def validate_config_schema(update_db: bool, run_jobs: bool = True) -> None:
    # type: (bool) -> None
    config = APP.config
    logger: logging.Logger = APP.logger

    logger.info("Testing configuration...")
    if config.get("PARSE_LOG"):
        CONFIGURATION_SCHEMA["definitions"]["service_description_schema"]["required"].append("stats")
        CONFIGURATION_SCHEMA["definitions"]["platform_description_schema"]["required"].append("stats")
    try:
        jsonschema.validate(config, CONFIGURATION_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise jsonschema.ValidationError(f"The configuration is invalid : {exc!s}")

    if run_jobs:
        monitor(update_db=update_db)

        if config.get("PARSE_LOG"):
            access_log_fn = config["DATABASE"]["access_log"]
            route_invocations = {}
            file_checked = 0
            for i in range(0, min(10, LOG_BACKUP_COUNT)):
                fn = access_log_fn + (f".{i}" if i > 0 else "")
                try:
                    route_stats = parse_log(fn)
                    for route, value in route_stats.items():
                        route_invocations[route] = route_invocations.get(route, 0) + value["count"]
                    file_checked += 1
                except IOError:
                    break

            for route, invocs in route_invocations.items():
                if invocs > 0:
                    logger.info("Found %s invocations to route %s in %s log files", invocs, route, file_checked)
                else:
                    logger.warning("Found no invocations to route %s in %s log files", route, file_checked)
            if not route_invocations:
                logger.warning("Found no invocations at all in %s log files", file_checked)
    logger.info("Tests completed!")
