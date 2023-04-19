# -- Standard lib ------------------------------------------------------------
import logging
import logging.handlers
import os
import re
import signal
import sqlite3
import time
from typing import Dict, Optional, Union

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.utility_rest import get_db, retry_db_error_after_init

# -- 3rd party ---------------------------------------------------------------
from dateutil.parser import parse as dt_parse

LOG_BACKUP_COUNT = 150

RouteStatistics = Dict[str, Dict[str, Union[str, int]]]

def parse_log(filename: str, database: Optional[sqlite3.Connection] = None) -> RouteStatistics:
    # Load config
    logger = APP.logger
    logger.info("Loading configuration")
    config = APP.config
    srv_stats = {route: config["SERVICES"][route]["stats"] for route in config["SERVICES"]}
    pf_stats = {route: config["PLATFORMS"][route]["stats"] for route in config["PLATFORMS"]}
    all_stats = srv_stats
    all_stats.update(pf_stats)

    route_stats = {}
    for route in all_stats:
        route_regex = all_stats[route]
        try:
            route_stats[route] = {
                "method_regex": re.compile(route_regex["method"]),
                "route_regex": re.compile(route_regex["route"]),
                "count": 0,
                "last_access": None,
            }
        except Exception:
            logger.error("Exception occurs while trying to compile regex of %s", route)
            raise

    # get the last entry from the logs in order to not duplicate entries if the same log file is read multiple times
    with APP.app_context():
        db = database or get_db()
        cur = db.cursor()
        cur.execute('select last_access from stats order by last_access desc limit 1')
        records = cur.fetchone()
        if records:
            last_access = dt_parse(records[0][0])
        else:
            last_access = None

    # Load access log
    logger.info("Loading log file : %s", filename)
    log_regex = re.compile(r".*\[(?P<datetime>.*)\] \"(?P<method>[A-Z]+) (?P<route>/.*) .*")  # pylint: disable=C4001
    log_records = []
    with open(filename, mode="r", encoding="utf-8") as f:
        for line in f:
            match = log_regex.match(line)
            if match:
                records = match.groupdict()
                if last_access is None or dt_parse(records["datetime"]) > last_access:
                    log_records.append(records)

    # Compile stats
    logger.info("Compiling stats from %s records", len(log_records))
    for record in log_records:
        for route, value in route_stats.items():
            if value["route_regex"].match(record["route"]) and \
               value["method_regex"].match(record["method"]):
                value["count"] = value["count"] + 1
                value["last_access"] = record["datetime"]
                break
    return route_stats


@retry_db_error_after_init
def update_db(route_stats: RouteStatistics, database: Optional[sqlite3.Connection] = None) -> None:
    # Update stats in database
    logger = APP.logger
    logger.info("Updating database")
    with APP.app_context():
        db = database or get_db()
        cur = db.cursor()

        for route, value in route_stats.items():
            if not value["count"]:
                continue

            logger.info("Adding %s invocations to route %s", value["count"], route)

            query = (
                "insert or replace into stats (route, invocations, last_access) values ("
                "?, "
                " ifnull((select invocations from stats where route=?),0) + ?, "
                "?)"
            )

            # sqlite can take the date as a string as long as it is formatted using ISO-8601
            cur.execute(query, [route, route, value["count"], value["last_access"]])

        cur.execute("insert or replace into cron (job, last_execution) values ('log', CURRENT_TIMESTAMP)")
        db.commit()
        db.close()


def cron_job() -> None:
    if APP.config.get("PARSE_LOGS", True):
        logger = APP.logger
        logger.info("Cron job for parsing server log")
        access_log_fn = APP.config["DATABASE"]["access_log"]
        update_db(parse_log(access_log_fn))
        logger.info("Done")


if __name__ == "__main__":
    cron_job()
