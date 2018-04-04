# coding: utf-8
import time
import os
# from gateway import gateway_singleton, get_event_loop
from new_gateway import gateway_singleton, get_event_loop
from config import cg_debug

if __name__ == "__main__":
    if cg_debug:
        import logging
        from glog import tcp_logger
        # logging.basicConfig(level=logging.DEBUG)
        # get_event_loop().set_debug(cg_debug)
        tcp_logger.setLevel(logging.DEBUG)
    try:
        gateway_singleton.start()
    except Exception as exc:
        # gateway_singleton.clearn()
        raise
    finally:
        # gateway_singleton.close()
        pass