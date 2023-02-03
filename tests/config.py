import copy
import os
import tempfile

from canarieapi.default_configuration import *  # noqa  # pylint: ignore=W0401,W0614  # import all to mimic config

# flake8: noqa

# overrides for tests
db_dir = tempfile.mkdtemp(prefix="tmp")
DATABASE["filename"] = os.path.join(db_dir, "stats.db")
DATABASE["access_log"] = os.path.join(db_dir, "nginx.log")
DATABASE["log_pid"] = os.path.join(db_dir, "nginx.pid")

TEST_SERVICE = list(SERVICES)[0]
TEST_SERVICE_CONFIG = SERVICES.pop(TEST_SERVICE)
SERVICES = {
    "test-service-1": copy.deepcopy(TEST_SERVICE_CONFIG),
    "test-service-2": copy.deepcopy(TEST_SERVICE_CONFIG),
}
for name, svc in SERVICES.items():
    svc["info"]["name"] = name
