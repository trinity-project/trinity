# --*-- coding : utf-8 --*--
"""Author: Trinity Core Team

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import logging
import os
from logging.handlers import RotatingFileHandler
BASE_LOG_DIR = os.getcwd()


class Cfg(object):
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
        }
    },
    'loggers': {
        'logger': {
            'handlers': ['file'] if Cfg.RELEASE_MODE else ['file', 'console'],
            'level': 'INFO' if Cfg.RELEASE_MODE else 'DEBUG',
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
    log_path = os.path.join(log_dir, 'test-' + filename.lower() + '.log')
    LOGGING['handlers']['file']['filename'] = log_path


LOG = logging.getLogger('logger')
set_log_file('tnc')


def init_logger():
    log_dir = BASE_LOG_DIR
    logfile = 'test.log'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    LOG.name = logfile
    level = getattr(logging, 'DEBUG')
    print(level)
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
