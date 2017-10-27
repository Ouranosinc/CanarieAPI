# -- Standard lib ------------------------------------------------------------
import re
import requests
from requests.exceptions import ConnectionError

# -- Project specific --------------------------------------------------------
from utility_rest import get_db
from status import Status
from app_object import APP


def monitor(update_db=True):
    # Load config
    logger = APP.logger
    config = APP.config
    logger.info('Loading configuration')
    srv_mon = {route : config['SERVICES'][route]['monitoring'] for route in config['SERVICES']}
    pf_mon = {route: config['PLATFORMS'][route]['monitoring'] for route in config['PLATFORMS']}
    all_mon = srv_mon
    all_mon.update(pf_mon)

    logger.info('Checking status of routes...')
    with APP.app_context():
        if update_db:
            db = get_db()
            cur = db.cursor()
            query = 'insert or replace into status (route, service, status) values (?, ?, ?)'

        for route in all_mon:
            for service, test_dic in all_mon[route].items():
                try:
                    status = check_service(request=test_dic['request'],
                                           response=test_dic.get('response', {}))
                except:
                    logger.error('Exception occurs while trying to check status of {0}.{1}'.format(route, service))
                    raise
                logger.info('{0}.{1} : {2}'.format(route, service, Status.pretty_msg(status)))

                if update_db:
                    cur.execute(query, [route, service, status])

        if update_db:
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

    logger = APP.logger
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


def cron_job():
    logger = APP.logger
    logger.info('Cron job for monitoring routes status')
    monitor()
    logger.info('Done')


if __name__ == '__main__':
    cron_job()