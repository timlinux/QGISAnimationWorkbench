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

import time

# DO NOT REMOVE THIS - it forces sip2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QMessageBox, QPushButton, QAction
from .animation_workbench import AnimationWorkbench
from .workbench_settings import WorkbenchSettings
from .utilities import resources_path
from .render_queue import RenderQueue
from .settings import setting

def classFactory(iface):
    return AnimationWorkbenchPlugin(iface)


class AnimationWorkbenchPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):

        self.render_queue = RenderQueue()
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

        # If you change debug_mode to true, after clicking
        # this toolbutton, QGIS will block until it can attach
        # to the remote debugger
        debug_mode = int(setting(key='debug_mode', default=0))
        if debug_mode:
            self.debug_action = QAction(
                icon,
                'Animation Workbench Debug Mode',
                self.iface.mainWindow())
            self.debug_action.triggered.connect(self.debug)
            self.iface.addToolBarIcon(self.debug_action)

    def debug(self):
        self.display_information_message_box(
            title='Animation Workbench',
            message='Close this dialog then open VSCode and start your debug client.')
        time.sleep(2)
        import multiprocessing
        if multiprocessing.current_process().pid > 1:

            import debugpy
            debugpy.listen(("0.0.0.0", 9000))
            debugpy.wait_for_client()
            self.display_information_message_bar(
                title='Animation Workbench',
                message='Visual Studio Code debugger is now attached on port 9000')

    def unload(self):
        self.iface.removeToolBarIcon(self.run_action)
        self.iface.removeToolBarIcon(self.settings_action)
        del self.run_action
        del self.settings_action

    def run(self):
        dialog = AnimationWorkbench(
            parent=self.iface.mainWindow(),
            iface=self.iface,
            render_queue=self.render_queue)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.show()

    def settings(self):
        dialog = WorkbenchSettings()
        dialog.exec_()

    def display_information_message_bar(
            self,
            title=None,
            message=None,
            more_details=None,
            button_text='Show details ...',
            duration=8):
        """
        Display an information message bar.
        :param title: The title of the message bar.
        :type title: basestring
        :param message: The message inside the message bar.
        :type message: basestring
        :param more_details: The message inside the 'Show details' button.
        :type more_details: basestring
        :param button_text: Text of the button if 'more_details' is not empty.
        :type button_text: basestring
        :param duration: The duration for the display, default is 8 seconds.
        :type duration: int
        """
        self.iface.messageBar().clearWidgets()
        widget = self.iface.messageBar().createMessage(title, message)

        if more_details:
            button = QPushButton(widget)
            button.setText(button_text)
            button.pressed.connect(
                lambda: self.display_information_message_box(
                    title=title, message=more_details))
            widget.layout().addWidget(button)

        self.iface.messageBar().pushWidget(widget, Qgis.Info, duration)

    def display_information_message_box(
            self, parent=None, title=None, message=None):
        """
        Display an information message box.
        :param title: The title of the message box.
        :type title: basestring
        :param message: The message inside the message box.
        :type message: basestring
        """
        QMessageBox.information(parent, title, message)