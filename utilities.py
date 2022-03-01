# coding=utf-8

"""Utilities for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

import os
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA

from qgis.PyQt import uic
from qgis.PyQt import QtCore

def resources_path(*args):
    """Get the path to our resources folder.

    .. versionadded:: 1.0

    Note that in version 1.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param args List of path elements e.g. ['img', 'logos', 'image.png']
    :type args: str

    :return: Absolute path to the resources folder.
    :rtype: str
    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(
        os.path.join(path, 'resources'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path


def resource_url(path):
    """Get the a local filesystem url to a given resource.

    .. versionadded:: 1.0

    Note that we dont use Qt Resource files in
    favour of directly accessing on-disk resources.

    :param path: Path to resource e.g. /home/timlinux/foo/bar.png
    :type path: str

    :return: A valid file url e.g. file:///home/timlinux/foo/bar.png
    :rtype: str
    """
    url = QtCore.QUrl.fromLocalFile(path)
    return str(url.toString())


def get_ui_class(ui_file):
    """Get UI Python class from .ui file.

       Can be filename.ui or subdirectory/filename.ui

    :param ui_file: The file of the ui in safe.gui.ui
    :type ui_file: str
    """
    os.path.sep.join(ui_file.split('/'))
    ui_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            # os.pardir,
            'ui',
            ui_file
        )
    )
    return uic.loadUiType(ui_file_path)[0]

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
        _f for _f in os.environ.get(
            'PATHEXT',
            '').split(
            os.pathsep) if _f]
    # pylint: enable=W0141
    path = os.environ.get('PATH', None)
    # In c6c9b26 we removed this hard coding for issue #529 but I am
    # adding it back here in case the user's path does not include the
    # gdal binary dir on OSX but it is actually there. (TS)
    if sys.platform == 'darwin':  # Mac OS X
        gdal_prefix = (
            '/Library/Frameworks/GDAL.framework/'
            'Versions/Current/Programs/')
        path = '%s:%s' % (path, gdal_prefix)

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