import logging
from datetime import datetime


# add the handlers to the logger


def get_logger(caller_name):
    logger = logging.getLogger(caller_name)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    launch_time = datetime.now()
    fh = logging.FileHandler('{}.log'.format(launch_time.date()))
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger

def fatal(*msg):
    logger = logging.getLogger('failed_events')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    launch_time = datetime.now()
    fh = logging.FileHandler('{}_failed_events.log'.format(launch_time.date()))
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.error(' '.join([m for m in msg]))