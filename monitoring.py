# -- Standard lib ------------------------------------------------------------
import os
import re
import time
import signal
import datetime
import logging
import logging.handlers
import requests
from requests.exceptions import ConnectionError


# -- 3rd party ---------------------------------------------------------------
import sqlite3

# -- Project specific --------------------------------------------------------
from canarieapi.utility_rest import get_db
from canarieapi.app_object import APP
from canarieapi.status import Status
logger = APP.logger


def monitor():
    # Load config
    logger.info('Loading configuration')
    routes = APP.config['SERVICES']
    routes.update(APP.config['PLATFORMS'])

    logger.info('Checking status of routes...')
    with APP.app_context():
        db = get_db()
        cur = db.cursor()
        query = 'insert or replace into status (route, service, status) values (?, ?, ?)'

        for route in routes:
            for service, test_dic in routes[route]['monitoring'].items():
                status = check_service(request=test_dic['request'],
                                       response=test_dic.get('response', {}))
                logger.info('{0}.{1} : {2}'.format(route, service, Status.pretty_msg(status)))

                cur.execute(query, [route, service, status])

        cur.execute('insert or replace into cron (job, last_execution) values (\'status\', CURRENT_TIMESTAMP)')
        db.commit()
        db.close()


def check_service(request, response):
    default_request = {
        'headers': {},
        'params': None,
        'data': None,
        'json': None,
        'method': 'get',
        'url': 'http://google.com'
    }
    default_request.update(request)

    default_response = {
        'status_code': 200,
        'text': None
    }
    default_response.update(response)
    try:
        r = requests.request(**default_request)
    except ConnectionError as e:
        logger.warn('Cannot reach {0} : {1}'.format(default_request['url'], str(e)))
        return Status.down

    if r.status_code != default_response['status_code']:
        logger.warn('Bad return code from {0} (Expecting {1}, Got {2}'.
                    format(default_request['url'],
                           default_response['status_code'],
                           r.status_code))
        return Status.bad

    if default_response['text']:
        text_regex = re.compile(default_response['text'])
        if not r.text or not text_regex.match(r.text):
            logger.warn('Bad response content from {0} (Expecting : \n{1}\nGot : \n{2}'.
                        format(default_request['url'],
                               default_response['text'],
                               r.text))
            return Status.bad
    return Status.ok


if __name__ == '__main__':
    logger.info('Cron job for monitoring routes status')
    monitor()
    logger.info('Done')
