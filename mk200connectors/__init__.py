#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#Copyright (C) 2015: Nucleron R&D LLC
#
#Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD
#
#See COPYING file for copyrights details.
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#General Public License for more details.
#
#You should have received a copy of the GNU General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


def MK200_connector_factory(uri, confnodesroot):
    """
    This returns the connector to YAPLC style PLCobject
    """
    import os
    # import wx

    servicetype, comportstr = uri.split("://")

    confnodesroot.logger.write(_("Connecting to:" + comportstr + "\n"))

    from MK200Object import MK200Object

    if os.name in ("nt", "ce"):
        lib_ext = ".dll"
    else:
        lib_ext = ".so"

    YaPySerialLib = os.path.dirname(os.path.realpath(__file__))
    YaPySerialLib = os.path.dirname(YaPySerialLib)
    YaPySerialLib = os.path.dirname(YaPySerialLib)
    YaPySerialLib = os.path.join(YaPySerialLib, "YaPySerial", "bin", "libYaPySerial" + lib_ext)
    # print YaPySerialLib

    return MK200Object(YaPySerialLib,confnodesroot,comportstr)

def MK201_connector_factory(uri, confnodesroot):
    import os
    import sys
    from MK201Object import MK201Object

    servicetype, comportstr = uri.split("://")
    # print '_dist_folder = ', os.path.dirname(os.path.realpath(__file__))

    return MK201Object(confnodesroot, comportstr)
