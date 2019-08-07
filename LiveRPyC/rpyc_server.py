# -*- coding: utf-8 -*-
#****************************************************************************************
# File:       rpyc_server.py
#
# Copyright: 2019 iamluciano. All Rights reserved
#
# Based on https://github.com/bkillenit/AbletonAPI/blob/master/python-api-materials/code/RpycHost/TaskServer.py
#****************************************************************************************

import os
import sys

import Live
from _Framework import Task
from _Framework.Dependency import depends
from _Framework.Util import const, print_message

import rpyc.lib.compat
from rpyc import Service
from rpyc.core import Channel, Connection, SocketStream
from rpyc.lib import Timeout
from rpyc.utils.server import Server

import rpyc_config
import lom_observer_helper


class LiveApiService(Service):

    exposed_Live = Live
    exposed_lom_observer_helper = lom_observer_helper


class RpycServer(Server):

    @depends(parent_task_group = None, log_message = const(print_message))
    def __init__(self, parent_task_group = None, log_message = None,
            connection_callback = lambda: None, disconnection_callback = lambda: None):
        if sys.platform == 'win32':
            kwargs = dict(hostname = rpyc_config.HOSTNAME, port = rpyc_config.PORT)
        else:
            try:
                os.unlink(rpyc_config.SOCKET_PATH)
            except OSError:
                pass
            kwargs = dict(socket_path = rpyc_config.SOCKET_PATH)
        super(RpycServer, self).__init__(LiveApiService, **kwargs)
        self._connection_callback = connection_callback
        self._disconnection_callback = disconnection_callback
        self._log_message = log_message
        self._live_task = parent_task_group.add(self._live_tick).kill()
        self._listener_poll = rpyc.lib.compat.poll()
        self._listener_poll.register(self.listener.fileno(), 'r')
        self._connection = None

    def start(self):
        self.listener.listen(1)
        self.active = True
        self._live_task.restart()
        self._log_message('server started', self.host, self.port)

    def close(self):
        super(RpycServer, self).close()
        self._live_task.kill()
        self._log_message('server stopped')

    def _live_tick(self, delta = None):
        if self._connection:
            self._serve()
        else:
            self._wait()
        return Task.RUNNING

    def _serve(self):
        try:
            """poll_all() ignores EOFError, use poll() instead
               higher timeout: lower client latency, less responsive ui
               lower timeout: higher client latency, more responsive ui"""
            timeout = Timeout(0.025)
            while not timeout.expired():
                self._connection.poll(timeout.timeleft())
        except:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None
            self._disconnection_callback()
            self._log_message('client disconnected')

    def _wait(self):
        if not self._listener_poll.poll(0.01):
            return
        sock, addrinfo = self.listener.accept()
        self.clients.add(sock)
        config = dict(self.protocol_config, allow_all_attrs = True, allow_setattr = True)
        self._connection = Connection(self.service, Channel(SocketStream(sock)), config)
        self._connection_callback()
        self._log_message('client connected', addrinfo)
