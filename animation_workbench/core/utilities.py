# coding=utf-8

"""Utilities for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

# -----------------------------------------------------------
# Copyright (C) 2022 Tim Sutton
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

from math import floor
import os
import sys


class CoreUtils:
    """
    Core utilities
    """

    @staticmethod
    def which(name, flags=os.X_OK):
        """Search PATH for executable files with the given name.

        ..note:: This function was taken verbatim from the twisted framework,
          licence available here:
          http://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/LICENSE

        On newer versions of MS-Windows, the PATHEXT environment variable will be
        set to the list of file extensions for files considered executable. This
        will normally include things like ".EXE". This function will also find
        files
        with the given name ending with any of these extensions.

        On MS-Windows the only flag that has any meaning is os.F_OK. Any other
        flags will be ignored.

        :param name: The name for which to search.
        :type name: C{str}

        :param flags: Arguments to L{os.access}.
        :type flags: C{int}

        :returns: A list of the full paths to files found, in the order in which
            they were found.
        :rtype: C{list}
        """
        result = []
        # pylint: disable=W0141
        extensions = [
            _f for _f in os.environ.get("PATHEXT", "").split(os.pathsep) if _f
        ]
        # pylint: enable=W0141
        path = os.environ.get("PATH", None)
        # In c6c9b26 we removed this hard coding for issue #529 but I am
        # adding it back here in case the user's path does not include the
        # gdal binary dir on OSX but it is actually there. (TS)
        if sys.platform == "darwin":  # Mac OS X
            gdal_prefix = (
                "/Library/Frameworks/GDAL.framework/Versions/Current/Programs/"
            )
            path = "%s:%s" % (path, gdal_prefix)

        if path is None:
            return []

        for p in path.split(os.pathsep):
            p = os.path.join(p, name)
            if os.access(p, flags):
                result.append(p)
            for e in extensions:
                path_extensions = p + e
                if os.access(path_extensions, flags):
                    result.append(path_extensions)

        return result


def calculate_cardinality(angle):
    """Compute the cardinality of an angle.

    ..versionadded: 1.0

    ..notes: Adapted from original function with the same
        name I wrote for InaSAFE.

    :param angle: Bearing angle.
    :type angle: float

    :return: Cardinality text.
    :rtype: str
    """
    # this method could still be improved later, since the acquisition interval
    # is a bit strange, i.e the input angle of 22.499° will return `N` even
    # though 22.5° is the direction for `NNE`

    direction_list = ("N,NNE,NE,ENE,E,ESE,SE,SSE,S,SSW,SW,WSW,W,WNW,NW,NNW").split(",")

    bearing = float(angle)
    direction_count = len(direction_list)
    direction_interval = 360.0 / direction_count
    index = int(floor(bearing / direction_interval))
    index %= direction_count
    return direction_list[index]
