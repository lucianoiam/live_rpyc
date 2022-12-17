#!/usr/bin/env python
# -*- coding: utf-8 -*-
#****************************************************************************************
# File:       client.py
#
# Copyright: 2019 Luciano Iam. All Rights reserved
#****************************************************************************************

import imp
import os
import sys
from threading import Thread

"""ensure client uses same rpyc version as MIDI Remote Script"""
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LiveRPyC'))

import rpyc
from rpyc.utils import factory
from rpyc.core import Connection, Service, SocketStream
from rpyc.lib import Timeout

import rpyc_config


disconnection_handler = None
bind = None
_conn = None


def connect():
    """rpyc.utils.factory.connect() uses default 3s connection timeout
    too short for some computers running big projects,
    use connect_stream() instead and set timeout"""
    stream = None
    if sys.platform == 'win32':
        stream = SocketStream.connect(rpyc_config.HOSTNAME, rpyc_config.PORT, timeout=15)
    else:
        stream = SocketStream.unix_connect(rpyc_config.SOCKET_PATH)
    """default sync_request_timeout is 30.0"""
    global _conn
    stream_config = dict(sync_request_timeout=3.0)
    _conn = factory.connect_stream(stream, config=stream_config)
    global bind
    bind = _conn.root.lom_observer_helper.bind
    return _conn.root.Live


def disconnect():
    global disconnection_handler
    disconnection_handler = None
    _conn.root.lom_observer_helper.unbind_all()
    _conn.close()


def start_thread():
    worker = Thread(target=_serve_connections)
    worker.daemon = True
    worker.start()


def _serve_connections():
    _conn.serve_all()
    if disconnection_handler:
        disconnection_handler()


class CustomConnection(Connection):
    
    def serve(self, timeout=1, wait_for_lock=True):
        """Serves a single request or reply that arrives within the given
        time frame (default is 1 sec). Note that the dispatching of a request
        might trigger multiple (nested) requests, thus this function may be
        reentrant.

        :returns: ``True`` if a request or reply were received, ``False``
                  otherwise.
        """
        timeout = Timeout(timeout)
        with self._recv_event:
            if not self._recvlock.acquire(False):
                return (wait_for_lock and
                        self._recv_event.wait(timeout.timeleft()))
        try:
            """possible sync request deadlock on at least
               one windows machine after starting poll thread,
               force a smaller timeout"""
            timeout = 0.01 if sys.platform == 'win32' else timeout 
            data = self._channel.poll(timeout) and self._channel.recv()
            if not data:
                return False
        except EOFError:
            self.close()
            raise
        finally:
            self._recvlock.release()
            with self._recv_event:
                self._recv_event.notify_all()
        self._dispatch(data)
        return True

Service._protocol = CustomConnection


if __name__ == '__main__':
    """using the wrong function signature make listeners silently fail"""
    def current_song_time_listener():
        print(song.get_current_beats_song_time())

    """same as calling api from midi remote script"""
    Live = connect()
    live_app = Live.Application.get_application()
    song = live_app.get_document()

    print('Connected to Ableton Live {}.{}.{}'.format(live_app.get_major_version(),
        live_app.get_minor_version(), live_app.get_bugfix_version()))

    """avoid direct add_*_listener calls and use supplied bind function instead,
       otherwise remove_*_listener calls will fail"""
    bind(song.add_current_song_time_listener, song.remove_current_song_time_listener,
        current_song_time_listener)

    """do not forget"""
    start_thread()

    try:
        input('Try playing/pausing Live or press Enter to exit\n')
    except:
        pass

    disconnect()
