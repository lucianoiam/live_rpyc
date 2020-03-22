# -*- coding: utf-8 -*-
#****************************************************************************************
# File:      __init__.py
#
# Copyright: 2019 Luciano Iam. All Rights reserved
#****************************************************************************************

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from rpyc_control_surface import RpycControlSurface

def create_instance(c_instance):
    return RpycControlSurface(c_instance)
