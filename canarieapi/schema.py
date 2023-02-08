# -- Standard lib ------------------------------------------------------------
import json
import os.path

# -- 3rd party ---------------------------------------------------------------
import jsonschema

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.logparser import LOG_BACKUP_COUNT, parse_log
from canarieapi.monitoring import monitor

# The schema that must be respected by the config
with open(os.path.join(os.path.dirname(__file__), "schema.json"), "r") as schema_file:
    CONFIGURATION_SCHEMA = json.load(schema_file)


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
            logger.warning("Found no invocations to route {0} in {1} log files".format(route, file_checked))
    if not route_invocations:
        logger.warning("Found no invocations at all in {0} log files".format(file_checked))
    logger.info("Tests completed!")
