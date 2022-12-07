# -*- coding: utf-8 -*-
#****************************************************************************************
# File:       rpyc_control_surface.py
#
# Copyright: 2013 Ableton AG, Berlin. All Rights reserved
# Copyright: 2019 Luciano Iam. All Rights reserved
#
# Based on https://github.com/bkillenit/AbletonAPI/blob/master/python-api-materials/code/RpycHost/RpycHost.py
#          https://github.com/gluon/AbletonLive10_MIDIRemoteScripts/blob/master/_Framework/ControlSurface.py
#****************************************************************************************

from __future__ import with_statement

from _Framework import Task
from _Framework.ControlSurface import ControlSurface
from _Framework.Profile import profile

import lom_observer_helper
from rpyc_server import RpycServer


class RpycControlSurface(ControlSurface):

    """ui update time"""
    suggested_update_time_in_ms = 10

    def __init__(self, c_instance):
        super(RpycControlSurface, self).__init__(c_instance)
        with self._control_surface_injector:
            with self.component_guard():
                self._rpyc_server = RpycServer(
                    connection_callback = self._on_client_connected,
                    disconnection_callback = self._on_client_disconnected
                )
                self._rpyc_server.start()

    """_Framework/ControlSurface.py@123"""
    def disconnect(self):
        lom_observer_helper.unbind_all()
        self._rpyc_server.close()
        super(RpycControlSurface, self).disconnect()

    """_Framework/ControlSurface.py@543"""
    @profile
    def call_listeners(self, listeners):
        with self.component_guard():
            for listener in filter(lambda l: l != None, listeners):
                """avoid RuntimeError: Changes cannot be triggered by notifications...
                by wrapping listeners in a task"""
                try:
                    self._tasks.add(Task.run(listener))
                except:
                    listener.disconnect()

    def _on_client_connected(self):
        pass

    def _on_client_disconnected(self):
        lom_observer_helper.unbind_all()
