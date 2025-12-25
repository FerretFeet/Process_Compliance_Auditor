import logging
import os

from shared.services import logger
from shared.utils import project_root

from tests.fixtures import * # noqa

def pytest_configure(config):
    # Modify logger to keep log files clean of test noise.
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)

    test_log_path = project_root / 'logs' / 'test.log'

    test_handler = logging.FileHandler(test_log_path)
    test_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    test_handler.setLevel(logging.DEBUG)

    logger.addHandler(test_handler)


