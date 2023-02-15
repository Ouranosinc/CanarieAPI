import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from canarieapi.api import APP as application  # noqa  # pylint: disable=C0413,W0611
