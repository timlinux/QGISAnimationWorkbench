# coding=utf-8
"""Widget for managing a list of media in the AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import (
    pyqtSignal,
)
from .utilities import get_ui_class

FORM_CLASS = get_ui_class("media_list_widget_base.ui")


class MediaListWidget(QWidget, FORM_CLASS):
    """
    A widget for managing a list of media.
    """

    def __init__(self, media_type="images", parent=None):
        """Constructor for media_list_widget.

        :media_type: Types of media that can be managed.
        :type current_easing: str

        :param parent: Parent widget of this widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.media_type = media_type
