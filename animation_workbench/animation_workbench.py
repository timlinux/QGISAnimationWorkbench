# coding=utf-8
"""This module has the main GUI interaction logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

# pylint: disable=too-many-lines

# This will make the QGIS use a world projection and then move the center
# of the CRS sequentially to create a spinning globe effect
import os
import tempfile
from functools import partial
from typing import Optional

from .core.video_player import (
    is_multimedia_available,
    open_in_system_player,
    get_system_player_name,
    get_video_playback_instructions,
)

# Import multimedia components with fallback
_multimedia_available, _multimedia_error = is_multimedia_available()
if _multimedia_available:
    from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
    from PyQt5.QtMultimediaWidgets import QVideoWidget
else:
    QMediaContent = None
    QMediaPlayer = None
    QVideoWidget = None
from qgis.PyQt.QtCore import pyqtSlot, QUrl
from qgis.PyQt.QtGui import QIcon, QPixmap, QImage
from qgis.PyQt.QtWidgets import (
    QStyle,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QToolButton,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QTextBrowser,
    QMessageBox,
)
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsExpressionContextUtils,
    QgsProject,
    QgsMapLayerProxyModel,
    QgsReferencedRectangle,
    QgsApplication,
    QgsPropertyCollection,
    QgsWkbTypes,
)
from qgis.gui import QgsExtentWidget, QgsPropertyOverrideButton

from .core import (
    AnimationController,
    InvalidAnimationParametersException,
    MovieCreationTask,
    MovieFormat,
    set_setting,
    setting,
    MapMode,
)
from .core.dependency_checker import DependencyChecker
from .dialog_expression_context_generator import DialogExpressionContextGenerator
from .gui.kartoza_branding import apply_kartoza_styling, KartozaFooter
from .utilities import get_ui_class, resources_path

FORM_CLASS = get_ui_class("animation_workbench_base.ui")

# pylint: disable=too-many-public-methods
class AnimationWorkbench(QDialog, FORM_CLASS):
    """Dialog implementation class Animation Workbench class."""

    # pylint: disable=too-many-locals,too-many-statements
    def __init__(
        self,
        parent=None,
        iface=None,
        render_queue=None,
    ):
        """Constructor for the workbench dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: QGIS Plugin Interface.
        :type iface: QgsInterface

        :param render_queue: Render queue to processing each frame.
        :type render_queue: RenderQueue
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        # Apply Kartoza branding and styling
        apply_kartoza_styling(self)
        self._setup_kartoza_footer()

        self.expression_context_generator = DialogExpressionContextGenerator()
        self.main_tab.setCurrentIndex(0)
        self.extent_group_box = QgsExtentWidget(None, QgsExtentWidget.ExpandedStyle)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.extent_group_box)
        self.extent_widget_container.setLayout(vbox_layout)

        self.render_queue = render_queue
        self.setWindowTitle(self.tr("Animation Workbench"))
        icon = resources_path("icons", "animation-workbench.svg")
        self.setWindowIcon(QIcon(icon))
        self.parent = parent
        self.iface = iface

        self.setup_media_widgets()

        self.data_defined_properties = QgsPropertyCollection()

        self.extent_group_box.setMapCanvas(self.iface.mapCanvas())
        self.scale_range.setMapCanvas(self.iface.mapCanvas())

        self.output_log_text_edit.append("Welcome to the QGIS Animation Workbench")
        self.output_log_text_edit.append("© Tim Sutton, Feb 2022")

        self.run_button = self.button_box.button(QDialogButtonBox.Ok)
        self.run_button.setText("Run")
        self.run_button.setEnabled(False)

        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        self.cancel_button.clicked.connect(self.cancel_processing)

        # Show commands button only shown in debug mode
        debug_mode = int(setting(key="debug_mode", default=0))
        if debug_mode:
            self.debug_button = QPushButton("Show Commands", default=True)
            self.debug_button.clicked.connect(self.debug_button_clicked)
            self.button_box.addButton(self.debug_button, QDialogButtonBox.ActionRole)

        # place where working files are stored
        self.work_directory = tempfile.gettempdir()
        self.frame_filename_prefix = "animation_workbench"
        # place where final products are stored
        output_file = setting(
            key="output_file", default="", prefer_project_setting=True
        )
        if output_file:
            self.movie_file_edit.setText(output_file)

        # Connect output file edit to validation and update initial state
        self.movie_file_edit.textChanged.connect(self._update_run_button_state)
        self._update_run_button_state()

        self.movie_file_button.clicked.connect(self.set_output_name)

        # Work around for not being able to set the layer
        # types allowed in the QgsMapLayerSelector combo
        # See https://github.com/qgis/QGIS/issues/38472#issuecomment-715178025
        self.layer_combo.setFilters(
            QgsMapLayerProxyModel.PointLayer
            | QgsMapLayerProxyModel.LineLayer
            | QgsMapLayerProxyModel.PolygonLayer
        )
        self.layer_combo.layerChanged.connect(self._layer_changed)

        prev_layer_id, _ = QgsProject.instance().readEntry("animation", "layer_id")
        if prev_layer_id:
            layer = QgsProject.instance().mapLayer(prev_layer_id)
            if layer:
                self.layer_combo.setLayer(layer)

        prev_data_defined_properties_xml, _ = QgsProject.instance().readEntry(
            "animation", "data_defined_properties"
        )
        if prev_data_defined_properties_xml:
            doc = QDomDocument()
            doc.setContent(prev_data_defined_properties_xml.encode())
            elem = doc.firstChildElement("data_defined_properties")
            self.data_defined_properties.readXml(
                elem, AnimationController.DYNAMIC_PROPERTIES
            )

        self.extent_group_box.setOutputCrs(QgsProject.instance().crs())
        self.extent_group_box.setOutputExtentFromUser(
            self.iface.mapCanvas().extent(), QgsProject.instance().crs()
        )
        # self.extent_group_box.setOriginalExtnt()

        # Close button action (save state on close)
        self.button_box.button(QDialogButtonBox.Close).clicked.connect(self.close)
        # Connect both accepted signal AND direct click to ensure accept() is called
        self.button_box.accepted.connect(self.accept)
        self.run_button.clicked.connect(self.accept)
        self.button_box.button(QDialogButtonBox.Cancel).setEnabled(False)

        # Used by ffmpeg and convert to set the fps for rendered videos
        self.framerate_spin.setValue(
            int(
                setting(
                    key="frames_per_second",
                    default="10",
                    prefer_project_setting=True,
                )
            )
        )

        # How many seconds to render for each feature pair transition
        self.hover_duration_spin.setValue(
            float(
                setting(
                    key="hover_duration",
                    default="2",
                    prefer_project_setting=True,
                )
            )
        )

        # How many seconds to hover at each feature for
        self.travel_duration_spin.setValue(
            float(
                setting(
                    key="travel_duration",
                    default="2",
                    prefer_project_setting=True,
                )
            )
        )

        self.check_loop_features.setChecked(
            setting(
                key="loop",
                default="false",
                prefer_project_setting=True,
            ).lower()
            == "true"
        )
        # How many frames to render when we are in static mode
        initial_frames = int(
            setting(
                key="frames_for_extent",
                default="10",
                prefer_project_setting=True,
            )
        )
        self.extent_frames_spin.setValue(initial_frames)
        # Connect signals that affect total frame count to update slider range
        self.extent_frames_spin.valueChanged.connect(self._update_preview_frame_range)
        self.framerate_spin.valueChanged.connect(self._update_preview_frame_range)
        self.travel_duration_spin.valueChanged.connect(self._update_preview_frame_range)
        self.hover_duration_spin.valueChanged.connect(self._update_preview_frame_range)
        self.layer_combo.layerChanged.connect(self._update_preview_frame_range)
        self.check_loop_features.toggled.connect(self._update_preview_frame_range)
        # Keep the scales the same if you dont want it to zoom in an out
        max_scale = float(
            setting(
                key="max_scale",
                default="10000000",
                prefer_project_setting=True,
            )
        )
        min_scale = float(
            setting(
                key="min_scale",
                default="25000000",
                prefer_project_setting=True,
            )
        )
        self.scale_range.setScaleRange(min_scale, max_scale)
        # We need to set min and max at the same time to prevent
        # the scale widget from overriding our preferred values
        self.last_preview_image = None

        self.setup_easings()

        self.setup_expression_contexts()

        resolution_string = setting(
            key="resolution", default="map_canvas", prefer_project_setting=True
        )
        if resolution_string == "low_res":
            self.radio_low_res.setChecked(True)
        elif resolution_string == "medium_res":
            self.radio_medium_res.setChecked(True)
        elif resolution_string == "high_res":
            self.radio_high_res.setChecked(True)
        else:  # map_canvas
            self.radio_map_canvas.setChecked(True)

        self.setup_render_modes()

        # Initialize preview frame range based on current settings
        self._update_preview_frame_range()

        self.current_preview_frame_render_job = None
        # Set an initial image in the preview based on the current map
        self.show_preview_for_frame(0)

        self.progress_bar.setValue(0)

        self.reuse_cache.setChecked(False)

        # Video playback stuff - see bottom of file for related methods
        self.current_movie_file = None
        self._multimedia_available = _multimedia_available
        if _multimedia_available:
            self.media_player = QMediaPlayer(
                None, QMediaPlayer.VideoSurface  # .video_preview_widget,
            )
        else:
            self.media_player = None
        self.setup_video_widget()
        # Enable options page on startup
        self.main_tab.setCurrentIndex(0)
        # Enable easing status page on startup
        self.render_queue.status_changed.connect(self.show_status)
        self.render_queue.processing_completed.connect(self.processing_completed)
        self.render_queue.status_message.connect(self.show_message)
        self.render_queue.image_rendered.connect(self.load_image)

        self.movie_task = None

        self.preview_frame_spin.valueChanged.connect(self.show_preview_for_frame)
        self.preview_frame_spin.valueChanged.connect(self._sync_slider_from_spinbox)
        self.preview_frame_slider.valueChanged.connect(self._sync_spinbox_from_slider)
        self.preview_frame_slider.valueChanged.connect(self._update_easing_previews)
        # Only render preview when slider is released (not during drag)
        self.preview_frame_slider.sliderReleased.connect(self._on_slider_released)

        self.register_data_defined_button(
            self.scale_min_dd_btn, AnimationController.PROPERTY_MIN_SCALE
        )
        self.register_data_defined_button(
            self.scale_max_dd_btn, AnimationController.PROPERTY_MAX_SCALE
        )

    def _setup_kartoza_footer(self):
        """Add the Kartoza branding footer to the dialog above the button box."""
        main_layout = self.layout()
        if main_layout and hasattr(self, 'button_box'):
            # Create the footer
            footer = KartozaFooter(self)
            # The layout is a QGridLayout - insert footer before button box
            # Remove button_box, add footer at row 1, add button_box at row 2
            main_layout.removeWidget(self.button_box)
            main_layout.addWidget(footer, 1, 0)
            main_layout.addWidget(self.button_box, 2, 0)

    def setup_video_widget(self):
        """Set up the video widget."""
        layout = QGridLayout(self.video_preview_widget)

        if self._multimedia_available and QVideoWidget is not None:
            # Full video player available
            video_widget = QVideoWidget()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_button.clicked.connect(self.play)
            self.media_player.setVideoOutput(video_widget)
            self.media_player.stateChanged.connect(self.media_state_changed)
            self.media_player.positionChanged.connect(self.position_changed)
            self.media_player.durationChanged.connect(self.duration_changed)
            self.media_player.error.connect(self.handle_video_error)
            layout.addWidget(video_widget, 0, 0)
        else:
            # Multimedia not available - show fallback UI
            self._setup_fallback_video_ui(layout)

        # Add "Open in System Player" button next to play button
        self._add_system_player_button()

    def _setup_fallback_video_ui(self, layout):
        """Set up fallback UI when multimedia is not available."""
        # Create info display
        info_widget = QTextBrowser()
        info_widget.setOpenExternalLinks(True)
        info_widget.setHtml(get_video_playback_instructions())
        layout.addWidget(info_widget, 0, 0)

        # Disable the play button and slider since they won't work
        self.play_button.setEnabled(False)
        self.play_button.setToolTip("Embedded player not available - use 'Open in System Player'")
        self.video_slider.setEnabled(False)

    def _add_system_player_button(self):
        """Add a button to open the video in the system player."""
        # Find the layout containing play_button
        parent_layout = self.play_button.parent().layout()
        if parent_layout is None:
            return

        # Create the system player button
        self.open_system_player_button = QToolButton()
        self.open_system_player_button.setText("Open External")
        self.open_system_player_button.setToolTip(
            f"Open video in {get_system_player_name()}"
        )
        self.open_system_player_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay)
        )
        self.open_system_player_button.setToolButtonStyle(2)  # TextBesideIcon
        self.open_system_player_button.clicked.connect(self._open_in_system_player)
        self.open_system_player_button.setEnabled(False)

        # Insert after play button
        if isinstance(parent_layout, QGridLayout):
            # Find position of play button and add new button
            parent_layout.addWidget(self.open_system_player_button, 2, 2)

    def setup_render_modes(self):
        """Set up the render modes."""
        mode_string = setting(
            key="map_mode", default="sphere", prefer_project_setting=True
        )
        if mode_string == "sphere":
            self.radio_sphere.setChecked(True)
            self.settings_stack.setCurrentIndex(0)
        elif mode_string == "planar":
            self.radio_planar.setChecked(True)
            self.settings_stack.setCurrentIndex(0)
        else:
            self.radio_extent.setChecked(True)
            self.settings_stack.setCurrentIndex(1)

        self.radio_planar.toggled.connect(self.show_non_fixed_extent_settings)
        self.radio_sphere.toggled.connect(self.show_non_fixed_extent_settings)
        self.radio_extent.toggled.connect(self.show_fixed_extent_settings)
        # Update frame range when mode changes
        self.radio_planar.toggled.connect(self._update_preview_frame_range)
        self.radio_sphere.toggled.connect(self._update_preview_frame_range)
        self.radio_extent.toggled.connect(self._update_preview_frame_range)

    def setup_easings(self):
        """Set up the easing options for the gui."""
        # Note: self.pan_easing_widget and zoom_easing_preview are
        # custom widgets implemented in easing_preview.py
        # and added in designer as promoted widgets.
        self.pan_easing_widget.set_checkbox_label("Enable Pan Easing")
        pan_easing_name = setting(
            key="pan_easing", default="Linear", prefer_project_setting=True
        )
        self.pan_easing_widget.set_preview_color("#ffff00")
        self.pan_easing_widget.set_easing_by_name(pan_easing_name)
        if (
            int(
                setting(
                    key="enable_pan_easing",
                    default=0,
                    prefer_project_setting=True,
                )
            )
            == 0
        ):
            self.pan_easing_widget.disable()
        else:
            self.pan_easing_widget.enable()

        self.zoom_easing_widget.set_checkbox_label("Enable Zoom Easing")
        zoom_easing_name = setting(
            key="zoom_easing", default="Linear", prefer_project_setting=True
        )
        self.zoom_easing_widget.set_preview_color("#0000ff")
        self.zoom_easing_widget.set_easing_by_name(zoom_easing_name)
        if (
            int(
                setting(
                    key="enable_zoom_easing",
                    default=0,
                    prefer_project_setting=True,
                )
            )
            == 0
        ):
            self.zoom_easing_widget.disable()
        else:
            self.zoom_easing_widget.enable()

    def setup_media_widgets(self):
        """Set up the media widgets."""
        self.intro_media.set_media_type("images")
        self.outro_media.set_media_type("images")
        self.music_media.set_media_type("sounds")

        self.intro_media.from_json(
            setting(key="intro_media", default="{}", prefer_project_setting=True)
        )
        self.outro_media.from_json(
            setting(key="outro_media", default="{}", prefer_project_setting=True)
        )
        self.music_media.from_json(
            setting(key="music_media", default="{}", prefer_project_setting=True)
        )

    def setup_expression_contexts(self):
        """Set up all the expression context variables."""
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), "frames_per_feature", 0
        )
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), "current_frame_for_feature", 0
        )
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), "dwell_frames_per_feature", 0
        )
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), "current_feature_id", 0
        )
        # None, Panning, Hovering
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), "current_animation_action", "None"
        )

        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), "total_frame_count", "None"
        )

    def debug_button_clicked(self):
        """Show the different ffmpeg commands that will be run to process the images."""
        self.output_log_text_edit.clear()
        self.intro_media.set_output_resolution(self.output_mode_name())
        self.outro_media.set_output_resolution(self.output_mode_name())
        self.music_media.set_output_resolution(self.output_mode_name())
        intro_command = self.intro_media.video_command()
        outro_command = self.outro_media.video_command()
        music_command = self.music_media.video_command()
        if intro_command:
            self.output_log_text_edit.append(" ".join(intro_command))
        if outro_command:
            self.output_log_text_edit.append(" ".join(outro_command))
        if music_command:
            self.output_log_text_edit.append(" ".join(music_command))

    def close(self):  # pylint: disable=missing-function-docstring
        """Handler for the close button."""
        try:
            self.save_state()
        except Exception as e:
            # Don't let save_state failure prevent closing
            self.output_log_text_edit.append(f"Warning: Could not save state: {e}")
        self.reject()

    def closeEvent(
        self, event
    ):  # pylint: disable=missing-function-docstring,unused-argument
        self.save_state()
        self.reject()

    def _layer_changed(self, layer):
        """
        Triggered when the layer is changed
        """
        self.expression_context_generator.set_layer(layer)

        buttons = self.findChildren(QgsPropertyOverrideButton)
        for button in buttons:
            button.setVectorLayer(layer)

    def register_data_defined_button(self, button, property_key: int):
        """
        Registers a new data defined button, linked to the given property key (see values in AnimationController)
        """
        button.init(
            property_key,
            self.data_defined_properties,
            AnimationController.DYNAMIC_PROPERTIES,
            None,
            False,
        )
        button.changed.connect(self._update_property)
        button.registerExpressionContextGenerator(self.expression_context_generator)
        button.setVectorLayer(self.layer_combo.currentLayer())

    def _update_property(self):
        """
        Triggered when a property override button value is changed
        """
        button = self.sender()
        self.data_defined_properties.setProperty(
            button.propertyKey(), button.toProperty()
        )

    def update_data_defined_button(self, button):
        """
        Updates the current state of a property override button to reflect the current
        property value
        """
        if button.propertyKey() < 0:
            return

        button.blockSignals(True)
        button.setToProperty(
            self.data_defined_properties.property(button.propertyKey())
        )
        button.blockSignals(False)

    def show_message(self, message: str):
        """
        Shows a log message in the dialog
        """
        self.output_log_text_edit.append(message)

    def show_non_fixed_extent_settings(self):
        """
        Switches to the non-fixed extent settings page
        """
        self.settings_stack.setCurrentIndex(0)

    def show_fixed_extent_settings(self):
        """
        Switches to the fixed extent settings page
        """
        self.settings_stack.setCurrentIndex(1)

    def show_status(self):
        """
        Display the size of the QgsTaskManager queue.

        :returns: None
        """
        self.active_lcd.display(self.render_queue.active_queue_size())
        self.total_tasks_lcd.display(self.render_queue.total_queue_size)
        self.remaining_features_lcd.display(
            self.render_queue.total_feature_count
            - self.render_queue.completed_feature_count
        )
        self.completed_tasks_lcd.display(self.render_queue.total_completed)
        self.completed_features_lcd.display(self.render_queue.completed_feature_count)

        self.progress_bar.setValue(self.render_queue.total_completed)

    def _update_run_button_state(self):
        """Update Run button and output file field based on whether output is set."""
        output_file = self.movie_file_edit.text().strip()
        has_output = bool(output_file)

        # Update Run button state and tooltip
        self.run_button.setEnabled(has_output)
        if has_output:
            self.run_button.setToolTip("Start rendering the animation")
            self.movie_file_edit.setStyleSheet("")
        else:
            self.run_button.setToolTip("Output file not set - click '...' to choose")
            self.movie_file_edit.setStyleSheet(
                "QLineEdit { border: 2px solid #e74c3c; background-color: #fdf2f2; }"
            )

    def set_output_name(self):
        """
        Asks the user for the output video file path
        """
        dialog_title = "Save video"

        output_directory = os.path.dirname(self.movie_file_edit.text())
        if not output_directory:
            output_directory = self.work_directory

        # noinspection PyCallByClass,PyTypeChecker
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            dialog_title,
            os.path.join(output_directory, "qgis_animation.mp4"),
            "Video (*.mp4);;GIF (*.gif)",
        )
        if file_path:
            self.movie_file_edit.setText(file_path)

    def choose_music_file(self):
        """
        Asks the user for the music file path
        """
        # Popup a dialog to request the filename for music backing track
        dialog_title = "Music for video"

        # noinspection PyCallByClass,PyTypeChecker
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            dialog_title,
            self.music_file_edit.text(),
            "Mp3 (*.mp3);;Wav (*.wav)",
        )
        if file_path is None or file_path == "":
            return
        self.music_file_edit.setText(file_path)

    def save_state(self):
        """
        We save some project settings to both QSettings AND the current project,
        others just to the current project, others just to settings...
        """
        set_setting(
            key="frames_per_second",
            value=self.framerate_spin.value(),
            store_in_project=True,
        )
        set_setting(
            key="intro_media", value=self.intro_media.to_json(), store_in_project=True
        )
        set_setting(
            key="outro_media", value=self.outro_media.to_json(), store_in_project=True
        )
        set_setting(
            key="music_media", value=self.music_media.to_json(), store_in_project=True
        )

        if self.radio_low_res.isChecked():
            set_setting(key="resolution", value="low_res", store_in_project=True)
        elif self.radio_medium_res.isChecked():
            set_setting(key="resolution", value="medium_res", store_in_project=True)
        elif self.radio_high_res.isChecked():
            set_setting(key="resolution", value="high_res", store_in_project=True)
        else:
            set_setting(key="resolution", value="map_canvas", store_in_project=True)

        if self.radio_sphere.isChecked():
            set_setting(key="map_mode", value="sphere", store_in_project=True)
        elif self.radio_planar.isChecked():
            set_setting(key="map_mode", value="planar", store_in_project=True)
        else:
            set_setting(key="map_mode", value="fixed_extent", store_in_project=True)
        set_setting(
            key="hover_duration",
            value=self.hover_duration_spin.value(),
            store_in_project=True,
        )
        set_setting(
            key="travel_duration",
            value=self.travel_duration_spin.value(),
            store_in_project=True,
        )
        set_setting(
            key="loop",
            value="true" if self.check_loop_features.isChecked() else "false",
            store_in_project=True,
        )
        set_setting(
            key="frames_for_extent",
            value=self.extent_frames_spin.value(),
            store_in_project=True,
        )
        set_setting(
            key="max_scale",
            value=str(self.scale_range.maximumScale()),
            store_in_project=True,
        )
        set_setting(
            key="min_scale",
            value=str(self.scale_range.minimumScale()),
            store_in_project=True,
        )
        set_setting(
            key="enable_pan_easing",
            value=1 if self.pan_easing_widget.is_enabled() else 0,
            store_in_project=True,
        )
        set_setting(
            key="enable_zoom_easing",
            value=1 if self.zoom_easing_widget.is_enabled() else 0,
            store_in_project=True,
        )
        set_setting(
            key="pan_easing",
            value=self.pan_easing_widget.easing_name() or "Linear",
            store_in_project=True,
        )
        set_setting(
            key="zoom_easing",
            value=self.zoom_easing_widget.easing_name() or "Linear",
            store_in_project=True,
        )
        set_setting(
            key="output_file",
            value=self.movie_file_edit.text(),
            store_in_project=True,
        )

        # only saved to project
        if self.layer_combo.currentLayer():
            QgsProject.instance().writeEntry(
                "animation", "layer_id", self.layer_combo.currentLayer().id()
            )
        else:
            QgsProject.instance().removeEntry("animation", "layer_id")
        temp_doc = QDomDocument()
        dd_elem = temp_doc.createElement("data_defined_properties")
        self.data_defined_properties.writeXml(
            dd_elem, AnimationController.DYNAMIC_PROPERTIES
        )
        temp_doc.appendChild(dd_elem)
        QgsProject.instance().writeEntry(
            "animation", "data_defined_properties", temp_doc.toString()
        )

    # Prevent the slot being called twice
    @pyqtSlot()
    def accept(self):
        """Process the animation sequence.

        .. note:: This is called on OK click.
        """
        try:
            # Check if output file is specified
            output_file = self.movie_file_edit.text().strip()
            if not output_file:
                QMessageBox.warning(
                    self,
                    "Output File Required",
                    "Please specify an output file path before running.\n\n"
                    "Click the '...' button next to the output field to choose a location."
                )
                return

            # Pre-flight dependency check - verify tools are available BEFORE rendering
            is_gif = self.radio_gif.isChecked()
            valid, tool_path = DependencyChecker.validate_movie_export(
                for_gif=is_gif,
                parent=self
            )
            if not valid:
                self.output_log_text_edit.append(
                    "Export cancelled: Required tools not found. "
                    "Please install the missing dependencies and try again."
                )
                return
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during pre-flight checks:\n{str(e)}"
            )
            return

        # Enable progress page on accept
        self.main_tab.setCurrentIndex(5)
        # Image preview page
        self.preview_stack.setCurrentIndex(0)
        # Enable queue status page
        # set parameter from dialog

        if not self.reuse_cache.isChecked():
            os.system("rm %s/%s*" % (self.work_directory, self.frame_filename_prefix))

        self.save_state()

        self.render_queue.reset()
        self.last_preview_image = None
        self.output_log_text_edit.clear()
        self.output_log_text_edit.append("Preparing animation run. Please wait.")
        controller = self.create_controller()
        if not controller:
            return

        controller.reuse_cache = self.reuse_cache.isChecked()

        self.render_queue.set_annotations(
            QgsProject.instance().annotationManager().annotations()
        )
        self.render_queue.set_decorations(self.iface.activeDecorations())

        self.output_log_text_edit.append(
            "Generating {} frames".format(controller.total_frame_count)
        )
        self.progress_bar.setMaximum(controller.total_frame_count)
        self.progress_bar.setValue(0)

        def log_message(message):
            self.output_log_text_edit.append(message)

        controller.normal_message.connect(log_message)
        if int(setting(key="verbose_mode", default=0)):
            controller.verbose_message.connect(log_message)

        self.render_queue.total_feature_count = controller.total_feature_count

        # this needs reworking!
        self.render_queue.frames_per_feature = (
            controller.travel_duration + controller.hover_duration
        ) * controller.frame_rate

        for job in controller.create_jobs():
            self.output_log_text_edit.append(job.file_name)
            self.render_queue.add_job(job)

        self.button_box.button(QDialogButtonBox.Cancel).setEnabled(True)
        # Now all the tasks are prepared, start the render_queue processing
        self.render_queue.start_processing()

    def cancel_processing(self):
        """
        Cancels current processing
        """
        self.button_box.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.render_queue.cancel_processing()
        # Enable progress page
        self.main_tab.setCurrentIndex(0)

    def create_controller(self) -> Optional[AnimationController]:
        """
        Creates a new animation controller based on the state of the dialog
        """
        if self.radio_sphere.isChecked():
            map_mode = MapMode.SPHERE
        elif self.radio_planar.isChecked():
            map_mode = MapMode.PLANAR
        else:
            map_mode = MapMode.FIXED_EXTENT

        if map_mode != MapMode.FIXED_EXTENT:
            if not self.layer_combo.currentLayer():
                self.output_log_text_edit.append(
                    "Cannot generate sequence without choosing a layer"
                )
                return None

            layer_type = QgsWkbTypes.displayString(
                self.layer_combo.currentLayer().wkbType()
            )
            layer_name = self.layer_combo.currentLayer().name()
            self.output_log_text_edit.append(
                "Generating flight path for %s layer: %s" % (layer_type, layer_name)
            )

        if map_mode == MapMode.FIXED_EXTENT:
            controller = AnimationController.create_fixed_extent_controller(
                map_settings=self.iface.mapCanvas().mapSettings(),
                output_mode=self.output_mode_ffmpeg(),
                feature_layer=self.layer_combo.currentLayer() or None,
                output_extent=QgsReferencedRectangle(
                    self.extent_group_box.outputExtent(),
                    self.extent_group_box.outputCrs(),
                ),
                total_frames=self.extent_frames_spin.value(),
                frame_rate=self.framerate_spin.value(),
            )
        else:
            try:
                controller = AnimationController.create_moving_extent_controller(
                    map_settings=self.iface.mapCanvas().mapSettings(),
                    output_mode=self.output_mode_ffmpeg(),
                    mode=map_mode,
                    feature_layer=self.layer_combo.currentLayer(),
                    travel_duration=self.travel_duration_spin.value(),
                    hover_duration=self.hover_duration_spin.value(),
                    min_scale=self.scale_range.minimumScale(),
                    max_scale=self.scale_range.maximumScale(),
                    loop=self.check_loop_features.isChecked(),
                    pan_easing=self.pan_easing_widget.get_easing()
                    if self.pan_easing_widget.is_enabled()
                    else None,
                    zoom_easing=self.zoom_easing_widget.get_easing()
                    if self.zoom_easing_widget.is_enabled()
                    else None,
                    frame_rate=self.framerate_spin.value(),
                )
            except InvalidAnimationParametersException as e:
                self.output_log_text_edit.append(f"Processing halted: {e}")
                return None

        controller.data_defined_properties = QgsPropertyCollection(
            self.data_defined_properties
        )
        return controller

    def processing_completed(self, success: bool):
        """Run after all processing is done to generate gif or mp4.

        .. note:: This called by process_more_tasks when all tasks are complete.
        """
        if not success:
            self.output_log_text_edit.append("Canceled by user")
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            self.button_box.button(QDialogButtonBox.Cancel).setEnabled(False)
            return
        # We assemble first commands needed to make the pieces of the movie
        self.intro_media.set_output_resolution(self.output_mode_name())
        self.outro_media.set_output_resolution(self.output_mode_name())
        self.music_media.set_output_resolution(self.output_mode_name())
        intro_command = self.intro_media.video_command()
        outro_command = self.outro_media.video_command()
        music_command = self.music_media.video_command()
        output_mode = self.output_mode_ffmpeg()
        self.movie_task = MovieCreationTask(
            output_file=self.movie_file_edit.text(),
            output_mode=output_mode,
            intro_command=intro_command,
            outro_command=outro_command,
            music_command=music_command,
            output_format=MovieFormat.GIF
            if self.radio_gif.isChecked()
            else MovieFormat.MP4,
            work_directory=self.work_directory,
            frame_filename_prefix=self.frame_filename_prefix,
            framerate=self.framerate_spin.value(),
        )

        def log_message(message):
            self.output_log_text_edit.append(message)

        def show_movie(movie_file: str):
            # Store the movie file path for system player fallback
            self.current_movie_file = movie_file

            # Video preview page
            self.main_tab.setCurrentIndex(5)
            self.preview_stack.setCurrentIndex(1)

            # Enable system player button
            if hasattr(self, 'open_system_player_button'):
                self.open_system_player_button.setEnabled(True)

            if self._multimedia_available and self.media_player is not None:
                # Try embedded player
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(movie_file)))
                self.play_button.setEnabled(True)
                self.play()
            else:
                # Multimedia not available - offer to open in system player
                self.output_log_text_edit.append(
                    f"Video created successfully: {movie_file}"
                )
                self.output_log_text_edit.append(
                    "Embedded player not available. Click 'Open External' to view."
                )
                # Auto-open in system player as a convenience
                self._open_in_system_player()

        def cleanup_movie_task():
            self.movie_task = None

            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)

        self.movie_task.message.connect(log_message)
        self.movie_task.movie_created.connect(show_movie)

        # todo - show a message based on success/fail
        self.movie_task.taskCompleted.connect(cleanup_movie_task)
        self.movie_task.taskTerminated.connect(cleanup_movie_task)

        QgsApplication.taskManager().addTask(self.movie_task)

        self.button_box.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.main_tab.setCurrentIndex(5)

    def output_mode_ffmpeg(self):
        """Get the output mode (resolution) in ffmpeg format.

        Will map to 480p, 720p, 1080p, etc. or canvas size.
        """
        output_mode = None
        if self.radio_low_res.isChecked():
            output_mode = "1280:720"
        elif self.radio_medium_res.isChecked():
            output_mode = "1920:1080"
        elif self.radio_high_res.isChecked():
            output_mode = "3840:2160"
        else:  # Map canvas size
            map_settings = self.iface.mapCanvas().mapSettings()
            size = map_settings.outputSize()
            output_mode = "%s:%s" % (size.width(), size.height())
        return output_mode

    def output_mode_name(self):
        """Return the output mode name like 1080p, 720p etc."""
        output_mode = None
        if self.radio_low_res.isChecked():
            output_mode = "720p"
        elif self.radio_medium_res.isChecked():
            output_mode = "1080p"
        elif self.radio_high_res.isChecked():
            output_mode = "4k"
        else:  # Map canvas size
            map_settings = self.iface.mapCanvas().mapSettings()
            size = map_settings.outputSize()
            output_mode = "%s:%s" % (size.width(), size.height())

        return output_mode

    def show_preview_for_frame(self, frame: int):
        """
        Shows a preview image for a specific frame
        """
        if self.radio_sphere.isChecked() or self.radio_planar.isChecked():
            if not self.layer_combo.currentLayer():
                self.output_log_text_edit.append(
                    "Cannot generate sequence without choosing a layer"
                )
                return
        if self.current_preview_frame_render_job:
            self.current_preview_frame_render_job.cancel()
            self.current_preview_frame_render_job = None

        controller = self.create_controller()
        job = controller.create_job_for_frame(frame)
        if not job:
            return

        def update_preview_image(file_name):
            if not self.current_preview_frame_render_job:
                return

            image = QImage(file_name)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                self.user_defined_preview.setPixmap(pixmap)
                self.current_frame_preview.setPixmap(pixmap)

            self.current_preview_frame_render_job = None

        job.file_name = "/tmp/tmp_image.png"
        self.current_preview_frame_render_job = job.create_task()

        self.current_preview_frame_render_job.taskCompleted.connect(
            partial(update_preview_image, file_name=job.file_name)
        )
        self.current_preview_frame_render_job.taskTerminated.connect(
            partial(update_preview_image, file_name=job.file_name)
        )

        QgsApplication.taskManager().addTask(self.current_preview_frame_render_job)

    def _sync_slider_from_spinbox(self, value: int):
        """Sync the slider position when spinbox value changes."""
        max_frames = self.extent_frames_spin.value()
        if max_frames > 0:
            self.preview_frame_slider.blockSignals(True)
            self.preview_frame_slider.setMaximum(max_frames)
            self.preview_frame_slider.setValue(value)
            self.preview_frame_slider.blockSignals(False)

    def _sync_spinbox_from_slider(self, value: int):
        """Sync the spinbox value when slider position changes.

        Note: This does NOT trigger a preview render - that happens
        via _on_slider_released to avoid rendering during drag.
        """
        self.preview_frame_spin.blockSignals(True)
        self.preview_frame_spin.setValue(value)
        self.preview_frame_spin.blockSignals(False)

    def _on_slider_released(self):
        """Render preview when slider drag ends."""
        frame = self.preview_frame_slider.value()
        self.show_preview_for_frame(frame)

    def _update_easing_previews(self, frame: int):
        """Update easing preview dot positions based on current frame."""
        max_frames = self.extent_frames_spin.value()
        if max_frames > 0:
            progress = frame / max_frames
            self.pan_easing_widget.set_progress(progress)
            self.zoom_easing_widget.set_progress(progress)

    def _calculate_total_frames(self) -> int:
        """Calculate the total frame count based on current settings.

        For fixed extent mode: uses extent_frames_spin value.
        For sphere/planar mode: matches AnimationController formula:
            (feature_count * hover_frames) + (travel_segments * travel_frames)
        Where travel_segments = feature_count if loop else (feature_count - 1).
        This accounts for whether the animation returns to the first feature.
        """
        if self.radio_extent.isChecked():
            return self.extent_frames_spin.value()

        # Sphere or planar mode
        layer = self.layer_combo.currentLayer()
        if not layer:
            return 1

        fps = self.framerate_spin.value()
        travel_duration = self.travel_duration_spin.value()
        hover_duration = self.hover_duration_spin.value()
        feature_count = layer.featureCount()
        loop = self.check_loop_features.isChecked()

        if feature_count == 0:
            return 1

        hover_frames = fps * hover_duration
        travel_frames = fps * travel_duration
        # When looping, we travel back to first feature; otherwise one less travel segment
        travel_segments = feature_count if loop else max(0, feature_count - 1)

        total_frames = int((feature_count * hover_frames) + (travel_segments * travel_frames))
        return max(1, total_frames)

    def _update_preview_frame_range(self, *args):
        """Update the slider, spinbox, and total frames label based on calculated frame count."""
        max_value = self._calculate_total_frames()
        self.preview_frame_slider.setMaximum(max_value)
        self.preview_frame_spin.setMaximum(max_value)
        self.total_frames_label.setText(f"/ {max_value}")
        # Also update easing previews for current position
        current = self.preview_frame_slider.value()
        if max_value > 0:
            progress = current / max_value
            self.pan_easing_widget.set_progress(progress)
            self.zoom_easing_widget.set_progress(progress)

    def load_image(self, name):
        """
        Loads a preview image
        """
        if self.last_preview_image is not None and self.last_preview_image > name:
            # Images won't necessarily be rendered in order, so only update the
            # preview image if the rendered image is from later in the animation
            # vs the one we are currently showing. Avoids the preview jumping
            # forward and backward and zooming/in out in unpredictable patterns
            return

        self.last_preview_image = name
        # Load the preview with the named image file
        if True:  # pylint: disable=using-constant-test
            with open(name, "rb") as image_file:
                content = image_file.read()
                image = QImage()
                image.loadFromData(content)
                pixmap = QPixmap.fromImage(image)
                self.user_defined_preview.setPixmap(pixmap)
                self.current_frame_preview.setPixmap(pixmap)
        else:  # this should be an except, but I'm not sure what the specific exception was supposed to be!
            pass

    # Video Playback Methods
    def play(self):
        """
        Plays the video preview.

        Falls back to system player if embedded player is not available.
        """
        if not self._multimedia_available or self.media_player is None:
            # Fallback to system player
            self._open_in_system_player()
            return

        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self, state):  # pylint: disable=unused-argument
        """
        Called when the media state is changed
        """
        if not self._multimedia_available or self.media_player is None:
            return

        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        """
        Called when the video position changes
        """
        self.video_slider.setValue(position)

    def duration_changed(self, duration):
        """
        Called when the video duration changes
        """
        self.video_slider.setRange(0, duration)

    def set_position(self, position):
        """
        Sets the position of the playing video
        """
        if self._multimedia_available and self.media_player is not None:
            self.media_player.setPosition(position)

    def handle_video_error(self):
        """
        Handles errors when playing videos.

        When the embedded player fails, offers to open in system player.
        """
        self.play_button.setEnabled(False)
        error_string = self.media_player.errorString() if self.media_player else "Unknown error"
        self.output_log_text_edit.append(f"Video playback error: {error_string}")
        self.output_log_text_edit.append(
            "Click 'Open External' to view in your system media player."
        )

        # Offer to open in system player
        if self.current_movie_file:
            reply = QMessageBox.question(
                self,
                "Video Playback Error",
                f"The embedded video player encountered an error:\n{error_string}\n\n"
                f"Would you like to open the video in {get_system_player_name()}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._open_in_system_player()

    def _open_in_system_player(self):
        """Open the current movie file in the system's default media player."""
        if not self.current_movie_file:
            QMessageBox.warning(
                self,
                "No Video Available",
                "No video file is available to open."
            )
            return

        success, error = open_in_system_player(self.current_movie_file)
        if success:
            self.output_log_text_edit.append(
                f"Opened video in {get_system_player_name()}"
            )
        else:
            QMessageBox.warning(
                self,
                "Could Not Open Video",
                f"Failed to open video in system player:\n{error}\n\n"
                f"The video file is located at:\n{self.current_movie_file}"
            )
