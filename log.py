import logging

import sys


def create_logger(filename=None, level=logging.DEBUG):
    """
    Create Logger with 2 Handlers (Stream with level DEBUG and FileHandler with level ERROR)
    :return: logger
    """

    logger = logging.getLogger('A')
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(fmt)
    stream_handler.setLevel(level)
    logger.addHandler(stream_handler)

    if filename is not None:
        file_handler = logging.FileHandler(filename=filename)
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger
