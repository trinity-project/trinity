# coding: utf-8
import time
from datetime import datetime

class Statistics:
    def __init__(self):
        self.stati_tcp = Count_Tcp()
        self.stati_wsocket = Count_Wsocket()
        self.stati_http = Count_Http()

class Count:
    def __init__(self):
        # self.send_totals = 0
        # self.rev_totals = 0
        self.rev_invalid_times = 0
        self.close_times = 0
        self.exc_close_times = 0
        self.rev_split_data_totals = []
        self.rev_data_split_times = len(self.rev_split_data_totals)

class Count_Tcp(Count):
    def __init__(self):
        super().__init__()

class Count_Wsocket(Count):
    def __init__(self):
        super().__init__()

class Count_Http:
    def __init__(self):
        self.send_times = 0
        self.rev_times = 0
        self.rev_invalid_times = 0
        self.send_total = []

def get_timestamp(with_strf=None):
    if not with_strf:
        return time.time()
    else:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")