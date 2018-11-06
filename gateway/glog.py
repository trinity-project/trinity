# coding: utf-8
import logging
import logging.handlers
import sys, os
from config import cg_debug
"""
loggers for gateway
"""
class _NoErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR
        

rpc_logger = logging.getLogger("RPC")
tcp_logger = logging.getLogger("TCP")
wst_logger = logging.getLogger("WST")
gw_logger = logging.getLogger("CMN")

_formatter = logging.Formatter('[%(name)s]: %(asctime)s %(levelname)-8s: %(message)s')


if cg_debug:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(_formatter)

    rpc_logger.addHandler(console_handler)
    tcp_logger.addHandler(console_handler)
    wst_logger.addHandler(console_handler)
    gw_logger.addHandler(console_handler)

# default: write the logs to the files
if not os.path.exists('./temp'):
    os.makedirs('./temp')

access_file_handler = logging.handlers.TimedRotatingFileHandler('./temp/gateway.log', when='d')

# set log handler record level and filter
access_file_handler.setLevel(logging.DEBUG)
# access_file_handler.addFilter(_NoErrorFilter())

# set log handler format
access_file_handler.setFormatter(_formatter)

rpc_logger.setLevel(logging.DEBUG)
tcp_logger.setLevel(logging.DEBUG)
wst_logger.setLevel(logging.DEBUG)
gw_logger.setLevel(logging.DEBUG)

rpc_logger.addHandler(access_file_handler)

tcp_logger.addHandler(access_file_handler)

wst_logger.addHandler(access_file_handler)

gw_logger.addHandler(access_file_handler)
