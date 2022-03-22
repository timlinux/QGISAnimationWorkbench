# coding=utf-8
"""This module has the main GUI interaction logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

# This will make the QGIS use a world projection and then move the center
# of the CRS sequentially to create a spinning globe effect
from doctest import debug_script
import os
import timeit
import tempfile
from enum import Enum

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA

from qgis.PyQt.QtCore import (
    pyqtSlot,
    QUrl
)
from qgis.PyQt.QtGui import (
    QIcon,
    QPixmap,
    QImage
)
from qgis.PyQt.QtWidgets import (
    QStyle,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QGridLayout
)

from PyQt5.QtMultimedia import (
    QMediaContent,
    QMediaPlayer
)
from PyQt5.QtMultimediaWidgets import QVideoWidget

from qgis.core import (
    QgsPointXY,
    QgsWkbTypes,
    QgsExpressionContextUtils,
    QgsProject,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsMapLayerProxyModel,
    QgsReferencedRectangle
)
from .settings import set_setting, setting
from .utilities import get_ui_class, which, resources_path


class MapMode(Enum):
    SPHERE = 1  # CRS will be manipulated to create a spinning globe effect
    PLANAR = 2  # CRS will not be altered, extents will as we pan and zoom
    FIXED_EXTENT = 3  # EASING and ZOOM disabled, extent stays in place


FORM_CLASS = get_ui_class('animation_workbench_base.ui')


class AnimationWorkbench(QDialog, FORM_CLASS):
    """Dialog implementation class Animation Workbench class."""

    def __init__(self, parent=None, iface=None, render_queue=None):
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
        self.render_queue = render_queue
        self.setWindowTitle(self.tr('Animation Workbench'))
        icon = resources_path(
            'img', 'icons', 'animation-workshop.svg')
        self.setWindowIcon(QIcon(icon))
        self.parent = parent
        self.iface = iface

        self.output_log_text_edit.append(
            'Welcome to the QGIS Animation Workbench')
        self.output_log_text_edit.append(
            '© Tim Sutton, Feb 2022')

        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        # ok_button.clicked.connect(self.accept)
        ok_button.setText('Run')
        ok_button.setEnabled(False)

        # place where working files are stored
        self.work_directory = tempfile.gettempdir()
        self.frame_filename_prefix = 'animation_workbench'
        # place where final products are stored
        self.output_directory = None
        self.output_file = setting(key='output_file', default='')

        if self.output_file != '':
            self.file_edit.setText(self.output_file)
            self.output_directory = os.path.dirname(self.output_file)
            ok_button.setEnabled(True)
        self.file_button.clicked.connect(
            self.set_output_name)
        self.file_edit.textChanged.connect(
            self.output_name_changed)
        # Work around for not being able to set the layer
        # types allowed in the QgsMapLayerSelector combo
        # See https://github.com/qgis/QGIS/issues/38472#issuecomment-715178025
        self.layer_combo.setFilters(
            QgsMapLayerProxyModel.PointLayer |
            QgsMapLayerProxyModel.LineLayer |
            QgsMapLayerProxyModel.PolygonLayer)

        self.extent_group_box.setOutputCrs(
            QgsProject.instance().crs()
        )
        self.extent_group_box.setOutputExtentFromUser(
            self.iface.mapCanvas().extent(),
            QgsProject.instance().crs())
        # self.extent_group_box.setOriginalExtnt()
        # Set up things for context help
        self.help_button = self.button_box.button(
            QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)

        # Close button action
        close_button = self.button_box.button(
            QDialogButtonBox.Close)
        close_button.clicked.connect(self.close)
        # Fix ends

        # Used by ffmpeg and convert to set the fps for rendered videos
        self.frames_per_second = int(
            setting(key='frames_per_second', default='90'))
        self.framerate_spin.setValue(self.frames_per_second)
        # How many frames to render for each feature pair transition
        # The output is generated at e.g. 30fps so choosing 30
        # would fly to each feature for 1s
        # You can then use the 'current_feature' project variable
        # to determine the current feature id
        # and the 'feature_frame' project variable to determine
        # the frame number for the current feature based on frames_for_interval

        self.frames_per_feature = int(
            setting(key='frames_per_feature', default='90'))
        self.feature_frames_spin.setValue(self.frames_per_feature)

        # How many frames to dwell at each feature for (output at e.g. 30fps)
        self.dwell_frames = int(
            setting(key='dwell_frames', default='30'))
        self.hover_frames_spin.setValue(self.dwell_frames)
        # How many frames to render when we are in static mode
        self.frames_for_extent = int(
            setting(key='frames_for_extent', default='90'))
        self.extent_frames_spin.setValue(self.frames_for_extent)
        # Keep the scales the same if you dont want it to zoom in an out
        self.max_scale = int(setting(key='max_scale', default='10000000'))
        self.scale_range.setMaximumScale(self.max_scale)
        self.min_scale = int(setting(key='min_scale', default='25000000'))
        self.scale_range.setMinimumScale(self.min_scale)

        # Stores the current image in the entire set
        self.image_counter = None
        # Stores the total number of frames in the whole animation
        self.total_frame_count = None

        # Note: self.pan_easing_widget and zoom_easing_preview are
        # custom widgets implemented in easing_preview.py
        # and added in designer as promoted widgets.
        self.pan_easing_widget.set_checkbox_label('Enable Pan Easing')
        pan_easing_name = setting(key='pan_easing', default='Linear')
        self.pan_easing_widget.set_preview_color('#00ff00')
        self.pan_easing_widget.set_easing_by_name(pan_easing_name)
        if setting(key='enable_pan_easing', default='false') == 'false':
            self.pan_easing_widget.disable()
        else:
            self.pan_easing_widget.enable()
        self.pan_easing = self.pan_easing_widget.get_easing()
        self.pan_easing_widget.easing_changed_signal.connect(
            self.pan_easing_changed
        )

        self.zoom_easing_widget.set_checkbox_label('Enable Zoom Easing')
        zoom_easing_name = setting(key='zoom_easing', default='Linear')
        self.zoom_easing_widget.set_preview_color('#0000ff')
        self.zoom_easing_widget.set_easing_by_name(zoom_easing_name)
        if setting(key='enable_zoom_easing', default='false') == 'false':
            self.zoom_easing_widget.disable()
        else:
            self.zoom_easing_widget.enable()

        self.zoom_easing = self.zoom_easing_widget.get_easing()
        self.zoom_easing_widget.easing_changed_signal.connect(
            self.zoom_easing_changed
        )

        self.previous_feature = None

        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'frames_per_feature', 0)
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_frame_for_feature', 0)
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_feature_id', 0)
        # None, Panning, Hovering
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_animation_action', 'None')

        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_frame', 'None')
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'total_frame_count', 'None')

        self.map_mode = None
        mode_string = setting(key='map_mode', default='sphere')
        if mode_string == 'sphere':
            self.map_mode == MapMode.SPHERE
            self.radio_sphere.setChecked(True)
            self.status_stack.setCurrentIndex(0)
            self.settings_stack.setCurrentIndex(0)
        elif mode_string == 'planar':
            self.map_mode == MapMode.PLANAR
            self.radio_planar.setChecked(True)
            self.status_stack.setCurrentIndex(0)
            self.settings_stack.setCurrentIndex(0)
        else:
            self.map_mode == MapMode.FIXED_EXTENT
            self.radio_extent.setChecked(True)
            self.status_stack.setCurrentIndex(1)
            self.settings_stack.setCurrentIndex(1)

        self.radio_planar.toggled.connect(
            self.show_non_fixed_extent_settings
        )
        self.radio_sphere.toggled.connect(
            self.show_non_fixed_extent_settings
        )
        self.radio_extent.toggled.connect(
            self.show_fixed_extent_settings
        )

        # Set an initial image in the preview based on the current map
        image = self.render_queue.render_image()
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self.current_frame_preview.setPixmap(pixmap)

        self.progress_bar.setValue(0)
        # This will be half the number of frames per feature
        # so that the first half of the journey is flying up
        # away from the last feature and the next half of the
        # journey is flying down towards the next feature.
        self.frames_to_zenith = None

        reuse_cache = setting(key='reuse_cache', default='false')
        if reuse_cache == 'false':
            self.reuse_cache.setChecked(False)
        else:
            self.reuse_cache.setChecked(True)

        # Video playback stuff - see bottom of file for related methods
        self.media_player = QMediaPlayer(
            None,  # .video_preview_widget,
            QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget()
        # self.video_page.replaceWidget(self.video_preview_widget,video_widget)
        self.play_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)
        self.media_player.setVideoOutput(video_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.error.connect(self.handle_video_error)
        layout = QGridLayout(self.video_preview_widget)
        layout.addWidget(video_widget)
        # Enable image preview page on startup
        self.preview_stack.setCurrentIndex(0)
        # Enable easing status page on startup
        self.status_stack.setCurrentIndex(0)
        self.render_queue.status_changed.connect(
            self.show_status)
        self.render_queue.processing_completed.connect(
            self.processing_completed)
        self.render_queue.status_message.connect(
            self.show_message)
        self.render_queue.image_rendered.connect(
            self.load_image)

    def close(self):
        self.save_state()
        self.reject()

    def show_message(self, message):
        self.output_log_text_edit.append(message)

    # slot
    def pan_easing_changed(self, easing):
        self.output_log_text_edit.append(
            'Pan easing set to: %s' %
            self.pan_easing_widget.easing_name())
        self.pan_easing = easing

    # slot
    def zoom_easing_changed(self, easing):
        self.output_log_text_edit.append(
            'Zoom easing set to: %s' %
            self.pan_easing_widget.easing_name())
        self.zoom_easing = easing

    def show_non_fixed_extent_settings(self):

        self.settings_stack.setCurrentIndex(0)

    def show_fixed_extent_settings(self):

        self.settings_stack.setCurrentIndex(1)

    def show_status(self):
        """
        Display the size of the QgsTaskManager queue.

        :returns: None
        """
        self.active_lcd.display(
            self.render_queue.active_queue_size)
        self.total_tasks_lcd.display(
            self.render_queue.total_queue_size
        )
        self.remaining_features_lcd.display(
            self.render_queue.total_feature_count -
            self.render_queue.completed_feature_count)
        self.completed_tasks_lcd.display(
            self.render_queue.total_completed
        )
        self.completed_features_lcd.display(
            self.render_queue.completed_feature_count)

    def output_name_changed(self, path):
        # File name line edit changed slot
        self.output_file = path
        self.output_directory = os.path.dirname(self.output_file)
        set_setting(key='output_file', value=path)

    def set_output_name(self):
        # Popup a dialog to request the filename if scenario_file_path = None
        dialog_title = 'Save video'
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        ok_button.setText('Run')
        ok_button.setEnabled(False)

        if self.output_directory is None:
            self.output_directory = self.work_directory
        # noinspection PyCallByClass,PyTypeChecker
        file_path, __ = QFileDialog.getSaveFileName(
            self,
            dialog_title,
            os.path.join(self.output_directory, 'qgis_animation.mp4'),
            "Video (*.mp4);;GIF (*.gif)")
        if file_path is None or file_path == '':
            ok_button.setEnabled(False)
            return
        ok_button.setEnabled(True)
        self.output_directory = os.path.dirname(file_path)
        self.output_file = file_path
        self.file_edit.setText(file_path)

    def save_state(self):

        self.frames_per_second = self.framerate_spin.value()
        set_setting(key='frames_per_second', value=self.frames_per_second)

        if self.radio_sphere.isChecked():
            set_setting(key='map_mode', value='sphere')
        elif self.radio_planar.isChecked():
            set_setting(key='map_mode', value='planar')
        else:
            set_setting(key='map_mode', value='fixed_extent')
        # Save state
        set_setting(key='frames_per_feature', value=self.frames_per_feature)
        set_setting(key='dwell_frames', value=self.dwell_frames)
        set_setting(key='frames_for_extent', value=self.frames_for_extent)
        set_setting(key='max_scale', value=int(self.max_scale))
        set_setting(key='min_scale', value=int(self.min_scale))
        set_setting(
            key='enable_pan_easing',
            value=self.pan_easing_widget.is_enabled())
        set_setting(
            key='enable_zoom_easing',
            value=self.zoom_easing_widget.is_enabled())
        set_setting(
            key='pan_easing',
            value=self.pan_easing_widget.easing_name())
        set_setting(
            key='zoom_easing',
            value=self.zoom_easing_widget.easing_name())
        set_setting(key='reuse_cache', value=self.reuse_cache.isChecked())
        set_setting(key='output_file', value=self.output_file)

    # Prevent the slot being called twize
    @pyqtSlot()
    def accept(self):
        """Process the animation sequence.

        .. note:: This is called on OK click.
        """
        # Image preview page
        self.preview_stack.setCurrentIndex(0)
        # Enable queue status page
        self.status_stack.setCurrentIndex(1)
        # set parameter from dialog

        if not self.reuse_cache.isChecked():
            os.system('rm %s/%s*' %
                      (
                          self.work_directory,
                          self.frame_filename_prefix
                      ))
        # feature layer that we will visit each feature for
        feature_layer = self.layer_combo.currentLayer()
        if feature_layer:
            self.transform = QgsCoordinateTransform(
                feature_layer.crs(),
                QgsProject.instance().crs(),
                QgsProject.instance())
            feature_count = feature_layer.featureCount()

        layer_type = qgis.core.QgsWkbTypes.displayString(
            int(self.layer_combo.currentLayer().wkbType()))
        layer_name = self.layer_combo.currentLayer().name()
        self.output_log_text_edit.append(
            'Generating flight path for %s layer: %s' %
            (layer_type, layer_name))
        self.max_scale = self.scale_range.maximumScale()
        self.min_scale = self.scale_range.minimumScale()
        self.dwell_frames = self.hover_frames_spin.value()
        self.frames_per_feature = self.feature_frames_spin.value()
        self.frames_to_zenith = int(self.frames_per_feature / 2)
        self.frames_for_extent = self.extent_frames_spin.value()
        self.render_queue.frames_per_feature = (
            self.frames_per_feature + self.dwell_frames)
        self.image_counter = 1

        self.frames_per_second = self.framerate_spin.value()

        if self.radio_sphere.isChecked():
            self.map_mode = MapMode.SPHERE
        elif self.radio_planar.isChecked():
            self.map_mode = MapMode.PLANAR
        else:
            self.map_mode = MapMode.FIXED_EXTENT

        self.save_state()

        self.render_queue.reset()
        if self.map_mode == MapMode.FIXED_EXTENT:
            self.output_log_text_edit.append(
                'Generating %d frames for fixed extent render'
                % self.frames_for_extent)
            self.progress_bar.setMaximum(self.frames_for_extent)
            self.total_frame_count = self.frames_for_extent
            self.progress_bar.setValue(0)
            self.iface.mapCanvas().setReferencedExtent(QgsReferencedRectangle(
                self.extent_group_box.currentExtent(), self.extent_group_box.currentCrs()))

            self.image_counter = 0

            for image_count in range(0, self.frames_for_extent):
                name = ('%s/%s-%s.png' % (
                    self.work_directory,
                    self.frame_filename_prefix,
                    str(self.image_counter).rjust(10, '0')
                ))
                self.output_log_text_edit.append(name)
                self.render_queue.queue_task(
                    name,
                    None,
                    self.image_counter,
                    'Fixed Extent')
                self.progress_bar.setValue(self.image_counter)
                self.image_counter += 1
        else:
            if not feature_layer:
                self.output_log_text_edit.append(
                    'Processing halted, no animation layer set.')
                return
            # Subtract one because we already start at the first feature
            self.total_frame_count = (
                (feature_count - 1) *
                (self.dwell_frames + self.frames_per_feature))
            self.output_log_text_edit.append(
                'Generating %d frames' % self.total_frame_count)
            self.progress_bar.setMaximum(
                self.total_frame_count)
            self.progress_bar.setValue(0)
            self.previous_feature = None
            for feature in feature_layer.getFeatures():
                # None, Panning, Hovering
                if self.previous_feature is None:
                    self.previous_feature = feature
                    self.dwell_at_feature(feature)
                else:
                    self.fly_feature_to_feature(self.previous_feature, feature)
                    self.dwell_at_feature(feature)
                    self.previous_feature = feature
        # Now all the tasks are prepared, start the render_queue processing
        self.render_queue.process_more_tasks()

    def processing_completed(self):
        """Run after all processing is done to generate gif or mp4.

        .. note:: This called by process_more_tasks when all tasks are complete.
        """
        if self.radio_gif.isChecked():
            self.output_log_text_edit.append('Generating GIF')
            convert = which('convert')[0]
            self.output_log_text_edit.append('convert found: %s' % convert)
            # Now generate the GIF. If this fails try run the call from
            # the command line and check the path to convert (provided by
            # ImageMagick) is correct...
            # delay of 3.33 makes the output around 30fps
            os.system('%s -delay 3.33 -loop 0 %s/$s-*.png %s' % (
                self.work_directory,
                self.frame_filename_prefix,
                convert, self.work_directory, self.output_file))
            # Now do a second pass with image magick to resize and compress the
            # gif as much as possible.  The remap option basically takes the
            # first image as a reference image for the colour palette Depending
            # on you cartography you may also want to bump up the colors param
            # to increase palette size and of course adjust the scale factor to
            # the ultimate image size you want
            os.system("""
                %s %s -coalesce -scale 600x600 -fuzz 2% +dither \
                    -remap %s/%s.gif[20] +dither -colors 14 -layers \
                    Optimize %s/animation_small.gif""" % (
                convert,
                self.output_file,
                self.work_directory,
                self.frame_filename_prefix,
                self.work_directory
            ))
            # Video preview page
            self.preview_stack.setCurrentIndex(1)
            self.media_player.setMedia(
                QMediaContent(QUrl.fromLocalFile('/tmp/animation_small-gif')))
            self.play_button.setEnabled(True)
            self.play()
            self.output_log_text_edit.append(
                'GIF written to %s' % self.output_file)
        else:
            self.output_log_text_edit.append('Generating MP4 Movie')
            ffmpeg = which('ffmpeg')[0]
            # Also we will make a video of the scene - useful for cases where
            # you have a larger colour pallette and gif will not hack it.
            # The Pad option is to deal with cases where ffmpeg complains
            # because the h or w of the image is an odd number of pixels.
            # :color=white pads the video with white pixels.
            # Change to black if needed.
            # -y to force overwrite exising file
            self.output_log_text_edit.append('ffmpeg found: %s' % ffmpeg)

            framerate = str(self.framerate_spin.value())

            command = ("""
                %s -y -framerate %s -pattern_type glob \
                -i "%s/%s-*.png" -vf \
                "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white" \
                -c:v libx264 -pix_fmt yuv420p %s""" % (
                ffmpeg,
                framerate,
                self.work_directory,
                self.frame_filename_prefix,
                self.output_file))
            self.output_log_text_edit.append('Generating Movie:\n%s' % command)
            os.system(command)
            # Video preview page
            self.preview_stack.setCurrentIndex(1)
            self.media_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.output_file)))
            self.play_button.setEnabled(True)
            self.play()
            self.output_log_text_edit.append(
                'MP4 written to %s' % self.output_file)

    def fly_feature_to_feature(self, start_feature, end_feature):
        self.image_counter += 1
        verbose_mode = int(setting(key='verbose_mode', default=0))
        self.progress_bar.setValue(self.image_counter)
        # In case we are iterating over lines or polygons, we
        # need to conver them to points first.
        start_point = self.geometry_to_pointxy(start_feature)
        end_point = self.geometry_to_pointxy(end_feature)
        if not start_point or not end_point:
            self.output_log_text_edit.append(
                'Unsupported geometry, skipping.')
            return

        # now go on to calculate the mins, max's and ranges
        x_min = start_point.x()
        x_max = end_point.x()
        x_range = abs(x_max - x_min)
        x_increment = x_range / self.frames_per_feature
        y_min = start_point.y()
        y_max = end_point.y()
        y_range = abs(y_max - y_min)
        y_increment = y_range / self.frames_per_feature
        # at the midfeature of the traveral between the two features
        # we switch the easing around so the movememnt first
        # goes away from the direct line, then towards it.
        y_midfeature = (y_increment * self.frames_per_feature) / 2
        x_midfeature = (x_increment * self.frames_per_feature) / 2
        scale = None

        for current_frame in range(0, self.frames_per_feature, 1):

            # For x we could have a pan easing
            x_offset = x_increment * current_frame
            if self.pan_easing_widget.is_enabled():
                if x_offset < x_midfeature:
                    # Flying away from centerline
                    # should be 0 at origin, 1 at centerfeature
                    pan_easing_factor = 1 - self.pan_easing.valueForProgress(
                        x_offset/x_midfeature)
                else:
                    # Flying towards centerline
                    # should be 1 at centerfeature, 0 at destination
                    try:
                        pan_easing_factor = self.pan_easing.valueForProgress(
                            (x_offset - x_midfeature) / x_midfeature)
                    except:
                        pan_easing_factor = 0
                x_offset = x_offset * pan_easing_factor
            # Deal with case where we need to fly west instead of east
            if x_min < x_max:
                x = x_min + x_offset
            else:
                x = x_min - x_offset

            # for Y we could have easing
            y_offset = y_increment * current_frame

            if self.pan_easing_widget.is_enabled():
                if y_offset < y_midfeature:
                    # Flying away from centerline
                    # should be 0 at origin, 1 at centerfeature
                    pan_easing_factor = 1 - self.pan_easing.valueForProgress(
                        y_offset / y_midfeature)
                else:
                    # Flying towards centerline
                    # should be 1 at centerfeature, 0 at destination
                    pan_easing_factor = self.pan_easing.valueForProgress(
                        y_offset - y_midfeature / y_midfeature)

                y_offset = y_offset * pan_easing_factor

            # Deal with case where we need to fly north instead of south
            if y_min < y_max:
                y = y_min + y_offset
            else:
                y = y_min - y_offset

            # zoom in and out to each feature if we are doing zoom easing
            if self.zoom_easing_widget.is_enabled():
                # Now use easings for zoom level too
                # first figure out if we are flying up or down
                if current_frame < self.frames_to_zenith:
                    # Flying up
                    zoom_easing_factor = 1 - self.zoom_easing.valueForProgress(
                        current_frame/self.frames_to_zenith)
                    scale = ((self.max_scale - self.min_scale) *
                             zoom_easing_factor) + self.min_scale
                else:
                    # flying down
                    zoom_easing_factor = self.zoom_easing.valueForProgress(
                        (current_frame - self.frames_to_zenith) /
                        self.frames_to_zenith)
                    scale = ((self.max_scale - self.min_scale) *
                             zoom_easing_factor) + self.min_scale

            if self.map_mode == MapMode.PLANAR:
                center = QgsPointXY(x, y)
                center = self.transform.transform(center)
                self.iface.mapCanvas().setCenter(center)
            if scale is not None:
                self.iface.mapCanvas().zoomScale(scale)

            # Change CRS if needed
            if self.map_mode == MapMode.SPHERE:
                definition = (""" +proj=ortho \
                    +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 \
                    +ellps=sphere +units=m +no_defs""" % (x, y))
                crs = QgsCoordinateReferenceSystem()
                crs.createFromProj(definition)
                self.iface.mapCanvas().setDestinationCrs(crs)
                if not self.enable_zoom_easing.isChecked():
                    self.iface.mapCanvas().zoomToFullExtent()

            # Pad the numbers in the name so that they form a 10 digit
            # string with left padding of 0s

            name = ('%s/%s-%s.png' % (
                self.work_directory,
                self.frame_filename_prefix,
                str(self.image_counter).rjust(10, '0')))

            if verbose_mode:
                self.output_log_text_edit.append(
                    'Fly : %s' % name)

            starttime = timeit.default_timer()
            if os.path.exists(name) and self.reuse_cache.isChecked():
                # User opted to re-used cached images so do nothing for now
                pass
            else:
                # Not crashy but no decorations and annotations....
                # render_image(name)
                # crashy - check with Nyall why...
                self.render_queue.queue_task(
                    name, end_feature.id(), current_frame, 'Panning')
            self.image_counter += 1
            self.progress_bar.setValue(self.image_counter)

    def load_image(self, name):
        # Load the preview with the named image file
        with open(name, 'rb') as image_file:
            content = image_file.read()
            image = QImage()
            image.loadFromData(content)
            pixmap = QPixmap.fromImage(image)
            self.current_frame_preview.setPixmap(pixmap)

    def dwell_at_feature(self, feature):
        """Wait at a feature to emphasise it in the video.

        :param feature: QgsFeature to dwell at.
        :type feature: QgsFeature
        """
        center = self.geometry_to_pointxy(feature)
        if not center:
            self.output_log_text_edit.append(
                'Unsupported geometry, skipping.')
            return
        center = self.transform.transform(center)
        self.iface.mapCanvas().setCenter(center)
        self.iface.mapCanvas().zoomScale(self.max_scale)
        verbose_mode = int(setting(key='verbose_mode', default=0))

        for current_frame in range(0, self.dwell_frames, 1):
            # Pad the numbers in the name so that they form a
            # 10 digit string with left padding of 0s
            name = ('%s/%s-%s.png' % (
                self.work_directory,
                self.frame_filename_prefix,
                str(self.image_counter).rjust(10, '0')))

            if verbose_mode:
                self.output_log_text_edit.append(
                    'Dwell : %s' % name)

            if os.path.exists(name) and self.reuse_cache.isChecked():
                # User opted to re-used cached images to do nothing for now
                self.load_image(name)
            else:
                # Not crashy but no decorations and annotations....
                # render_image_to_file(name)
                # crashy - check with Nyall why...
                self.render_queue.queue_task(
                    name, feature.id(), current_frame, 'Hovering')

            self.image_counter += 1
            self.progress_bar.setValue(self.image_counter)

    def geometry_to_pointxy(self, feature):
        verbose_mode = int(setting(key='verbose_mode', default=0))
        x, y = None, None
        # Be careful of replacing this with logic like this
        # feature.geometry().wkbType() == QgsWkbTypes.PointGeometry:
        # subce it resolves to the wrong type
        geometry_type = qgis.core.QgsWkbTypes.displayString(
            int(feature.geometry().wkbType()))
        # List of type names is here:
        # https://api.qgis.org/api/qgswkbtypes_8cpp_source.html
        if geometry_type in ['Point', 'PointZ', 'PointM', 'PointZM', 'Point25D']:
            x = feature.geometry().asPoint().x()
            y = feature.geometry().asPoint().y()
            center = QgsPointXY(x, y)
        elif geometry_type in [
                'LineString', 'LineStringZ', 'LineStringM',
                'LineStringZM', 'LineString25D']:
            length = feature.geometry().length()
            point = feature.geometry().interpolate(length/2.0)
            x = point.geometry().x()
            y = point.geometry().y()
            center = QgsPointXY(x, y)
        elif geometry_type in [
                'Polygon', 'PolygonZ', 'PolygonM', 'PolygonZM', 'Polygon25D']:
            center = feature.geometry().centroid().asPoint()
        else:
            if verbose_mode:
                self.output_log_text_edit.append(
                    'Feature Geometry Type : %s' % geometry_type)
            center = None
        return center

    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.
        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user."""
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = workbench_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)

    # Video Playback Methods
    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.video_slider.setValue(position)

    def duration_changed(self, duration):
        self.video_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_video_error(self):
        self.play_button.setEnabled(False)
        self.output_log_text_edit.append(
            self.media_player.errorString())
