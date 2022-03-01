# coding=utf-8
"""This module contains the main GUI interaction logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

# This will make the QGIS use a world projection and then move the center
# of the CRS sequentially to create a spinning globe effect
from doctest import debug_script
import os
import timeit
import time

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA

from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtCore import QEasingCurve, QPropertyAnimation, QPoint
from qgis.core import (
    QgsPointXY,
    QgsExpressionContextUtils,
    QgsProject,
    QgsExpressionContextScope,
    QgsMapRendererTask,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsMapRendererCustomPainterJob,
    QgsMapLayerProxyModel)
from qgis.PyQt.QtWidgets import QMessageBox, QPushButton
from qgis.core import Qgis
from enum import Enum
from .settings import set_setting, setting
from .utilities import get_ui_class, which, resources_path 

class MapMode(Enum):
    SPHERE = 1 # CRS will be manipulated to create a spinning globe effect
    PLANE = 2 # CRS will not be altered, but will pan and zoom to each point
    STATIC = 3 # Map will not pan / zoom

FORM_CLASS = get_ui_class('animation_workbench_base.ui')


class AnimationWorkbench(QtWidgets.QDialog, FORM_CLASS):
    """Dialog implementation class Animation Workbench class."""

    def __init__(self, parent=None, iface=None, dock_widget=None):
        """Constructor for the multi buffer dialog.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget
        """
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)        
        # Work around for not being able to set the layer
        # types allowed in the QgsMapLayerSelector combo
        # See https://github.com/qgis/QGIS/issues/38472#issuecomment-715178025
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PointLayer)

        self.setWindowTitle(self.tr('Animation Workbench'))
        icon = resources_path(
            'img', 'icons', 'animation-workshop.svg')
        self.setWindowIcon(QtGui.QIcon(icon))
        self.parent = parent
        self.iface = iface
        # Set up things for context help
        self.help_button = self.button_box.button(
            QtWidgets.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)


        # Fix for issue 1699 - cancel button does nothing
        cancel_button = self.button_box.button(
            QtWidgets.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)
        # Fix ends
        ok_button = self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)

        # How many frames to render for each point pair transition
        # The output is generated at 30fps so choosing 30
        # would fly to each point for 1s
        # You can then use the 'current_point' project variable
        # to determine the current point id
        # and the 'point_frame' project variable to determine
        # the frame number for the current point based on frames_for_interval
        
        self.frames_per_point = int(setting(key='frames_per_point', default=90))
        self.point_frames_spin.setValue(self.frames_per_point)

        # How many frames to dwell at each point for (output at 30fps)
        self.dwell_frames = int(setting(key='dwell_frames', default=30))
        self.hover_frames_spin.setValue(self.dwell_frames)
        # Keep the scales the same if you dont want it to zoom in an out
        self.max_scale = int(setting(key='max_scale', default='250000000'))
        self.scale_range.setMaximumScale(self.max_scale)
        self.min_scale = int(setting(key='min_scale', default='10000000'))
        self.scale_range.setMinimumScale(self.min_scale)
        self.image_counter = None 
        # enable this if you want wobbling panning
        if setting(key='pan_easing_enabled', default=False) == 'false':
            self.pan_easing_enabled = False
        else:
            self.pan_easing_enabled = True
            
        self.previous_point = None

        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'frames_per_point', 0)
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_frame', 0)
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_point_id', 0)
        # None, Panning, Hovering
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_animation_action', 'None')

        self.map_mode = setting(key='map_mode', default=MapMode.SPHERE)
        if self.map_mode == MapMode.SPHERE:
            self.radio_sphere.setChecked(True)
        elif self.map_mode == MapMode.PLANE:
            self.radio_planar.setChecked(True)
        else:
            self.radio_static.setChecked(True)
        
        # Setup easing combos and previews etc
        self.load_combo_with_easings(self.pan_easing_combo)
        self.load_combo_with_easings(self.zoom_easing_combo)
        self.setup_easing_previews()

        self.pan_easing = None
        pan_easing_index = int(setting(key='pan_easing', default='0'))
        
        self.zoom_easing = None
        zoom_easing_index = int(setting(key='zoom_easing', default='0'))

        # Keep this after above animations are set up 
        # since the slot requires the above setup to be completed
        self.pan_easing_combo.currentIndexChanged.connect(
            self.pan_easing_changed)
        self.zoom_easing_combo.currentIndexChanged.connect(
            self.zoom_easing_changed)

        self.pan_easing_combo.setCurrentIndex(pan_easing_index)
        self.zoom_easing_combo.setCurrentIndex(zoom_easing_index)

        # Set an initial image in the preview based on the current map
        image = self.render_image()
        pixmap = QtGui.QPixmap.fromImage(image)
        self.current_frame_preview.setPixmap(pixmap)
        self.current_frame_preview.setScaledContents(True)
        # The maximum number of concurrent threads to allow
        # during rendering. Probably setting to the same number 
        # of CPU cores you have would be a good conservative approach
        # You could probably run 100 or more on a decently specced machine
        self.render_thread_pool_size = int(setting(
            key='render_thread_pool_size', default=100))
        # Number of currently running render threads
        self.current_render_thread_count = 0
        self.progress_bar.setValue(0)
        # This will be half the number of frames per point
        # so that the first half of the journey is flying up
        # away from the last point and the next half of the
        # journey is flying down towards the next point.
        self.frames_to_zenith = None

        self.reuse_cache.setChecked(
            bool(setting(key='reuse_cache', default=False)))

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
        :param button_text: The text of the button if 'more_details' is not empty.
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

    def pan_easing_changed(self, index):
        """Handle changes to the pan easing type combo.
        
        .. note:: This is called on changes to the pan easing combo.

        .. versionadded:: 1.0

        :param index: Index of the now selected combo item.
        :type flag: int

        """
        easing_type = QEasingCurve.Type(index)
        self.pan_easing_preview_animation.setEasingCurve(easing_type)
        self.pan_easing = QEasingCurve(easing_type)

    def zoom_easing_changed(self, index):
        """Handle changes to the zoom easing type combo.
        
        .. note:: This is called on changes to the zoom easing combo.

        .. versionadded:: 1.0

        :param index: Index of the now selected combo item.
        :type flag: int

        """
        easing = QEasingCurve.Type(index)
        self.zoom_easing_preview_animation.setEasingCurve(easing)
        self.zoom_easing = QEasingCurve(easing)

    def accept(self):
        """Process the animation sequence.

        .. note:: This is called on OK click.
        """
        # Save state
        set_setting(key='frames_per_point',value=self.frames_per_point)
        set_setting(key='dwell_frames',value=self.dwell_frames)
        set_setting(key='max_scale',value=int(self.max_scale))
        set_setting(key='min_scale',value=int(self.min_scale))
        set_setting(key='pan_easing_enabled',value=self.pan_easing_enabled)
        set_setting(key='map_mode',value=self.map_mode)
        set_setting(key='pan_easing',value=self.pan_easing_combo.currentIndex())
        set_setting(key='zoom_easing',value=self.zoom_easing_combo.currentIndex())
        set_setting(
            key='render_thread_pool_size',value=self.render_thread_pool_size)
        set_setting(key='reuse_cache',value=self.reuse_cache.isChecked())

        # set parameter from dialog

        if not self.reuse_cache.isChecked():
            os.system('rm /tmp/globe*')

        # Point layer that we will visit each point for
        point_layer = self.layer_combo.currentLayer()
        self.max_scale = self.scale_range.maximumScale()
        self.min_scale = self.scale_range.minimumScale()
        self.dwell_frames = self.hover_frames_spin.value()
        self.frames_per_point = self.point_frames_spin.value()
        self.frames_to_zenith = int(self.frames_per_point / 2)
        self.image_counter = 1
        self.progress_bar.setMaximum(
            point_layer.featureCount() * (
                self.dwell_frames + self.frames_per_point)
        )
        self.progress_bar.setValue(0)
        self.previous_point = None

        if self.radio_sphere.isChecked():
            self.map_mode = MapMode.SPHERE
        elif self.radio_planar.isChecked():
            self.map_mode = MapMode.PLANE
        else:
            self.map_mode = MapMode.STATIC
        
        for feature in point_layer.getFeatures():
            # None, Panning, Hovering
            QgsExpressionContextUtils.setProjectVariable(
                QgsProject.instance(), 'current_animation_action', 'None')
            if self.previous_point is None:
                self.previous_point = feature
                continue
            else: #elif image_counter < 2:
                self.fly_point_to_point(self.previous_point, feature)
                self.dwell_at_point(feature)
                self.previous_point = feature        

        if self.radio_gif.isChecked():
            convert = which('convert')
            # Now generate the GIF. If this fails try run the call from the command line
            # and check the path to convert (provided by ImageMagick) is correct...
            # delay of 3.33 makes the output around 30fps               
            os.system('%s -delay 3.33 -loop 0 /tmp/globe-*.png /tmp/globe.gif' % convert)
            # Now do a second pass with image magick to resize and compress the
            # gif as much as possible.  The remap option basically takes the
            # first image as a reference inmage for the colour palette Depending
            # on you cartography you may also want to bump up the colors param
            # to increase palette size and of course adjust the scale factor to
            # the ultimate image size you want               
            os.system('%s /tmp/globe.gif -coalesce -scale 600x600 -fuzz 2% +dither -remap /tmp/globe.gif[20] +dither -colors 14 -layers Optimize /tmp/globe_small.gif' % convert)
        else:
            ffmpeg = which('ffmpeg')
            # Also we will make a video of the scene - useful for cases where
            # you have a larger colour pallette and gif will not hack it. The Pad
            # option is to deal with cases where ffmpeg complains because the h
            # or w of the image is an odd number of pixels.  :color=white pads
            # the video with white pixels. Change to black if needed.
            # -y to force overwrite exising file
            os.system('%s -y -framerate 30 -pattern_type glob -i "/tmp/globe-*.png" -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white" -c:v libx264 -pix_fmt yuv420p /tmp/globe.mp4' % ffmpeg)

    def render_image(self):
        """Render the current canvas to an image.
        
        .. note:: This is renders synchronously.

        .. versionadded:: 1.0

        :returns QImage: 
        """
        size = self.iface.mapCanvas().size()
        image = QImage(size, QImage.Format_RGB32)

        painter = QPainter(image)
        settings = self.iface.mapCanvas().mapSettings()
        self.iface.mapCanvas().refresh()
        # You can fine tune the settings here for different
        # dpi, extent, antialiasing...
        # Just make sure the size of the target image matches

        job = QgsMapRendererCustomPainterJob(settings, painter)
        job.renderSynchronously()
        painter.end()
        self.display_information_message_bar(
                title="Image rendered",
                message="Image rendered",
                more_details=None,
                button_text='Show details ...',
                duration=8)
        return image


    def render_image_to_file(self, name):
        size = self.iface.mapCanvas().size()
        image = QImage(size, QImage.Format_RGB32)

        painter = QPainter(image)
        settings = self.iface.mapCanvas().mapSettings()
        self.iface.mapCanvas().refresh()
        # You can fine tune the settings here for different
        # dpi, extent, antialiasing...
        # Just make sure the size of the target image matches

        job = QgsMapRendererCustomPainterJob(settings, painter)
        job.renderSynchronously()
        painter.end()
        image.save(name)

    def free_render_lock(self):
        print('Freeing render lock.')
        self.current_render_thread_count -= 1
        print(' Now %d threads used ' % self.current_render_thread_count)

    def render_image_as_task(self,name,current_point_id,current_frame):
        # Block until there is space in the render thread pool
        while self.current_render_thread_count > self.render_thread_pool_size:
            time.sleep(1.0)
            print('Waiting for render lock.')
            self.current_render_thread_count -= 1
            print(' Now %d threads used ' % self.current_render_thread_count)
        # Ready to start rendering, claim a space in the pool
        self.current_render_thread_count += 1
        #size = self.iface.mapCanvas().size()
        settings = self.iface.mapCanvas().mapSettings()
        # The next part sets project variables that you can use in your 
        # cartography etc. to see the progress. Here is an example
        # of a QGS expression you can use in the map decoration copyright
        # widget to show current script progress
        # [%'Frame ' || to_string(coalesce(@current_frame, 0)) || '/' || 
        # to_string(coalesce(@frames_per_point, 0)) || ' for point ' || 
        # to_string(coalesce(@current_point_id,0))%]
        task_scope = QgsExpressionContextScope()
        task_scope.setVariable('current_point_id', current_point_id)
        task_scope.setVariable('frames_per_point', self.frames_per_point)
        task_scope.setVariable('current_frame', current_frame)
        context = settings.expressionContext()
        context.appendScope(task_scope) 
        settings.setExpressionContext(context)
        # Set the output file name for the render task
        mapRendererTask = QgsMapRendererTask( settings, name, "PNG" )
        # We need to clone the annotations because otherwise SIP will 
        # pass ownership and then cause a crash when the render task is destroyed
        annotations = QgsProject.instance().annotationManager().annotations()
        annotations_list = [a.clone() for a in annotations]
        if (len(annotations_list) > 0):
            mapRendererTask.addAnnotations([a.clone() for a in annotations])
        # Add decorations to the render job
        decorations = self.iface.activeDecorations()
        mapRendererTask.addDecorations(decorations)
        # Allo other tasks waiting in the queue to go on and render
        mapRendererTask.renderingComplete.connect(self.free_render_lock)
        # Does not work
        #QObject.connect(mapRendererTask,SIGNAL("renderingComplete()"),free_render_lock)
        # Start the rendering task on the queue
        QgsApplication.taskManager().addTask(mapRendererTask)

    def fly_point_to_point(self, start_point, end_point):
       
        self.image_counter += 1
        self.progress_bar.setValue(self.image_counter)
        x_min = start_point.geometry().asPoint().x()
        print("XMIN : %f" % x_min)
        x_max = end_point.geometry().asPoint().x()
        print("XMAX : %f" % x_max)
        x_range = abs(x_max - x_min)
        print("XRANGE : %f" % x_range)
        x_increment = x_range / self.frames_per_point
        y_min = start_point.geometry().asPoint().y()
        print("YMIN : %f" % y_min)
        y_max = end_point.geometry().asPoint().y()
        print("YMAX : %f" % y_max)
        y_range = abs(y_max - y_min)
        print("YRANGE : %f" % y_range)
        y_increment = y_range / self.frames_per_point

        # None, Panning, Hovering
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_animation_action', 'Panning')

        for current_frame in range(0, self.frames_per_point, 1):
            x_offset = x_increment * current_frame
            x = x_min + x_offset 
            y_offset = y_increment * current_frame
            if self.pan_easing_enabled:
                y_easing_factor = y_offset / self.frames_per_point 
                y = y_min + (y_offset * self.pan_easing.valueForProgress(y_easing_factor))
            else:
                y = y_min + y_offset
            if self.map_mode == MapMode.SPHERE:
                definition = ( 
                '+proj=ortho +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=sphere +units=m +no_defs' % (x, y))
                crs = QgsCoordinateReferenceSystem()
                crs.createFromProj(definition)
                self.iface.mapCanvas().setDestinationCrs(crs)
            # For plane map mode we just use whatever CRS is active
            if self.map_mode is not MapMode.STATIC:
                # Now use easings for zoom level too
                # first figure out if we are flying up or down
                if current_frame < self.frames_to_zenith:
                    # Flying up
                    zoom_easing_factor = self.zoom_easing.valueForProgress(
                        current_frame/self.frames_to_zenith)
                    scale = ((self.max_scale - self.min_scale) * 
                              zoom_easing_factor) + self.min_scale
                else:
                    # flying down
                    zoom_easing_factor = 1 - self.zoom_easing.valueForProgress(
                        (current_frame - self.frames_to_zenith)/self.frames_to_zenith)
                    scale = ((self.max_scale - self.min_scale) * 
                        zoom_easing_factor) + self.min_scale

                if self.map_mode != MapMode.SPHERE:
                    self.iface.mapCanvas().setCenter(
                        QgsPointXY(x,y))
                self.iface.mapCanvas().zoomScale(scale)
            
            # Pad the numbers in the name so that they form a 10 digit string with left padding of 0s
            name = ('/tmp/globe-%s.png' % str(self.image_counter).rjust(10, '0'))
            starttime = timeit.default_timer()
            if os.path.exists(name) and self.reuse_cache.isChecked():
                # User opted to re-used cached images to do nothing for now
                self.image_counter += 1
            else:
                # Not crashy but no decorations and annotations....
                #render_image(name)
                # crashy - check with Nyall why...
                self.render_image_as_task(
                    name, end_point.id(), current_frame)
                self.image_counter += 1

    def load_image(self, name):
        #Load the preview with the named image file 
        with open(name, 'rb') as image_file:
            content = image_file.read()
            image = QtGui.QImage()
            image.loadFromData(content)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.current_frame_preview.setPixmap(pixmap)
            self.current_frame_preview.setScaledContents(True)

    def dwell_at_point(self, feature):
        #f.write('Render Time,Longitude,Latitude,Latitude Easing Factor,Zoom Easing Factor,Zoom Scale\n')
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        point = QgsPointXY(x,y)
        self.iface.mapCanvas().setCenter(point)
        self.iface.mapCanvas().zoomScale(self.min_scale)
        # None, Panning, Hovering
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_animation_action', 'Hovering')
        for current_frame in range(0, self.dwell_frames, 1):
            # Pad the numbers in the name so that they form a 10 digit string with left padding of 0s
            name = ('/tmp/globe-%s.png' % str(self.image_counter).rjust(10, '0'))
            if os.path.exists(name) and self.reuse_cache.isChecked():
                # User opted to re-used cached images to do nothing for now
                self.load_image(name)
            else:
                # Not crashy but no decorations and annotations....
                #render_image_to_file(name)
                # crashy - check with Nyall why...
                self.render_image_as_task(name, feature.id(), current_frame)
            
            self.image_counter += 1
            self.progress_bar.setValue(self.image_counter)

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

        message = multi_buffer_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
    
    def load_combo_with_easings(self, combo):
        # Perhaps we can softcode these items using the logic here
        # https://github.com/baoboa/pyqt5/blob/master/examples/animation/easing/easing.py#L159
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
        combo.addItem("Custom",QEasingCurve.Custom)
    
    def setup_easing_previews(self):
        # Set up easing previews
        self.pan_easing_preview_icon = QtWidgets.QWidget(self.pan_easing_preview)
        self.pan_easing_preview_icon.setStyleSheet("background-color:yellow;border-radius:5px;")
        self.pan_easing_preview_icon.resize(10, 10)
        self.pan_easing_preview_animation = QPropertyAnimation(self.pan_easing_preview_icon, b"pos")
        self.pan_easing_preview_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.pan_easing_preview_animation.setStartValue(QPoint(0, 0))
        self.pan_easing_preview_animation.setEndValue(QPoint(250, 150))
        self.pan_easing_preview_animation.setDuration(1500)
        # loop forever ...
        self.pan_easing_preview_animation.setLoopCount(-1)
        self.pan_easing_preview_animation.start()

        self.zoom_easing_preview_icon = QtWidgets.QWidget(self.zoom_easing_preview)
        self.zoom_easing_preview_icon.setStyleSheet("background-color:green;border-radius:5px;")
        self.zoom_easing_preview_icon.resize(10, 10)
        self.zoom_easing_preview_animation = QPropertyAnimation(self.zoom_easing_preview_icon, b"pos")
        self.zoom_easing_preview_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.zoom_easing_preview_animation.setStartValue(QPoint(0, 0))
        self.zoom_easing_preview_animation.setEndValue(QPoint(250, 150))
        self.zoom_easing_preview_animation.setDuration(1500)
        # loop forever ...
        self.zoom_easing_preview_animation.setLoopCount(-1)
        self.zoom_easing_preview_animation.start()