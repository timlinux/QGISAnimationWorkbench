# coding=utf-8
"""Easing selector and preview widget for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QPoint,
    pyqtSignal,
)
from .utilities import get_ui_class

FORM_CLASS = get_ui_class("easing_preview_base.ui")


class EasingPreview(QWidget, FORM_CLASS):
    # Signal emitted when the easing is changed
    easing_changed_signal = pyqtSignal(QEasingCurve)

    """Widget implementation for the easing preview class."""

    def __init__(self, color="#ff0000", parent=None):
        """Constructor for easing preview.

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
        self.easing_combo.currentIndexChanged.connect(self.easing_changed)
        self.enable_easing.toggled.connect(self.checkbox_changed)

    def checkbox_changed(self, new_state):
        if new_state:
            self.enable()
        else:
            self.disable()

    def disable(self):
        self.enable_easing.setChecked(False)
        self.easing_preview_animation.stop()

    def enable(self):
        self.enable_easing.setChecked(True)
        self.easing_preview_animation.start()

    def is_enabled(self):
        return self.enable_easing.isChecked()

    def set_easing_by_name(self, name):
        combo = self.easing_combo
        index = combo.findText(name)
        if index != -1:
            combo.setCurrentIndex(index)

    def easing_name(self):
        return self.easing_combo.currentText()

    def get_easing(self):
        easing_type = QEasingCurve.Type(self.easing_combo.currentIndex())
        return QEasingCurve(easing_type)

    def preview_color(self):
        return self.preview_color

    def set_preview_color(self, color):
        self.preview_color = color
        self.easing_preview_icon.setStyleSheet(
            "background-color:%s;border-radius:5px;" % self.preview_color
        )

    def set_checkbox_label(self, label):
        self.enable_easing.setText(label)

    def load_combo_with_easings(self):
        # Perhaps we can softcode these items using the logic here
        # https://github.com/baoboa/pyqt5/blob/master/examples/
        # animation/easing/easing.py#L159
        combo = self.easing_combo
        combo.addItem("Linear", QEasingCurve.Linear)
        combo.addItem("InQuad", QEasingCurve.InQuad)
        combo.addItem("OutQuad", QEasingCurve.OutQuad)
        combo.addItem("InOutQuad", QEasingCurve.InOutQuad)
        combo.addItem("OutInQuad", QEasingCurve.OutInQuad)
        combo.addItem("InCubic", QEasingCurve.InCubic)
        combo.addItem("OutCubic", QEasingCurve.OutCubic)
        combo.addItem("InOutCubic", QEasingCurve.InOutCubic)
        combo.addItem("OutInCubic", QEasingCurve.OutInCubic)
        combo.addItem("InQuart", QEasingCurve.InQuart)
        combo.addItem("OutQuart", QEasingCurve.OutQuart)
        combo.addItem("InOutQuart", QEasingCurve.InOutQuart)
        combo.addItem("OutInQuart", QEasingCurve.OutInQuart)
        combo.addItem("InQuint", QEasingCurve.InQuint)
        combo.addItem("OutQuint", QEasingCurve.OutQuint)
        combo.addItem("InOutQuint", QEasingCurve.InOutQuint)
        combo.addItem("OutInQuint", QEasingCurve.OutInQuint)
        combo.addItem("InSine", QEasingCurve.InSine)
        combo.addItem("OutSine", QEasingCurve.OutSine)
        combo.addItem("InOutSine", QEasingCurve.InOutSine)
        combo.addItem("OutInSine", QEasingCurve.OutInSine)
        combo.addItem("InExpo", QEasingCurve.InExpo)
        combo.addItem("OutExpo", QEasingCurve.OutExpo)
        combo.addItem("InOutExpo", QEasingCurve.InOutExpo)
        combo.addItem("OutInExpo", QEasingCurve.OutInExpo)
        combo.addItem("InCirc", QEasingCurve.InCirc)
        combo.addItem("OutCirc", QEasingCurve.OutCirc)
        combo.addItem("InOutCirc", QEasingCurve.InOutCirc)
        combo.addItem("OutInCirc", QEasingCurve.OutInCirc)
        combo.addItem("InElastic", QEasingCurve.InElastic)
        combo.addItem("OutElastic", QEasingCurve.OutElastic)
        combo.addItem("InOutElastic", QEasingCurve.InOutElastic)
        combo.addItem("OutInElastic", QEasingCurve.OutInElastic)
        combo.addItem("InBack", QEasingCurve.InBack)
        combo.addItem("OutBack", QEasingCurve.OutBack)
        combo.addItem("InOutBack", QEasingCurve.InOutBack)
        combo.addItem("OutInBack", QEasingCurve.OutInBack)
        combo.addItem("InBounce", QEasingCurve.InBounce)
        combo.addItem("OutBounce", QEasingCurve.OutBounce)
        combo.addItem("InOutBounce", QEasingCurve.InOutBounce)
        combo.addItem("OutInBounce", QEasingCurve.OutInBounce)
        combo.addItem("BezierSpline", QEasingCurve.BezierSpline)
        combo.addItem("TCBSpline", QEasingCurve.TCBSpline)

    def setup_easing_previews(self):
        # Set up easing previews
        self.easing_preview_icon = QtWidgets.QWidget(self.easing_preview)
        height = self.easing_preview.height()
        width = self.easing_preview.width()
        self.preview_color = "red"
        self.easing_preview_icon.setStyleSheet(
            "background-color:%s;border-radius:5px;" % self.preview_color
        )
        self.easing_preview_icon.resize(10, 10)
        self.easing_preview_animation = QPropertyAnimation(
            self.easing_preview_icon, b"pos"
        )
        self.easing_preview_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.easing_preview_animation.setStartValue(QPoint(0, 0))
        self.easing_preview_animation.setEndValue(QPoint(width, height))
        self.easing_preview_animation.setDuration(3500)
        # loop forever ...
        self.easing_preview_animation.setLoopCount(-1)
        self.easing_preview_animation.start()

    def easing_changed(self, index):
        """Handle changes to the easing type combo.

        .. note:: This is called on changes to the easing combo.

        .. versionadded:: 1.0

        :param index: Index of the now selected combo item.
        :type flag: int

        """
        easing_type = QEasingCurve.Type(index)
        self.easing_preview_animation.setEasingCurve(easing_type)
        self.easing = QEasingCurve(easing_type)
        self.easing_changed_signal.emit(self.easing)
