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
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QEasingCurve
from qgis.PyQt import QtCore
from qgis.core import QgsPointXY,QgsExpressionContextUtils,QgsProject,QgsExpressionContextScope,QgsMapRendererTask,QgsApplication,QgsCoordinateReferenceSystem
from enum import Enum


def resources_path(*args):
    """Get the path to our resources folder.

    .. versionadded:: 1.0

    Note that in version 1.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param args List of path elements e.g. ['img', 'logos', 'image.png']
    :type args: str

    :return: Absolute path to the resources folder.
    :rtype: str
    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(
        os.path.join(path, os.path.pardir, 'resources'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path


def resource_url(path):
    """Get the a local filesystem url to a given resource.

    .. versionadded:: 1.0

    Note that we dont use Qt Resource files in
    favour of directly accessing on-disk resources.

    :param path: Path to resource e.g. /home/timlinux/foo/bar.png
    :type path: str

    :return: A valid file url e.g. file:///home/timlinux/foo/bar.png
    :rtype: str
    """
    url = QtCore.QUrl.fromLocalFile(path)
    return str(url.toString())


def get_ui_class(ui_file):
    """Get UI Python class from .ui file.

       Can be filename.ui or subdirectory/filename.ui

    :param ui_file: The file of the ui in safe.gui.ui
    :type ui_file: str
    """
    os.path.sep.join(ui_file.split('/'))
    ui_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            # os.pardir,
            'ui',
            ui_file
        )
    )
    return uic.loadUiType(ui_file_path)[0]

class MapMode(Enum):
    SPHERE = 1 # CRS will be manipulated to create a spinning globe effect
    PLANE = 2 # CRS will not be altered, but will pan and zoom to each point
    STATIC = 3 # Map will not pan / zoom
class EasingMode(Enum):
    EASE_IN = 1 # traveling away from an object
    EASE_OUT = 2 # travelling towards an object


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
        self.setWindowTitle(self.tr('Animation Workbench'))
        icon = resources_path('img', 'icons', 'animation-w.svg')
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

        debug_mode = False
        if debug_mode:
            try:
                self.initialize_debugger()
            except:
                pass

        # How many frames to render for each point pair transition
        # The output is generated at 30fps so choosing 30
        # would fly to each point for 1s
        # You can then use the 'current_point' project variable
        # to determine the current point id
        # and the 'point_frame' project variable to determine
        # the frame number for the current point based on frames_for_interval
        self.frames_per_point = 90

        # How many frames to dwell at each point for (output at 30fps)
        self.dwell_frames = 30

        # Keep the scales the same if you dont want it to zoom in an out
        self.max_scale = 75589836
        self.min_scale = 1000000
        self.image_counter = 1 
        # enable this if you want wobbling panning
        self.pan_easing_enabled = False
        self.previous_point = None

        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'frames_per_point', 0)
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_frame', 0)
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'current_point_id', 0)

        self.map_mode = MapMode.SPHERE
        self.easing_mode = EasingMode.EASE_OUT

        # The maximum number of concurrent threads to allow
        # during rendering. Probably setting to the same number 
        # of CPU cores you have would be a good conservative approach
        # You could probably run 100 or more on a decently specced machine
        self.render_thread_pool_size = 100
        # Number of currently running render threads
        self.current_render_thread_count = 0

    def accept(self):
        """Process the layer for multi buffering and generate a new layer.

        .. note:: This is called on OK click.
        """
        # set parameter from dialog

        os.system('rm /tmp/globe*')
        # Point layer that we will visit each point for
        point_layer = self.iface.activeLayer()
        for feature in point_layer.getFeatures():
            if self.previous_point is None:
                self.previous_point = feature
                continue
            else: #elif image_counter < 2:
                self.fly_point_to_point(previous_point, feature)
                self.dwell_at_point(feature)
                self.previous_point = feature        

        # Now generate the GIF. If this fails try run the call from the command line
        # and check the path to convert (provided by ImageMagick) is correct...
        # delay of 3.33 makes the output around 30fps               
        os.system('/usr/bin/convert -delay 3.33 -loop 0 /tmp/globe-*.png /tmp/globe.gif')
        # Now do a second pass with image magick to resize and compress the gif as much as possible.
        # The remap option basically takes the first image as a reference inmage for the colour palette
        # Depending on you cartography you may also want to bump up the colors param to increase palette size
        # and of course adjust the scale factor to the ultimate image size you want               
        os.system('/usr/bin/convert /tmp/globe.gif -coalesce -scale 600x600 -fuzz 2% +dither -remap /tmp/globe.gif[20] +dither -colors 14 -layers Optimize /tmp/globe_small.gif')
        # Also we will make a video of the scene - useful for cases where you have a larger colour
        # pallette and gif will not hack it
        # Pad option is to deal with cases where ffmpeg complains because the h or w of the image
        # is an odd number of pixels.
        # :color=white pads the video with white pixels. Change to black if needed.
        #os.system('ffmpeg -framerate 30 -pattern_type glob -i "/tmp/globe-*.png" -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white" -c:v libx264 -pix_fmt yuv420p /tmp/globe.mp4')


    def initialize_debugger():
        import multiprocessing
        if multiprocessing.current_process().pid > 1:
            import debugpy
            debugpy.listen(("0.0.0.0", 9000))
            print("Debugger is ready to be attached, press F5", flush=True)
            debugpy.wait_for_client()
            print("Visual Studio Code debugger is now attached", flush=True)


    def render_image(self, name):
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
        global current_render_thread_count
        print('Freeing render lock.')
        current_render_thread_count -= 1
        print(' Now %d threads used ' % current_render_thread_count)

    def render_image_as_task(self,name,current_point_id,current_frame):
        global current_render_thread_count, render_thread_pool_size
        # Block until there is space in the render thread pool
        while current_render_thread_count > render_thread_pool_size:
            time.sleep(1.0)
            print('Waiting for render lock.')
            current_render_thread_count -= 1
            print(' Now %d threads used ' % current_render_thread_count)
        # Ready to start rendering, claim a space in the pool
        current_render_thread_count += 1
        size = self.iface.mapCanvas().size()
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
        task_scope.setVariable('frames_per_point', frames_per_point)
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
        QgsApplication.taskManager().addTask( mapRendererTask )

    def fly_point_to_point(self, start_point, end_point):
        global image_counter, frames_per_point, last_easing
        with open('/tmp/log.txt', 'a') as f: # change to append too record all
            f.write('Feature: %d\n' % end_point.id())
            #f.write('Render Time,Longitude,Latitude,Latitude Easing Factor,Zoom Easing Factor,Zoom Scale\n')
            image_counter += 1
            x_min = start_point.geometry().asPoint().x()
            print("XMIN : %f" % x_min)
            x_max = end_point.geometry().asPoint().x()
            print("XMAX : %f" % x_max)
            x_range = abs(x_max - x_min)
            print("XRANGE : %f" % x_range)
            x_increment = x_range / frames_per_point
            y_min = start_point.geometry().asPoint().y()
            print("YMIN : %f" % y_min)
            y_max = end_point.geometry().asPoint().y()
            print("YMAX : %f" % y_max)
            y_range = abs(y_max - y_min)
            print("YRANGE : %f" % y_range)
            y_increment = y_range / frames_per_point
            global pan_easing_enabled
            # See https://doc.qt.io/qt-5/qeasingcurve.html#Type-enum
            # For the full list of available easings
            # This is just to change up the easing from one point hop 
            # to the next
            if EasingMode == EasingMode.EASE_OUT:
                pan_easing = QEasingCurve(QEasingCurve.OutBack)
                zoom_easing = QEasingCurve(QEasingCurve.OutBack)
                EasingMode == EasingMode.EASE_IN
            else:
                pan_easing = QEasingCurve(QEasingCurve.InBack)
                zoom_easing = QEasingCurve(QEasingCurve.InBack)
                last_easing = 0

            for current_frame in range(0, frames_per_point, 1):
                x_offset = x_increment * current_frame
                x = x_min + x_offset 
                y_offset = y_increment * current_frame
                if pan_easing_enabled:
                    y_easing_factor = y_offset / frames_per_point 
                    y = y_min + (y_offset * pan_easing.valueForProgress(y_easing_factor))
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
                    zoom_easing_factor = zoom_easing.valueForProgress(
                        current_frame/frames_per_point)
                    scale = ((max_scale - min_scale) * zoom_easing_factor) + min_scale
                    if zoom_easing_factor == 1:
                        self.iface.mapCanvas().zoomToFullExtent()
                    else:
                        if self.map_mode == MapMode.SPHERE:
                            self.iface.mapCanvas().zoomScale(scale)
                        else:
                            self.iface.mapCanvas().setCenter(
                                QgsPointXY(x,y))
                            iface.mapCanvas().zoomScale(scale)
                
                # Pad the numbers in the name so that they form a 10 digit string with left padding of 0s
                name = ('/tmp/globe-%s.png' % str(image_counter).rjust(10, '0'))
                starttime = timeit.default_timer()
                # Not crashy but no decorations and annotations....
                #render_image(name)
                # crashy - check with Nyall why...
                render_image_as_task(name, end_point.id(), current_frame)
                #f.write('%s,%f,%f,%f,%f,%f\n' % (
                #    timeit.default_timer() - starttime, 
                #    x, 
                #    y, 
                #    y_easing_factor, 
                #    zoom_easing_factor, 
                #    scale))
                image_counter += 1

    def dwell_at_point(feature):
        global image_counter, dwell_frames
        #f.write('Render Time,Longitude,Latitude,Latitude Easing Factor,Zoom Easing Factor,Zoom Scale\n')
        x = feature.geometry().asPoint().x()
        y = feature.geometry().asPoint().y()
        point = QgsPointXY(x,y)
        iface.mapCanvas().setCenter(point)
        iface.mapCanvas().zoomScale(min_scale)
        for current_frame in range(0, dwell_frames, 1):
            # Pad the numbers in the name so that they form a 10 digit string with left padding of 0s
            name = ('/tmp/globe-%s.png' % str(image_counter).rjust(10, '0'))
            # Not crashy but no decorations and annotations....
            #render_image(name)
            # crashy - check with Nyall why...
            render_image_as_task(name, feature.id(), current_frame)
            image_counter += 1

