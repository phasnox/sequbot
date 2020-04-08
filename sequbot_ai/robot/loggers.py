import logging
import os
import sys


LOG_DIR  = '/var/log/sequbot/{}/'
LOGGERS  = ['robot_hive', 'instagram_hack_api', 'automata', 'aimodels', 'social_interface']
HANDLERS = {}
LEVEL    = logging.DEBUG

# Formatter
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s')


def get_handlers(process_name):
    log_dir = LOG_DIR.format(process_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    info_filepath = log_dir + 'info.log'
    info = logging.handlers.RotatingFileHandler(info_filepath, maxBytes=400000, backupCount=5)
    info.setLevel(LEVEL)
    info.setFormatter(formatter)

    error_filepath = log_dir + 'error.log'
    error = logging.handlers.RotatingFileHandler(error_filepath, maxBytes=400000, backupCount=5)
    error.setLevel(logging.ERROR)
    error.setFormatter(formatter)

    return info, error

def add_handlers(process_name):
    info, error = get_handlers(process_name)
    for logger_name in LOGGERS:
        logger = logging.getLogger(logger_name)
        logger.setLevel(LEVEL)
        logger.addHandler(info)
        logger.addHandler(error)
        logger.propagate = False

    HANDLERS[process_name] = (info, error)

def handle_uncaught(logger):
    def fn(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))
    return fn

def get_logger(name):
    info, error = get_handlers(name)
    logger = logging.getLogger(name)
    logger.setLevel(LEVEL)
    logger.addHandler(info)
    logger.addHandler(error)
    # Adds logging for uncaught errors
    sys.excepthook = handle_uncaught(logger)
    return logger

def remove_handlers(name):
    info, error = HANDLERS.get(name, (None, None))
    if info is None or error is None:
        return
    for logger_name in LOGGERS:
        logger = logging.getLogger(logger_name)
        logger.removeHandler(info)
        logger.removeHandler(error)

