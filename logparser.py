# -- Standard lib ------------------------------------------------------------
import os
import re
import time
import signal
import datetime
import logging
import logging.handlers

# -- 3rd party ---------------------------------------------------------------
import sqlite3

# -- Project specific --------------------------------------------------------
from canarieapi.utility_rest import get_db
from canarieapi.app_object import APP
logger = APP.logger

def rotate_log(filename):
    logger.info('Rotating {0}'.format(filename))

    # Base on a rotation every 10 minutes, if we want to keep 1 day worth of logs we have to keep about 150 of them
    rfh = logging.handlers.RotatingFileHandler(filename, backupCount=150)
    rfh.doRollover()

    pid_file = APP.config['DATABASE']['log_pid']
    logger.info('Asking nginx to reload log file (using pid file : {0}'.format(pid_file))
    try:
        with open(pid_file, "rb") as pid_f:
            pid = pid_f.read()
            logger.info('nginx pid is {0}'.format(int(pid)))
    except IOError:
        # If nginx is not running no needs to force the log reload
        logger.warn('No pid found!')
        return

    # Send SIGUSR1 to nginx to force the log reload
    logger.info('Sending USR1 (to reload log) signal to nginx process')
    os.kill(int(pid), signal.SIGUSR1)
    time.sleep(1)


def parse_log(filename):
    # Load config
    logger.info('Loading configuration')
    routes = APP.config['SERVICES']
    routes.update(APP.config['PLATFORMS'])
    route_stats = {}
    for route in routes:
        route_regex = routes[route]['stats']
        route_stats[route] = dict(method_regex=re.compile(route_regex['method']),
                                  route_regex=re.compile(route_regex['route']),
                                  count=0,
                                  last_access=None)


    # Load access log
    logger.info('Loading log file : {0}'.format(filename))
    log_fmt = '.*\[(?P<datetime>.*)\] "(?P<method>[A-Z]+) (?P<route>/.*) .*'
    log_regex = re.compile(log_fmt)
    log_records = []
    with open(filename, 'r') as f:
        for line in f:
            m = log_regex.match(line)
            if m:
                log_records.append(m.groupdict())

    # Compile stats
    logger.info('Compiling stats from {0} records'.format(len(log_records)))
    for record in log_records:
        for route, value in route_stats.items():
            if value['route_regex'].match(record['route']) and \
               value['method_regex'].match(record['method']):
                value['count'] = value['count'] + 1
                value['last_access'] = record['datetime']
                break

    # Update stats in database
    logger.info('Updating databse')
    with APP.app_context():
        db = get_db()
        for route, value in route_stats.items():
            if not value['count']:
                continue

            logger.info('Adding {0} invocations to route {1}'.format(value['count'], route))

            query = 'insert or replace into stats (route, invocations, last_access) values (' \
                    '?, ' \
                    ' ifnull((select invocations from stats where route=?),0) + ?, ' \
                    '?)'

            # sqlite can take the date as a string as long as it is formatted using ISO-8601
            cur = db.execute(query, [route, route, value['count'], value['last_access']])
            cur.close()
            db.commit()
        db.close()


if __name__ == '__main__':
    access_log_fn = APP.config['DATABASE']['access_log']
    rotate_log(access_log_fn)
    parse_log(access_log_fn + '.1')
    logger.info('Done')