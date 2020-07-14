# -- Standard lib ------------------------------------------------------------
import os
import re
import time
import signal
import logging
import logging.handlers
import time
import datetime
from ipwhois import IPWhois

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.utility_rest import get_db,is_ip_information

# Limit the processing time, to avoid cron job overlaps
MAX_PROCESSING_TIME_IN_SECONDS = 540

def get_ip_info():
    # Load config
    logger = APP.logger
    logger.info('Starting ip information collection')
    with APP.app_context():
        if is_ip_information():
            start = time.time()
            db = get_db()
            db.autocommit = True
            cur = db.cursor()
            cur.execute("select ip from unprocessed_ips")
            all_ips = cur.fetchall()
            cur.close()
            cur = db.cursor()
            ip_details_query = "insert into ip_details(ip,asn,asn_description,asn_country,last_updated)" \
                               "VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"
            for ip_row in all_ips:
                ip = ip_row[0]
                current = time.time()
                if (current - start) > MAX_PROCESSING_TIME_IN_SECONDS:
                    logger.info("Stopped collecting ip information due to time limit.")
                    break
                try:
                    iplooker = IPWhois(ip)
                    ip_stats = iplooker.lookup_whois()
                    now = str(datetime.datetime.now())
                    cur.execute(ip_details_query,[ip,ip_stats['asn'],ip_stats['asn_description']
                        ,ip_stats['asn_country_code'],now])
                except Exception as e:
                    # failure to get information about ip for some reasons
                    cur.execute(ip_details_query, [ip, -1, ""
                        , "  ",now])

                # delete entry from upp details
                cur.execute("delete from unprocessed_ips where ip = %s",[ip])


    logger.info('Done ip information collection')

def cron_job():
    logger = APP.logger
    logger.info('Cron job for getting ip information')
    get_ip_info()
    logger.info('Done')


if __name__ == '__main__':
    cron_job()