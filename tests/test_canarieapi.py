#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `canarieapi` module.
"""
import os
import shutil
import unittest

import mock
import responses
from flask_webtest import TestApp

from canarieapi.logparser import cron_job as cron_job_logparse
from canarieapi.monitoring import cron_job as cron_job_monitor
from tests import config as test_config


class TestCanarieAPI(unittest.TestCase):
    app = None
    config = None

    @classmethod
    def setUpClass(cls):
        cls.config = test_config

        # important not to import APP at the top nor before config/env were applied
        # otherwise, configuration is loaded immediately and raises an error due to missing directory to store DB file
        cfg_path = os.path.abspath(test_config.__file__)
        try:
            with mock.patch.dict("os.environ", {"CANARIE_API_CONFIG_FN": cfg_path, "CANARIE_API_SKIP_CHECK": "true"}):
                from canarieapi.api import APP  # isort: skip  # noqa
        except ImportError:
            print(f"Failed loading APP with test config. Ensure [CANARIE_API_CONFIG_FN={cfg_path}] is set!")
            raise

        APP.config.from_object(cls.config)

        # setup monitored apps
        for i, (_, cfg) in enumerate(APP.config["SERVICES"].items()):
            port = 6000 + i
            url = f"http://localhost:{port}/"
            cfg["monitoring"]["Component"]["request"]["url"] = url
            responses.get(url, json={}, status=200)  # mock their response
            for req in cfg["redirect"]:
                cfg["redirect"][req] = f"{url.rstrip('/')}/{req}"  # not called, just set for compare

        cls.app = APP
        cls.web = TestApp(cls.app)

        responses.start()  # mock for monitors

        # trigger cron updates immediately to generate status update entries
        # these should end up calling the above monitored apps
        cron_job_logparse()
        cron_job_monitor()

    @classmethod
    def tearDownClass(cls):
        path = cls.app.config.get("DATABASE", {}).get("filename", "")
        dir_path = os.path.dirname(path)
        if path and os.path.isdir(dir_path) and "tmp" in os.path.basename(dir_path):
            shutil.rmtree(dir_path)

    def test_entrypoint_page(self):
        resp = self.web.get("/")
        assert resp.status_code == 200
        assert all(info in resp.text for info in ["Canarie API", "Platforms", "Services"])
        assert all(name in resp.text for name in self.app.config["SERVICES"])

    def test_extern_http_error(self):
        from canarieapi.api import HANDLED_HTML_ERRORS

        for code in HANDLED_HTML_ERRORS:
            resp = self.web.get(f"/{code}", expect_errors=True)
            assert resp.status_code == code

    def test_test_endpoint(self):
        resp = self.web.get("/test", params={"f": "json"})
        while 300 < resp.status_code < 310:
            resp = resp.follow()
        assert resp.status_code == 200
        assert "Platforms" in resp.json
        assert "Services" in resp.json
        assert all(svc in resp.json["Services"] for svc in self.app.config["SERVICES"])

    def test_service_info_json(self):
        name = list(self.app.config["SERVICES"])[0]
        resp = self.web.get(f"/{name}/service/info", params={"f": "json"})
        assert resp.status_code == 200

        fields = [
            "category",
            "institution",
            "name",
            "releaseTime",
            "researchSubject",
            "supportEmail",
            "synopsis",
            "tags",
            "version",
        ]
        assert all(field in resp.json for field in fields)
        assert all(isinstance(resp.json[field], str) and resp.json[field] for field in set(fields) - {"tags"})
        assert isinstance(resp.json["tags"], list) and all(isinstance(tag, str) for tag in resp.json["tags"])

    def test_service_status_page(self):
        name = list(self.app.config["SERVICES"])[0]
        resp = self.web.get(f"/{name}/service/status")
        assert resp.status_code == 200
        assert name in resp.text
        assert "Never" not in resp.text  # if cron update did not work
        assert "Down" not in resp.text   # various keywords if error from monitored app
        assert "Bad" not in resp.text
        assert "Ok" in resp.text  # monitored app reached successfully with HTTP OK 200 returned

    def test_service_status_json_query_string(self):
        name = list(self.app.config["SERVICES"])[0]
        resp = self.web.get(f"/{name}/service/status", params={"f": "json"})
        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        assert resp.json["Component"] == "Ok"
        assert resp.json["lastStatusUpdate"] != "Never"

    def test_service_status_json_accept_header(self):
        name = list(self.app.config["SERVICES"])[0]
        resp = self.web.get(f"/{name}/service/status", headers={"Accept": "application/json"})
        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        assert resp.json["Component"] == "Ok"
        assert resp.json["lastStatusUpdate"] != "Never"

    def test_service_stats_page(self):
        name = list(self.app.config["SERVICES"])[0]
        resp = self.web.get(f"/{name}/service/stats")
        assert resp.status_code == 200
        assert resp.content_type == "text/html"
        assert f"Service: {name}" in resp.text
        assert all(
            field in resp.text
            for field in ["invocations", "lastReset", "monitoring"]
        )

    def test_service_stats_json(self):
        name = list(self.app.config["SERVICES"])[0]
        resp = self.web.get(f"/{name}/service/stats", params={"f": "json"})
        assert resp.status_code == 200
        assert all(
            field in resp.json
            for field in ["invocations", "lastReset", "monitoring"]
        )

    def test_service_redirect_json(self):
        name = list(self.app.config["SERVICES"])[0]
        cfg = self.app.config["SERVICES"][name]
        url = cfg["monitoring"]["Component"]["request"]["url"]
        resp = self.web.get(f"/{name}/service/doc", params={"f": "json"})
        assert resp.status_code == 302, "Expect redirect request to the service's doc redirect endpoint"
        assert resp.location == f"{url.rstrip('/')}/doc"


if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())
