#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_canarieapi
----------------------------------

Tests for `canarieapi` module.
"""
import os
import shutil
import unittest

from flask_webtest import TestApp

from canarieapi.api import APP
from tests import config as test_config


class TestCanarieAPI(unittest.TestCase):

    def setUp(self):
        self.config = test_config
        APP.config.from_object(self.config)
        self.app = APP
        self.web = TestApp(self.app)

    def tearDown(self):
        path = self.app.config.get("DATABASE", {}).get("filename", "")
        dir_path = os.path.dirname(path)
        if path and os.path.isdir(dir_path) and "tmp" in os.path.basename(dir_path):
            shutil.rmtree(dir_path)

    def test_entrypoint_page(self):
        resp = self.web.get("/")
        assert resp.status_code == 200
        assert "Canarie API" in resp.text


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
