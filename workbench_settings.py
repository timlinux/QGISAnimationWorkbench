# coding=utf-8
"""This module has the main GUI interaction logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"


# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA

from qgis.PyQt import QtGui, QtWidgets

from .settings import set_setting, setting
from .utilities import get_ui_class, resources_path


FORM_CLASS = get_ui_class("workbench_settings_base.ui")


class WorkbenchSettings(QtWidgets.QDialog, FORM_CLASS):
    """Dialog implementation class Animation Workbench class."""

    def __init__(self, parent=None):
        """Constructor for the settings buffer dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Animation Workbench"))
        icon = resources_path("img", "icons", "animation-workshop.svg")
        self.setWindowIcon(QtGui.QIcon(icon))
        self.parent = parent

        # Close button action
        # close_button = self.button_box.button(
        #    QtWidgets.QDialogButtonBox.Close)
        # close_button.clicked.connect(self.reject)

        # The maximum number of concurrent threads to allow
        # during rendering. Probably setting to the same number
        # of CPU cores you have would be a good conservative approach
        # You could probably run 100 or more on a decently specced machine
        self.spin_thread_pool_size.setValue(
            int(setting(key="render_thread_pool_size", default=10))
        )
        # This is intended for developers to attach to the plugin using a
        # remote debugger so that they can step through the code. Do not
        # enable it if you do not have a remote debugger set up as it will
        # block QGIS startup until a debugger is attached to the process.
        # Requires restart after changing.
        debug_mode = int(setting(key="debug_mode", default=0))
        if debug_mode:
            self.debug_mode_checkbox.setChecked(True)
        else:
            self.debug_mode_checkbox.setChecked(False)
        # Adds verbose log message, useful for diagnostics
        verbose_mode = int(setting(key="verbose_mode", default=0))
        if verbose_mode:
            self.verbose_mode_checkbox.setChecked(True)
        else:
            self.verbose_mode_checkbox.setChecked(False)

    def accept(self):
        """Process the animation sequence.

        .. note:: This is called on OK click.
        """
        set_setting(
            key="render_thread_pool_size",
            value=self.spin_thread_pool_size.value(),
        )
        if self.debug_mode_checkbox.isChecked():
            set_setting(key="debug_mode", value=1)
        else:
            set_setting(key="debug_mode", value=0)

        if self.verbose_mode_checkbox.isChecked():
            set_setting(key="verbose_mode", value=1)
        else:
            set_setting(key="verbose_mode", value=0)

        self.close()
