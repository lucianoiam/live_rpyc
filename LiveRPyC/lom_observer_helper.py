# -*- coding: utf-8 -*-
#****************************************************************************************
# File:      lom_observer_helper.py
#
# Copyright: 2019 iamluciano. All Rights reserved
#
# Currently there is no unbind() function for single listeners
# because rpyc netrefs (object proxies) vary between calls
# ie, calling bind and unbind using the same remote_listener
# from the remote (client) code result in different proxied
# objects in local (server: live) code
#****************************************************************************************

_removers = []


def bind(setter, remover, remote_listener):
    """wrap with lambda otherwise listener removal methods fail for rypyc netrefs:
       RuntimeError: Observer not connected"""
    local_listener = lambda: remote_listener()        
    _removers.append(lambda: remover(local_listener))
    setter(local_listener)


def unbind_all():
    global _removers
    for remover in _removers:
        try:
            remover()
        except:
            """listener might have been already disconnected in call_listeners()"""
            pass
    _removers = []
