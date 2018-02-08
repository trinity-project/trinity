# --*-- coding : utf-8 --*--
import logging
import os, sys
BASE_LOG_DIR = os.getcwd()
class cfg(object):
    RELEASE_MODE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'release': {
            'format': '%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(message)s'
        },
        'debug': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(filename)s %(module)s %(funcName)s %(lineno)d: %('
                      'message)s'
            # INFO 2016-09-03 16:25:20,067 /home/ubuntu/mysite/views.py views.py views get 29: some info...
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'debug'
        },
        'file': {
            'level': 'DEBUG',
            # 'class': 'logging.FileHandler',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_LOG_DIR,
            'formatter': 'release',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10
        },
        'mail_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, 'Tersy2-mail.log'),
            'formatter': 'release',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10
        },
    },
    'loggers': {
        'logger': {
            'handlers': ['file'] if cfg.RELEASE_MODE else ['file', 'console'],
            'level': 'INFO' if cfg.RELEASE_MODE else 'DEBUG',
        },
        'email_logger': {
            'handlers': ['mail_file'],
            'level': 'INFO'
        },
    },
}

def set_log_file(filename):
    log_dir = LOGGING['handlers']['file']['filename']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, 'Tersy2-' + filename.lower() + '.log')
    LOGGING['handlers']['file']['filename'] = log_path

from logging.handlers import RotatingFileHandler


LOG = logging.getLogger('logger')
set_log_file('tnc')

def init_logger():
    log_dir = BASE_LOG_DIR
    logfile = 'Tersy2-ctl-helper.log'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    LOG.name = logfile
    level = getattr(logging, 'DEBUG')
    print (level)
    LOG.setLevel(level)
    file_handler = RotatingFileHandler(log_dir + os.sep + logfile, 'a', 5 * 1024 * 1024, 10)
    file_handler.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    LOG.addHandler(file_handler)
    LOG.addHandler(stream_handler)


init_logger()


LOG.info('test')
LOG.debug('ok')
