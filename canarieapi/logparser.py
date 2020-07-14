# -- Standard lib ------------------------------------------------------------
import os
import re
import time
import signal
import logging
import logging.handlers
import datetime

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.utility_rest import get_db,is_additional_stats


LOG_BACKUP_COUNT = 150
NGINX_DATE_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

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
    log_fmt = '(?P<sender>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).*\[(?P<datetime>.*)\] "(?P<method>[A-Z]+) (?P<route>/.*) .*'
    log_regex = re.compile(log_fmt)
    log_records = []
    raw_stats = dict()
    print(route_stats)
    with open(filename, 'r') as f:
        for line in f:
            m = log_regex.match(line)
            if m:
                record = m.groupdict()
                process_record(raw_stats,route_stats,record)

    # Generic stats
    logger.info('Compiling stats from {0} records'.format(len(log_records)))
    return route_stats,raw_stats

def process_record(raw_stats,route_stats,record):
    # process record to gather stats
    if ("route" in record) and ("method" in record):
        for route, value in route_stats.items():
            if value['route_regex'].match(record['route']) and \
            value['method_regex'].match(record['method']):
                value['count'] = value['count'] + 1
                value['last_access'] = record['datetime']
                # create additional stats only if required
                if is_additional_stats():
                    raw_key = route + "_" + value["method_regex"].pattern
                    if not raw_key in raw_stats:
                        raw_stats[raw_key] = dict()
                    rm = raw_stats[raw_key]
                    # Update unique visitor values
                    if ("sender" in record) and ("datetime" in record):
                        try:
                            sender = record["sender"]
                            if sender not in rm:
                                rm[sender] = dict()

                            rm[sender]["route"] = route
                            call_dt = datetime.datetime.strptime(record["datetime"],NGINX_DATE_FORMAT)
                            hourly_date = call_dt.replace(minute=0,second=0,microsecond=0)
                            str_hourly_date = str(hourly_date)

                            rm[sender][str_hourly_date] = rm[sender].get(str_hourly_date,0) + 1

                        except Exception as e:
                            # Could not parse nginx log for sender or datetime so skipping it.
                            pass

                break;

def update_db(route_stats,raw_stats=None):
    # Update stats in database
    logger = APP.logger
    logger.info('Updating databse')
    with APP.app_context():
        db = get_db()
        cur = db.cursor()

        # update generic stats
        for route, value in route_stats.items():
            if not value['count']:
                continue

            logger.info('Adding {0} invocations to route {1}'.format(value['count'], route))

            query = 'insert into stats (route, invocations, last_access) values (%s,%s,%s)' \
                    'ON CONFLICT (route) DO UPDATE SET invocations = ' \
                    '(select invocations from stats where route = %s) + EXCLUDED.invocations'

            # postgres can take the date as a string as long as it is formatted using ISO-8601
            cur.execute(query, [route, value['count'], value['last_access'],route])

        # if additional stats
        if is_additional_stats() and raw_stats:
            is_new_ip_query = "select * from ip_details where ip = %s"
            insert_new_ip = "insert into unprocessed_ips (ip) values (%s) ON CONFLICT (ip) DO NOTHING"
            insert_new_raw_stats = "insert into raw_stats (call_date,ip,call_count) " \
                                   "values (%s,%s,%s) ON CONFLICT (call_date,ip) " \
                                   "DO UPDATE SET call_count=(SELECT call_count from raw_stats where call_date= %s AND ip =%s)" \
                                   " + EXCLUDED.call_count"
            db = get_db()
            unique_ips = set()
            for item in raw_stats.values():
                for ip,info in item.items():
                    # add the ip to unprocessed stack if ip has not details
                    if not ip in unique_ips:
                        cur = db.cursor()
                        res = cur.execute(is_new_ip_query,[ip])
                        if cur.rowcount == 0:
                            cur.execute(insert_new_ip,[ip])
                            unique_ips.add(ip)

                        route = info["route"]
                        for date in info.keys():
                            if date != "route":
                                cur.execute(insert_new_raw_stats,[date,ip,info[date],date,ip])

        # update specific call stats:
        cur.execute('insert into cron (job, last_execution) values (\'log\', CURRENT_TIMESTAMP) ON CONFLICT(job) DO UPDATE SET last_execution = CURRENT_TIMESTAMP')
        db.close()

def cron_job():
    logger = APP.logger
    logger.info('Cron job for parsing server log')
    access_log_fn = APP.config['DATABASE']['access_log']
    rotate_log(access_log_fn)
    update_db(*parse_log(access_log_fn + '.1'))
    logger.info('Done')


if __name__ == '__main__':
    cron_job()
