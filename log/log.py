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
import os
import logging.config
from trinity import __os_platform__, __running_mode__
LogDataDir = os.path.join(os.path.dirname(__file__),"log")
if not os.path.exists(LogDataDir):
    os.makedirs(LogDataDir)
LOG = logging.getLogger('logger')
# log configuration parts
if __os_platform__ in ['LINUX', 'DARWIN']:
    TRINITY_LOG_PATH = os.path.join(LogDataDir,"trinity.log")
else:
    TRINITY_LOG_PATH = os.getcwd().split(os.sep)[0]+os.sep+'temp'

log_settings = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'release': {
            'format': '[%(asctime)s] %(pathname)s line %(lineno)d %(levelname)s :%(message)s'
        },
        'debug': {
            'format': '[%(asctime)s] %(pathname)s line %(lineno)d %(levelname)s :%(message)s'
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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '{}{}{}'.format(TRINITY_LOG_PATH, os.sep, 'trinity.log'),
            'formatter': 'release',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10
        }
    },
    'loggers': {
        'logger': {
            'handlers': ['file'] if __running_mode__ else ['file', 'console'],
            'level': 'INFO' if __running_mode__ else 'DEBUG',
        }
    },
}


def init_logger(log_path = None, file_name=None):
    init_log_path = log_path if log_path else TRINITY_LOG_PATH
    init_filename = file_name if file_name else 'trinity.log'

    # create the log path
    if not os.path.exists(init_log_path):
        os.mkdir(init_log_path)

    # load logger configuration
    log_settings['handlers']['file']['filename'] = '{}{}{}'.format(init_log_path, os.sep, init_filename)
    logging.config.dictConfig(log_settings)

init_logger()
