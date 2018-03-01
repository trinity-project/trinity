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
import gevent
import requests
from gevent.queue import Queue
from gevent.threading import Lock
from gevent.event import Event
from logzero import logger
from sqlalchemy import or_
from datetime import datetime

from configure import Configure
from channel_manager.state import ChannelDatabase, Session
from channel_manager.channel import State
from channel_manager.manager import depositin, depoistout


class NodeBApi(object):
    def __init__(self):
        # NODE-B URL
        nodeb_net_port = os.getenv('NODEB_NET_PORT')
        if nodeb_net_port:
            self.nodeb_api_uri = Configure["NodeBNet"].replace('21332', str(nodeb_net_port))
        else:
            self.nodeb_api_uri = Configure["NodeBNet"]

    def get_channel_state_from_nodeb(self, data=None):
        """

        :return:
        """
        request_data = {}
        if data:
            request_data.update({'jsonrpc': '2.0',
                                 'method': 'confirmTx',
                                 'params': [data],
                                 'id': 1})

            return requests.post(self.nodeb_api_uri, json=request_data).json()

        return None


class MonitorDaemon(object):
    """
    Monitor Thread set to handle the transaction states from the trinity networks.
    """
    def __init__(self):
        self.register_lock = Lock()
        self.spawn_signal = Event()
        self.__t_reg = {}

        # set the worker timeout (unit: second)
        self.main_timeout = 1
        self.worker_timeout = 1

        # record the mapping relationship between tx_id and channel_name
        self.tx_id_channel_map = {}

        #
        self.nodeb_api = NodeBApi()

        # update channel api
        self.deposit_action = {State.OPEN:depositin, State.SETTLED:depoistout}

    def worker(self, callback, *args, **kwargs):
        """
        Worker to handler the each response from the NODE-B
        :param callback: The real handler called by worker.
        :param args:
        :param kwargs:
        :return:
        """
        transport = self.__register_transport(callback.__name__)
        if not transport:
            logger.info('No monitor worker thread is created. Channel state will never be updated.')
            return

        while True:
            try:
                task = transport.get(timeout=self.worker_timeout)
                if task:
                    callback(task)
            except Exception as e:
                # Never run here.
                logger.error('Exception occurred in the worker thread. exceptions: {}'.format(e))

            gevent.sleep(0.5)

        return

    def daemon_monitor_timer_event(self, interval = 10):
        self.spawn_signal.clear()
        self.spawn_signal.wait(5)
        if self.spawn_signal.is_set():
            logger.info('Start the Monitor timer event.')
        else:
            logger.info('Why no transport is registered????')
            return

        # timer event to handle the response from the NODE-B
        while True:
            try:
                start_time = datetime.now()
                self.confirm_channel_state(self.all_opening_channels)
                self.confirm_channel_state(self.all_settling_channels, 'settled')

                # calculate the total seconds
                total_seconds = (datetime.now()-start_time).total_seconds()
                if interval > total_seconds:
                    gevent.sleep(interval - total_seconds)
                else:
                    # sleep 500 ms
                    gevent.sleep(0.5)
            except Exception as e:
                logger.error('exception info: {}'.format(e))
                gevent.sleep(interval)

        # clear the spawn signal. should never run here.
        self.spawn_signal.clear()

        # need delete the resources here ??????

        return

    def confirm_channel_state(self, channel_set, expected_state = 'open', count_per_second = 100):
        """

        :param channel_set:
        :param count_per_second:
        :return:
        """
        if not channel_set:
            return

        # parse the all channels from the channel sets
        total_channels = len(channel_set)
        send_loop = total_channels // count_per_second
        left_chan = total_channels % count_per_second

        # handle the left channels
        if 0 != left_chan:
            tx_id_list = list()
            for ch in channel_set[send_loop*count_per_second::]:
                tx_id_list.append(ch.tx_id)
                self.tx_id_channel_map.update({ch.tx_id: ch.channel_name})

            # post data to the NODE-B
            response = self.nodeb_api.get_channel_state_from_nodeb(data = list(set(tx_id_list)))
            self.add_task(task={expected_state.lower():response})

        # handle the request wrapped by count_per_second
        for loop_index in range(send_loop):
            start_index = loop_index * count_per_second
            tx_id_list = list()
            for ch in channel_set[start_index:start_index+count_per_second:]:
                tx_id_list.append(ch.tx_id)
                self.tx_id_channel_map.update({ch.tx_id: ch.channel_name})

            response = self.nodeb_api.get_channel_state_from_nodeb(data = list(set(tx_id_list)))
            self.add_task(task={expected_state.lower(): response})

        return

    def update_channel(self, task):
        if not task:
            return

        if task.get('open'):
            tx_id_dict = task.get('open')
            expected_state = State.OPEN
        elif task.get('settled'):
            tx_id_dict = task.get('settled')
            expected_state = State.SETTLED
        else:
            logger.info('unknown expected state of channels')
            return

        for tx_id, status in tx_id_dict.items():
            if status is True:
                channel_set = Session.query(ChannelDatabase).filter(
                    ChannelDatabase.channel_name == self.tx_id_channel_map[tx_id]).first()
                if channel_set:
                    self.deposit_action[expected_state](channel_set.sender, 0)
                    self.deposit_action[expected_state](channel_set.receiver, 0)

    def add_task(self, task):
        tid_list = list(self.__t_reg.keys())
        transport = self.__t_reg[tid_list[0]]
        transport.add_task(task)

    @property
    def all_opening_channels(self):
        # get all of the opening channels
        channel_set = Session.query(ChannelDatabase).filter(or_(ChannelDatabase.state == State.OPENING,
                                                                ChannelDatabase.state == State.UPDATING)).all()
        return channel_set if channel_set else []

    @property
    def all_settling_channels(self):
        # get all of the opening channels
        channel_set = Session.query(ChannelDatabase).filter(ChannelDatabase.state == State.SETTLING).all()
        return channel_set if channel_set else []


    '''Private function'''
    class Transport(object):
        def __init__(self, tid, name):
            self.__tid  = tid
            self.__name = name
            self.q_maxsize = 100
            self.__task_queue = Queue(maxsize=self.q_maxsize)

        def add_task(self, task):
            if self.__task_queue.qsize() < self.q_maxsize:
                self.__task_queue.put_nowait(task)
                return True
            else:
                # queue is full
                logger.debug('The task queue is full')
                return False

        def get(self, timeout = None):
            task = None
            try:
                task = self.__task_queue.get(block=True, timeout= timeout)
            except Exception as e:
                if not self.__task_queue.empty():
                    logger.error('Transport Thread still in processing data')
            finally:
                return task

        @property
        def name(self):
            return str(self.__name)

    def __register_transport(self, name):
        if not name:
            logger.error( 'Failed to register {}'.format(name) )
            return None

        self.register_lock.acquire()
        tid = len(self.__t_reg.keys())
        t_name = '{}-{}'.format(name, tid)

        # if name has already existed, don't change
        transport = self.Transport(tid, t_name)
        self.__t_reg.update({}.fromkeys([tid], transport))
        self.register_lock.release()
        self.spawn_signal.set()

        return transport


def main():
    monitor = MonitorDaemon()
    gevent.joinall([
        gevent.spawn(monitor.daemon_monitor_timer_event, interval=0.5),
        gevent.spawn(monitor.worker, callback = monitor.update_channel)
    ])


if "__main__" == __name__:
    main()
