import os
import shutil

import jsonschema
import pytest

from canarieapi.schema import validate_config_schema


@pytest.yield_fixture(autouse=True)
def tmp_config():
    from tests import config as test_config

    yield test_config

    tmp_dir = os.path.dirname(test_config.DATABASE["filename"])
    if "tmp" in tmp_dir and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)


def test_validate_error_wrong_schema(tmp_config):  # noqa  # pylint: disable=W0621
    """
    Ensure the configuration schema is used to validate the application configuration at startup.
    """
    from canarieapi.api import APP  # isort: skip  # noqa

    APP.config.update({
        "SERVICES": {"random": "bad"},
        "PLATFORM": {"invalid": "error"},
    })

    with pytest.raises(jsonschema.ValidationError):
        validate_config_schema(False)
