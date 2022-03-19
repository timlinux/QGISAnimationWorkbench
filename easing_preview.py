# coding=utf-8
"""This module implements the easing selector and preview widget for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA

from qgis.PyQt import QtWidgets
from PyQt5.QtWidgets import QWidget
from qgis.PyQt.QtCore import QEasingCurve, QPropertyAnimation, QPoint

from .utilities import get_ui_class
from enum import Enum

FORM_CLASS = get_ui_class('easing_preview_base.ui')

class EasingPreview(QWidget, FORM_CLASS):
    """Widget implementation for the easing preview class."""

    def __init__(
        self, 
        enable_easing=False,
        current_easing="Linear",
        color = "#ff0000",
        parent=None):
        """Constructor for easing preview.

        :param enable_easing: Flag to indicate whether the easing is enabled.
        :type enable_easing: bool

        :current_easing: Easing to select by default in the easing combo.
        :type current_easing: str
        
        :color: Color of the easing display - defaults to red.
        :type current_easing: str

        :param parent: Parent widget of this widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)   
        self.easing_preview_animation = None
        self.preview_color = color
        self.load_combo_with_easings()
        self.setup_easing_previews()
    
    def disable(self):
        self.enable_easing.setChecked(False)
        self.easing_preview_animation.setLoopCount(0)

    def enable(self):
        self.enable_easing.setChecked(True)
        self.easing_preview_animation.setLoopCount(-1)
    
    def is_enabled(self):
        return self.easing.enable_easing.isChecked()
    
    def set_easing_by_name(self, name):
        combo = self.easing_combo
        index = combo.findText(name)
        if index != -1:
            combo.setCurrentIndex(index)
    
    def easing_name(self):
        return self.easing_combo.currentText()

    def easing(self):
        return self.easing_combo.currentData()

    def load_combo_with_easings(self):
        # Perhaps we can softcode these items using the logic here
        # https://github.com/baoboa/pyqt5/blob/master/examples/animation/easing/easing.py#L159
        combo = self.easing_combo
        combo.addItem("Linear",QEasingCurve.Linear)
        combo.addItem("InQuad",QEasingCurve.InQuad)
        combo.addItem("OutQuad",QEasingCurve.OutQuad)
        combo.addItem("InOutQuad",QEasingCurve.InOutQuad)
        combo.addItem("OutInQuad",QEasingCurve.OutInQuad)
        combo.addItem("InCubic",QEasingCurve.InCubic)
        combo.addItem("OutCubic",QEasingCurve.OutCubic)
        combo.addItem("InOutCubic",QEasingCurve.InOutCubic)
        combo.addItem("OutInCubic",QEasingCurve.OutInCubic)
        combo.addItem("InQuart",QEasingCurve.InQuart)
        combo.addItem("OutQuart",QEasingCurve.OutQuart)
        combo.addItem("InOutQuart",QEasingCurve.InOutQuart)
        combo.addItem("OutInQuart",QEasingCurve.OutInQuart)
        combo.addItem("InQuint",QEasingCurve.InQuint)
        combo.addItem("OutQuint",QEasingCurve.OutQuint)
        combo.addItem("InOutQuint",QEasingCurve.InOutQuint)
        combo.addItem("OutInQuint",QEasingCurve.OutInQuint)
        combo.addItem("InSine",QEasingCurve.InSine)
        combo.addItem("OutSine",QEasingCurve.OutSine)
        combo.addItem("InOutSine",QEasingCurve.InOutSine)
        combo.addItem("OutInSine",QEasingCurve.OutInSine)
        combo.addItem("InExpo",QEasingCurve.InExpo)
        combo.addItem("OutExpo",QEasingCurve.OutExpo)
        combo.addItem("InOutExpo",QEasingCurve.InOutExpo)
        combo.addItem("OutInExpo",QEasingCurve.OutInExpo)
        combo.addItem("InCirc",QEasingCurve.InCirc)
        combo.addItem("OutCirc",QEasingCurve.OutCirc)
        combo.addItem("InOutCirc",QEasingCurve.InOutCirc)
        combo.addItem("OutInCirc",QEasingCurve.OutInCirc)
        combo.addItem("InElastic",QEasingCurve.InElastic)
        combo.addItem("OutElastic",QEasingCurve.OutElastic)
        combo.addItem("InOutElastic",QEasingCurve.InOutElastic)
        combo.addItem("OutInElastic",QEasingCurve.OutInElastic)
        combo.addItem("InBack",QEasingCurve.InBack)
        combo.addItem("OutBack",QEasingCurve.OutBack)
        combo.addItem("InOutBack",QEasingCurve.InOutBack)
        combo.addItem("OutInBack",QEasingCurve.OutInBack)
        combo.addItem("InBounce",QEasingCurve.InBounce)
        combo.addItem("OutBounce",QEasingCurve.OutBounce)
        combo.addItem("InOutBounce",QEasingCurve.InOutBounce)
        combo.addItem("OutInBounce",QEasingCurve.OutInBounce)
        combo.addItem("BezierSpline",QEasingCurve.BezierSpline)
        combo.addItem("TCBSpline",QEasingCurve.TCBSpline)
    
    def setup_easing_previews(self):
        # Set up easing previews
        self.easing_preview_icon = QtWidgets.QWidget(
            self.easing_preview)
        self.easing_preview_icon.setStyleSheet(
            'background-color:%s;border-radius:5px;'
            % self.preview_color)
        self.easing_preview_icon.resize(10, 10)
        self.easing_preview_animation = QPropertyAnimation(
            self.easing_preview_icon, b"pos")
        self.easing_preview_animation.setEasingCurve(
            QEasingCurve.InOutCubic)
        self.easing_preview_animation.setStartValue(QPoint(0, 0))
        self.easing_preview_animation.setEndValue(QPoint(250, 150))
        self.easing_preview_animation.setDuration(1500)
        # loop forever ...
        self.easing_preview_animation.setLoopCount(-1)
        self.easing_preview_animation.start()

    def easing_changed(self, index):
        """Handle changes to the pan easing type combo.
        
        .. note:: This is called on changes to the pan easing combo.

        .. versionadded:: 1.0

        :param index: Index of the now selected combo item.
        :type flag: int

        """
        easing_type = QEasingCurve.Type(index)
        self.easing_preview_animation.setEasingCurve(easing_type)
        self.easing = QEasingCurve(easing_type)