# coding=utf-8

"""Init for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

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

# DO NOT REMOVE THIS - it forces sip2
# noinspection PyUnresolvedReferences
from matplotlib.colors import from_levels_and_colors
import qgis  # pylint: disable=unused-import

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from .animation_workbench import AnimationWorkbench
from .workbench_settings import WorkbenchSettings
from .utilities import resources_path
from .render_queue import RenderQueue


def classFactory(iface):
    return AnimationWorkbenchPlugin(iface)


class AnimationWorkbenchPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):

        self.render_queue = RenderQueue(iface=self.iface)

        # If you change this to true, QGIS startup
        # will block until it can attache to the remote debugger
        debug_mode = False
        if debug_mode:
            try:
                self.initialize_debugger()
            except:
                pass

        icon = QIcon(resources_path(
            'img', 'icons', 'animation-workbench.svg'))

        self.run_action = QAction(
            icon,
            'Animation Workbench',
            self.iface.mainWindow())
        self.run_action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.run_action)

        self.settings_action = QAction(
            icon,
            'Animation Workbench Settings',
            self.iface.mainWindow())
        self.settings_action.triggered.connect(self.settings)
        self.iface.addToolBarIcon(self.settings_action)

    def unload(self):
        self.iface.removeToolBarIcon(self.run_action)
        self.iface.removeToolBarIcon(self.settings_action)
        del self.run_action
        del self.settings_action

    def initialize_debugger(self):
        import multiprocessing
        if multiprocessing.current_process().pid > 1:
            import debugpy
            debugpy.listen(("0.0.0.0", 9000))
            print("Debugger is ready to be attached, press F5", flush=True)
            debugpy.wait_for_client()
            print("Visual Studio Code debugger is now attached", flush=True)

    def run(self):
        dialog = AnimationWorkbench(
            iface=self.iface,
            render_queue=self.render_queue)
        dialog.exec_()

    def settings(self):
        dialog = WorkbenchSettings()
        dialog.exec_()
