"""
Logger and log utilities for the docserver repo.
"""

import logging
import sys
import traceback

logger = logging.getLogger(str(__name__))

logger.setLevel(logging.getLevelName("INFO"))
formatter = logging.Formatter("%(levelname)s [%(asctime)s] %(message)s",
                              datefmt='%Y-%m-%d %I:%M:%S')

standard_handle = logging.StreamHandler(sys.stdout)
standard_handle.setLevel(logging.DEBUG)
standard_handle.setFormatter(formatter)
logger.addHandler(standard_handle)

error_handle = logging.StreamHandler(sys.stderr)
error_handle.setLevel(logging.WARNING)
error_handle.setFormatter(formatter)
logger.addHandler(error_handle)


def log_exception(raised_exception):
    """Logs the type, message, and traceback of an exception without raising it.

    Args:
        raised_exception: A raised exception.
    """
    error_type = str(type(raised_exception)).replace("<class '", "").replace("'>", "")
    error_message = str(raised_exception)
    error_traceback = str(traceback.format_exc())

    msg = """Error of type: {error_type} raised with error message:
    {error_message}
    
    And traceback:
    {error_traceback}        
    """.format(error_type=error_type,
               error_message=error_message,
               error_traceback=error_traceback)

    logger.error(msg)
