import os
import sys
r_path = os.getcwd()
print(r_path)
sys.path.append(r_path)
import logging

from glog import tcp_logger
# set log output min level
tcp_logger.setLevel(logging.DEBUG)
tcp_logger.debug("this is debug info")
tcp_logger.error("this is error info")
tcp_logger.warn("this is warning info")

try:
    3/0
except:
    tcp_logger.exception("this is an exception message")
