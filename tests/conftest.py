import os
import shutil
import pytest

from tests import config as test_config


@pytest.fixture()
def tmp_config():
    from canarieapi.api import APP

    APP.config.from_object(test_config)

    yield

    tmp_dir = os.path.dirname(test_config.DATABASE["filename"])
    if "tmp" in tmp_dir and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
