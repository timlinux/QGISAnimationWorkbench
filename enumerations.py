# coding=utf-8

"""Enumerated Types."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

#-----------------------------------------------------------
# Copyright (C) 2022 Tim Sutton
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from enum import Enum

class MapMode(Enum):
    SPHERE = 1 # CRS will be manipulated to create a spinning globe effect
    PLANE = 2 # CRS will not be altered, but will pan and zoom to each point
    STATIC = 3 # Map will not pan / zoom