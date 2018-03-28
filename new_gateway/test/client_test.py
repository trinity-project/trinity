# coding: utf-8
import time
import os
# import asyncio
from client import Client


if __name__ == "__main__":
    c = Client()
    addr = ("localhost", 8088)
    c.send(addr, b"pusheof")
    while(True):
        pass