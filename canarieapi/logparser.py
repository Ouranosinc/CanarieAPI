# -- Standard lib ------------------------------------------------------------
import os
import re
import time
import signal
import logging
import logging.handlers


# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.utility_rest import get_db


LOG_BACKUP_COUNT = 150


def rotate_log(filename):
    logger = APP.logger
    logger.info('Rotating {0}'.format(filename))

    # Base on a rotation every 10 minutes, if we want to keep 1 day worth of logs we have to keep about 150 of them
    rfh = logging.handlers.RotatingFileHandler(filename, backupCount=LOG_BACKUP_COUNT)
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
    logger = APP.logger
    logger.info('Loading configuration')
    config = APP.config
    srv_stats = {route : config['SERVICES'][route]['stats'] for route in config['SERVICES']}
    pf_stats = {route: config['PLATFORMS'][route]['stats'] for route in config['PLATFORMS']}
    all_stats = srv_stats
    all_stats.update(pf_stats)

    route_stats = {}
    for route in all_stats:
        route_regex = all_stats[route]
        try:
            route_stats[route] = dict(method_regex=re.compile(route_regex['method']),
                                      route_regex=re.compile(route_regex['route']),
                                      count=0,
                                      last_access=None)
        except:
            logger.error('Exception occurs while trying to compile regex of {0}'.format(route))
            raise

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
    return route_stats


def update_db(route_stats):
    # Update stats in database
    logger = APP.logger
    logger.info('Updating databse')
    with APP.app_context():
        db = get_db()
        cur = db.cursor()

        for route, value in route_stats.items():
            if not value['count']:
                continue

            logger.info('Adding {0} invocations to route {1}'.format(value['count'], route))

            query = 'insert or replace into stats (route, invocations, last_access) values (' \
                    '?, ' \
                    ' ifnull((select invocations from stats where route=?),0) + ?, ' \
                    '?)'

            # sqlite can take the date as a string as long as it is formatted using ISO-8601
            cur.execute(query, [route, route, value['count'], value['last_access']])

        cur.execute('insert or replace into cron (job, last_execution) values (\'log\', CURRENT_TIMESTAMP)')
        db.commit()
        db.close()


def cron_job():
    logger = APP.logger
    logger.info('Cron job for parsing server log')
    access_log_fn = APP.config['DATABASE']['access_log']
    rotate_log(access_log_fn)
    update_db(parse_log(access_log_fn + '.1'))
    logger.info('Done')


if __name__ == '__main__':
    cron_job()
