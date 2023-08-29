import os
import shutil

import jsonschema
import pytest

from canarieapi.schema import validate_config_schema
from tests import config as test_config


@pytest.fixture(autouse=True)
def tmp_config():
    from canarieapi.api import APP

    APP.config.from_object(test_config)

    yield

    tmp_dir = os.path.dirname(test_config.DATABASE["filename"])
    if "tmp" in tmp_dir and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)


def test_validate_error_wrong_schema():
    """
    Ensure the configuration schema is used to validate the application configuration at startup.
    """
    from canarieapi.api import APP

    APP.config.update({
        "SERVICES": {"random": "bad"},
        "PLATFORMS": {"invalid": "error"},
    })

    with pytest.raises(jsonschema.ValidationError):
        validate_config_schema(False, run_jobs=False)


def test_validate_schema_no_parse_logs():
    """
    Ensure the configuration schema is valid when PARSE_LOGS is False and stats are not set.
    """
    from canarieapi.api import APP

    APP.config["PARSE_LOGS"] = False

    for val in APP.config["SERVICES"].values():
        val.pop("stats")

    for val in APP.config["PLATFORMS"].values():
        val.pop("stats")

    validate_config_schema(False, run_jobs=False)
