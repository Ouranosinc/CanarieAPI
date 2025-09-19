#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3

from canarieapi.utility_rest import init_db
from canarieapi.logparser import parse_log


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_parse_log_datetime_tz(tmp_path, tmp_config):
    from canarieapi.api import APP

    db_path = tmp_path / "test.db"
    APP.config.update({
        "SERVICES": {
            "test-service": {"stats": {"method": "GET", "route": "/api/.*"}},
            "other-service": {"stats": {"method": "POST", "route": "/api/other"}},
        },
        "PLATFORMS": {},
        "DATABASE": {
            "filename": str(db_path),
            "access_log": str(tmp_path / "access.log"),
        },
    })
    APP.logger = DummyLogger()

    with APP.app_context():
        conn = sqlite3.connect(db_path)
        init_db(conn)
        conn.execute("INSERT INTO stats (last_access) VALUES (?)", ("2023-09-18T12:00:00",))
        conn.commit()

    # Create a log file with a mix of tz-aware and tz-naive datetimes for both services
    log_content = "".join([
        '[2023-09-18T13:00:00+00:00] "GET /api/test HTTP/1.1" 200 1234\n',  # tz-aware, test-service
        '[2023-09-18T14:00:00] "GET /api/test HTTP/1.1" 200 1234\n',         # tz-naive, test-service
        '[2023-09-18T15:00:00+00:00] "POST /api/other HTTP/1.1" 200 5678\n', # tz-aware, other-service
        '[2023-09-18T16:00:00] "POST /api/other HTTP/1.1" 200 5678\n',        # tz-naive, other-service
        '[2023-09-18T17:00:00+00:00] "GET /api/test HTTP/1.1" 200 1234\n',   # tz-aware, test-service (latest)
        '[2023-09-18T18:00:00] "POST /api/other HTTP/1.1" 200 5678\n',        # tz-naive, other-service (latest)
    ])
    log_file = tmp_path / "access.log"
    log_file.write_text(log_content)

    # Run parse_log and check that the log entries are counted for both services
    stats = parse_log(str(log_file), database=conn)
    assert stats["test-service"]["count"] == 3
    assert stats["test-service"]["last_access"] == "2023-09-18T17:00:00+00:00"
    assert stats["other-service"]["count"] == 3
    assert stats["other-service"]["last_access"] == "2023-09-18T18:00:00"

    conn.close()
    os.remove(db_path)
    os.remove(log_file)
