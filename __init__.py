# coding=utf-8

"""Init for AnimationWorkbench."""

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

# DO NOT REMOVE THIS - it forces sip2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from .animation_workbench import AnimationWorkbench
from .utilities import resources_path

def classFactory(iface):
    return AnimationWorkbenchPlugin(iface)

class AnimationWorkbenchPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        
        # If you change this to true, QGIS startup
        # will block until it can attache to the remote debugger
        debug_mode = True
        if debug_mode:
            try:
                self.initialize_debugger()
            except:
                pass

        icon = QIcon(resources_path(
            'img', 'icons', 'animation-workshop.svg'))
        self.action = QAction(
            icon, 
            'Animation Workshop', 
            self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action
    
    def initialize_debugger(self):
        import multiprocessing
        if multiprocessing.current_process().pid > 1:
            import debugpy
            debugpy.listen(("0.0.0.0", 9000))
            print("Debugger is ready to be attached, press F5", flush=True)
            debugpy.wait_for_client()
            print("Visual Studio Code debugger is now attached", flush=True)

    def run(self):
        dialog = AnimationWorkbench(iface=self.iface)
        dialog.exec_()
