# coding=utf-8
"""Easing selector and preview widget for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

from qgis.PyQt.QtWidgets import QWidget
#from qgis.PyQt.QtGui import QPainter, QPen, QColor
from qgis.PyQt.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QPoint,
    pyqtSignal,
)
#TODO: add a gui to prompt the user if they want to install py
try:
    import pyqtgraph
except ModuleNotFoundError:
    import pip
    pip.main(['install', 'pyqtgraph'])

from pyqtgraph import PlotWidget # pylint: disable=unused-import
import pyqtgraph as pg
from .utilities import get_ui_class

FORM_CLASS = get_ui_class("easing_preview_base.ui")


class EasingAnimation(QPropertyAnimation):
    """Animation settings for easings for natural transitions between states.

    See documentation here which explains that you should
    create your own subclass of QVariantAnimation
    if you want to change the animation behaviour. In our
    case we want to override the fact that the animation
    changes both the x and y coords in each increment
    so that we can show the preview as a mock chart
    https://doc.qt.io/qt-6/qvariantanimation.html#endValue-prop
    """
    def __init__(self, target_object, property):  # pylint: disable=redefined-builtin
        #parent = None
        super(EasingAnimation, self).__init__() # pylint: disable=super-with-arguments
        self.setTargetObject(target_object)
        self.setPropertyName(property)

    def interpolated(
        self, from_point: QPoint, to_point: QPoint, progress: float
    ) -> QPoint:
        """Linearly interpolate X and interpolate Y using the easing."""
        if not isinstance(from_point) == QPoint:
            from_point = QPoint(0, 0)
        x_range = to_point.x() - from_point.x()
        x = (progress * x_range) + from_point.x()
        y_range = to_point.y() - from_point.y()
        y = to_point.y() - (y_range * self.easingCurve().valueForProgress(progress))
        return QPoint(int(x), int(y))


class EasingPreview(QWidget, FORM_CLASS):
    """
    A widget for setting an easing mode.
    """

    # Signal emitted when the easing is changed
    easing_changed_signal = pyqtSignal(QEasingCurve)

    def __init__(self, color="#ff0000", parent=None):
        """Constructor for easing preview.

        :color: Color of the easing display - defaults to red.
        :type current_easing: str

        :param parent: Parent widget of this widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.easing = None
        self.easing_preview_animation = None
        self.preview_color = color
        self.load_combo_with_easings()
        self.setup_easing_previews()
        self.easing_combo.currentIndexChanged.connect(self.easing_changed)
        self.enable_easing.toggled.connect(self.checkbox_changed)
        ## chart: Switch to using white background and black foreground
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        self.chart.hideAxis("bottom")
        self.chart.hideAxis("left")

    def resizeEvent(self, new_size):
        """Resize event handler."""
        super(EasingPreview, self).resizeEvent(new_size) # pylint: disable=super-with-arguments
        width = self.easing_preview.width()
        height = self.easing_preview.height()
        self.easing_preview_animation.setEndValue(QPoint(width, height))

    def checkbox_changed(self, new_state):
        """
        Called when the enabled checkbox is toggled
        """
        if new_state:
            self.enable()
        else:
            self.disable()

    def disable(self):
        """
        Disables the widget
        """
        self.enable_easing.setChecked(False)
        self.easing_preview_animation.stop()

    def enable(self):
        """
        Enables the widget
        """
        self.enable_easing.setChecked(True)
        self.easing_preview_animation.start()

    def is_enabled(self) -> bool:
        """
        Returns True if the easing is enabled
        """
        return self.enable_easing.isChecked()

    def set_easing_by_name(self, name: str):
        """
        Sets an easing mode to show in the widget by name
        """
        combo = self.easing_combo
        index = combo.findText(name)
        if index != -1:
            combo.setCurrentIndex(index)

    def easing_name(self) -> str:
        """
        Returns the currently selected easing name
        """
        return self.easing_combo.currentText()

    def get_easing(self):
        """
        Returns the currently selected easing type
        """
        easing_type = QEasingCurve.Type(self.easing_combo.currentIndex())
        return QEasingCurve(easing_type)

    def set_preview_color(self, color: str):
        """
        Sets the widget's preview color
        """
        self.preview_color = color
        self.easing_preview_icon.setStyleSheet(
            "background-color:%s;border-radius:5px;" % self.preview_color
        )

    def set_checkbox_label(self, label: str):
        """
        Sets the label for the widget
        """
        self.enable_easing.setText(label)

    def load_combo_with_easings(self):
        """
        Populates the combobox with available easing modes
        """
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
        """
        Set up easing previews
        """
        # Icon is the little dot that animates across the widget
        self.easing_preview_icon = QWidget(self.easing_preview)
        self.easing_preview_icon.setStyleSheet(
            "background-color:%s;border-radius:5px;" % self.preview_color
        )
        # this is the size of the dot
        self.easing_preview_icon.resize(10, 10)
        self.easing_preview_animation = EasingAnimation(
            self.easing_preview_icon, b"pos"
        )
        self.easing_preview_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.easing_preview_animation.setStartValue(QPoint(0, 0))
        self.easing_preview_animation.setEndValue(
            QPoint(
                self.easing_preview.width(),
                self.easing_preview.height(),
            )
        )
        self.easing_preview_animation.setDuration(35000)
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
        self.easing_preview_animation.stop()
        self.easing_preview_animation.setEasingCurve(easing_type)
        self.easing = QEasingCurve(easing_type)
        self.easing_changed_signal.emit(self.easing)
        self.easing_preview_animation.start()
        self.chart.clear()
        chart = []
        for i in range(
            0,
            1000,
        ):
            chart.append(self.easing.valueForProgress(i / 1000))
        self.chart.plot(chart)
