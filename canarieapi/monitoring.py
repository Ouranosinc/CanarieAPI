# -- Standard lib ------------------------------------------------------------
import re
from typing import Dict, Optional, Tuple, Union
from typing_extensions import Literal, NotRequired, Required, TypedDict

# -- 3rd party modules -------------------------------------------------------
import requests
from requests.exceptions import ConnectionError

# -- Project specific --------------------------------------------------------
from canarieapi.app_object import APP
from canarieapi.status import Status
from canarieapi.utility_rest import JSON, get_db

RequestConfig = TypedDict("RequestConfig", {
    "url": Required[str],
    "method": NotRequired[Literal[
        "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE",
        "get", "options", "head", "post", "put", "patch", "delete",
    ]],
    "params": NotRequired[Optional[Union[str, Dict[str, str]]]],
    "headers": NotRequired[Dict[str, str]],
    "json": NotRequired[Optional[JSON]],
    "data": NotRequired[Optional[str]],
}, total=False)
ResponseConfig = TypedDict("ResponseConfig", {
    "status_code": NotRequired[Optional[int]],
    "text": NotRequired[Optional[str]],
}, total=True)


def monitor(update_db: bool = True) -> None:
    # Load config
    logger = APP.logger
    config = APP.config
    logger.info("Loading configuration")
    srv_mon = {route: config["SERVICES"][route]["monitoring"] for route in config["SERVICES"]}
    pf_mon = {route: config["PLATFORMS"][route]["monitoring"] for route in config["PLATFORMS"]}
    all_mon = srv_mon
    all_mon.update(pf_mon)

    logger.info("Checking status of routes...")
    with APP.app_context():
        if update_db:
            db = get_db()
            cur = db.cursor()
            query = "insert or replace into status (route, service, status, message) values (?, ?, ?, ?)"

        for route in all_mon:
            for service, test_dic in all_mon[route].items():
                try:
                    status, message = check_service(request=test_dic["request"],
                                                    response=test_dic.get("response", {}))
                except Exception:
                    logger.error("Exception occurs while trying to check status of {0}.{1}".format(route, service))
                    raise
                logger.info("{0}.{1} : {2}".format(route, service, Status.pretty_msg(status)))

                if update_db:
                    cur.execute(query,
                                [route, service, status, (message[0:253] + "...") if len(message) > 256 else message])

        if update_db:
            cur.execute('insert or replace into cron (job, last_execution) values (\'status\', CURRENT_TIMESTAMP)')
            db.commit()
            db.close()


def check_service(request: RequestConfig, response: ResponseConfig) -> Tuple[Status, str]:
    default_request: RequestConfig = {
        "headers": {},
        "params": None,
        "data": None,
        "json": None,
        "method": "get",
        "url": "http://google.com"
    }
    default_request.update(request)

    default_response: ResponseConfig = {
        "status_code": 200,
        "text": None
    }
    default_response.update(response)

    logger = APP.logger
    try:
        r = requests.request(**default_request)
    except ConnectionError as e:
        message = "Cannot reach {0} : {1}".format(default_request["url"], str(e))
        logger.warning(message)
        return Status.down, message

    if r.status_code != default_response["status_code"]:
        message = "Bad return code from {0} (Expecting {1}, Got {2}".format(
            default_request["url"],
            default_response["status_code"],
            r.status_code)
        logger.warning(message)
        return Status.bad, message

    if default_response["text"]:
        text_regex = re.compile(default_response["text"])
        if not r.text or not text_regex.match(r.text):
            message = "Bad response content from {0} (Expecting : \n{1}\nGot : \n{2}".format(
                default_request["url"],
                default_response["text"],
                r.text)
            logger.warning(message)
            return Status.bad, message
    return Status.ok, ""


def cron_job() -> None:
    logger = APP.logger
    logger.info("Cron job for monitoring routes status")
    monitor()
    logger.info("Done")


if __name__ == "__main__":
    cron_job()
