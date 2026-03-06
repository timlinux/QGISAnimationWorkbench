# coding=utf-8
"""Easing selector and preview widget for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

from qgis.PyQt.QtWidgets import QWidget, QApplication
from qgis.PyQt.QtGui import QPalette
from qgis.PyQt.QtCore import (
    QEasingCurve,
    QTimer,
    pyqtSignal,
)

try:
    import pyqtgraph as pg
    from pyqtgraph import PlotWidget  # pylint: disable=unused-import
except ImportError:
    # Try to install pyqtgraph using subprocess (modern approach)
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyqtgraph"])
        import pyqtgraph as pg
        from pyqtgraph import PlotWidget
    except Exception:
        pg = None
        PlotWidget = None

from .utilities import get_ui_class

# Kartoza Brand Colors
KARTOZA_GREEN_DARK = "#589632"
KARTOZA_GREEN_LIGHT = "#93b023"

# Theme-specific colors
DARK_THEME = {
    "background": "#2d2d2d",
    "foreground": KARTOZA_GREEN_LIGHT,
    "dot_color": "#ff6b6b",
    "border": KARTOZA_GREEN_DARK,
}

LIGHT_THEME = {
    "background": "#f5f5f5",
    "foreground": KARTOZA_GREEN_DARK,
    "dot_color": "#e74c3c",
    "border": KARTOZA_GREEN_DARK,
}

# Animation settings
ANIMATION_DURATION_MS = 3000  # Duration for one animation cycle
ANIMATION_STEPS = 100  # Number of steps in the animation
DOT_SIZE = 12  # Size of the indicator dot

FORM_CLASS = get_ui_class("easing_preview_base.ui")


class EasingPreview(QWidget, FORM_CLASS):
    """
    A widget for setting an easing mode with curve visualization.

    The dot position is controlled externally via set_progress() method,
    allowing it to be linked to a slider or spinbox for smooth scrubbing.
    """

    # Signal emitted when the easing is changed
    easing_changed_signal = pyqtSignal(QEasingCurve)

    def __init__(self, color=None, parent=None):
        """Constructor for easing preview.

        :param color: Color of the dot (unused, kept for API compatibility).
        :type color: str

        :param parent: Parent widget of this widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.easing = QEasingCurve(QEasingCurve.Linear)
        self.curve_data = []
        self.curve_plot = None
        self.dot_plot = None
        self.animation_progress = 0.0
        self.animation_direction = 1  # 1 = forward, -1 = backward

        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animation)

        self.load_combo_with_easings()
        self.setup_chart()
        self.easing_combo.currentIndexChanged.connect(self.easing_changed)
        self.enable_easing.toggled.connect(self.checkbox_changed)

    def is_dark_theme(self) -> bool:
        """Detect if the current application theme is dark.

        :returns: True if the theme is dark, False otherwise.
        :rtype: bool
        """
        palette = QApplication.instance().palette()
        window_color = palette.color(QPalette.Window)
        luminance = (
            0.299 * window_color.red() +
            0.587 * window_color.green() +
            0.114 * window_color.blue()
        )
        return luminance < 128

    def get_theme(self) -> dict:
        """Get the current theme colors."""
        return DARK_THEME if self.is_dark_theme() else LIGHT_THEME

    def setup_chart(self):
        """Set up the chart with the easing curve and indicator dot."""
        if pg is None:
            return

        theme = self.get_theme()

        # Configure chart appearance
        self.chart.setBackground(theme["background"])
        self.chart.hideAxis("bottom")
        self.chart.hideAxis("left")
        self.chart.setMouseEnabled(x=False, y=False)
        self.chart.setMenuEnabled(False)

        # Add a border around the chart
        self.chart.setStyleSheet(f"""
            border: 2px solid {theme["border"]};
            border-radius: 6px;
        """)

        # Generate initial curve data
        self._generate_curve_data()

        # Plot the curve
        pen = pg.mkPen(color=theme["foreground"], width=3)
        self.curve_plot = self.chart.plot(self.curve_data, pen=pen)

        # Create the indicator dot as a scatter plot
        self.dot_plot = pg.ScatterPlotItem(
            size=DOT_SIZE,
            brush=pg.mkBrush(theme["dot_color"]),
            pen=pg.mkPen(None)
        )
        self.chart.addItem(self.dot_plot)

        # Set initial dot position
        self._update_dot_position()

        # Start animation timer
        interval = ANIMATION_DURATION_MS // ANIMATION_STEPS
        self.animation_timer.start(interval)

    def _generate_curve_data(self):
        """Generate the Y values for the easing curve."""
        self.curve_data = []
        num_points = 1000
        for i in range(num_points):
            progress = i / (num_points - 1)
            self.curve_data.append(self.easing.valueForProgress(progress))

    def _update_animation(self):
        """Update the animation progress and dot position."""
        step = 1.0 / ANIMATION_STEPS
        self.animation_progress += step * self.animation_direction

        # Bounce at the ends
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_direction = -1
        elif self.animation_progress <= 0.0:
            self.animation_progress = 0.0
            self.animation_direction = 1

        self._update_dot_position()

    def set_progress(self, progress: float):
        """Set the dot position based on progress (0.0 to 1.0).

        This method allows external control of the dot position,
        typically linked to a slider or frame spinbox.

        :param progress: Progress value from 0.0 to 1.0.
        :type progress: float
        """
        self.animation_progress = max(0.0, min(1.0, progress))
        self._update_dot_position()

    def _update_dot_position(self):
        """Update the dot position on the chart based on animation progress."""
        if self.dot_plot is None:
            return

        # X position is linear (0 to 999 for 1000 data points)
        x = self.animation_progress * (len(self.curve_data) - 1)
        # Y position follows the easing curve
        y = self.easing.valueForProgress(self.animation_progress)

        self.dot_plot.setData([x], [y])

    def checkbox_changed(self, new_state):
        """Called when the enabled checkbox is toggled."""
        if new_state:
            self.enable()
        else:
            self.disable()

    def disable(self):
        """Disables the widget."""
        self.enable_easing.setChecked(False)
        self.animation_timer.stop()

    def enable(self):
        """Enables the widget."""
        self.enable_easing.setChecked(True)
        interval = ANIMATION_DURATION_MS // ANIMATION_STEPS
        self.animation_timer.start(interval)

    def is_enabled(self) -> bool:
        """Returns True if the easing is enabled."""
        return self.enable_easing.isChecked()

    def set_easing_by_name(self, name: str):
        """Sets an easing mode to show in the widget by name."""
        combo = self.easing_combo
        index = combo.findText(name)
        if index != -1:
            combo.setCurrentIndex(index)

    def easing_name(self) -> str:
        """Returns the currently selected easing name."""
        return self.easing_combo.currentText()

    def get_easing(self):
        """Returns the currently selected easing type."""
        easing_type = QEasingCurve.Type(self.easing_combo.currentIndex())
        return QEasingCurve(easing_type)

    def set_preview_color(self, color: str):
        """Sets the widget's dot color."""
        if self.dot_plot and pg:
            self.dot_plot.setBrush(pg.mkBrush(color))

    def set_checkbox_label(self, label: str):
        """Sets the label for the widget."""
        self.enable_easing.setText(label)

    def load_combo_with_easings(self):
        """Populates the combobox with available easing modes."""
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

    def easing_changed(self, index):
        """Handle changes to the easing type combo.

        :param index: Index of the now selected combo item.
        :type index: int
        """
        easing_type = QEasingCurve.Type(index)
        self.easing = QEasingCurve(easing_type)
        self.easing_changed_signal.emit(self.easing)

        if pg is None:
            return

        # Update the curve data
        self._generate_curve_data()

        # Update existing curve plot data instead of clearing and recreating
        if self.curve_plot is not None:
            # Update curve data in place
            self.curve_plot.setData(self.curve_data)

        # Update dot position
        self._update_dot_position()
