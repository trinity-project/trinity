# coding: utf-8
import time
import os
from gateway import gateway_singleton
from config import cg_debug

if __name__ == "__main__":
    import logging
    from glog import tcp_logger,wst_logger,rpc_logger
    # logging.basicConfig(level=logging.DEBUG)
    # get_event_loop().set_debug(cg_debug)
    rpc_logger.setLevel(logging.DEBUG)
    tcp_logger.setLevel(logging.DEBUG)
    wst_logger.setLevel(logging.DEBUG)
    try:
        gateway_singleton.start()
    except KeyboardInterrupt:
        gateway_singleton.clearn()
    # except Exception as exc:
    #     pass
    finally:
        gateway_singleton.close()
        # pass