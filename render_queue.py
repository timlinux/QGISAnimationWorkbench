# coding=utf-8

"""Render Queue for keeping track of render tasks."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

# -----------------------------------------------------------
# Copyright (C) 2022 Tim Sutton
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

# DO NOT REMOVE THIS - it forces sip2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from qgis.core import (
    QgsProject,
    QgsExpressionContextScope,
    QgsMapRendererTask,
    QgsApplication)

from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QImage, QPainter
from qgis.core import (
    QgsProject,
    QgsApplication,
    QgsMapRendererCustomPainterJob)
from .settings import setting


class RenderQueue(QObject):

    # Signal emitted when the easing is changed
    easing_changed_signal = pyqtSignal(int)

    def __init__(self, parent=None, iface=None):
        super().__init__(parent=parent)
        self.iface = iface
        # The maximum number of concurrent threads to allow
        # during rendering. Probably setting to the same number
        # of CPU cores you have would be a good conservative approach
        # You could probably run 100 or more on a decently specced machine
        self.render_thread_pool_size = int(setting(
            key='render_thread_pool_size', default=100))
        # A list of tasks that need to be rendered but
        # cannot be because the job queue is too full.
        # we pop items off this list self.render_thread_pool_size
        # at a time whenver the task manager tells us the queue is
        # empty.
        self.renderer_queue = []
        # Queue manager for above.
        QgsApplication.taskManager().allTasksFinished.connect(
            self.process_more_tasks)
        self.frames_per_feature = 0
        self.image_counter = 0
        self.total_frame_count = 0

    def process_more_tasks(self):
        """
        Feed the QgsTaskManager with another bundle of tasks.

        This slot is called whenever the QgsTaskManager queue is 
        finished (by means of the 'allTasksFinished' signal).

        :returns: None
        """
        # self.total_tasks_lcd.display(self.total_frame_count)
        # self.completed_tasks_lcd.display(
        #    self.total_frame_count - len(self.renderer_queue))
        if len(self.renderer_queue) == 0:
            # all processing done so go off and generate
            # the vid or gif
            # self.show_status()
            # self.processing_completed()
            # self.progress_bar.setValue(0)
            pass
        else:
            self.output_log_text_edit.append(
                'Thread pool emptied, adding more tasks')
            pop_size = self.render_thread_pool_size
            if len(self.renderer_queue) < pop_size:
                pop_size = len(self.renderer_queue)
            for task in range(0, pop_size):
                task_id = QgsApplication.taskManager().addTask(
                    self.renderer_queue.pop(0))
            self.progress_bar.setValue(
                self.progress_bar.value() * pop_size)

    def render_image_as_task(
            self,
            name,
            current_feature_id,
            current_frame,
            action='None'):

        #size = self.iface.mapCanvas().size()
        settings = self.iface.mapCanvas().mapSettings()
        # The next part sets project variables that you can use in your
        # cartography etc. to see the progress. Here is an example
        # of a QGS expression you can use in the map decoration copyright
        # widget to show current script progress
        # [%'Frame ' || to_string(coalesce(@current_frame, 0)) || '/' ||
        # to_string(coalesce(@frames_per_feature, 0)) || ' for feature ' ||
        # to_string(coalesce(@current_feature_id,0))%]
        task_scope = QgsExpressionContextScope()
        task_scope.setVariable('current_feature_id', current_feature_id)
        task_scope.setVariable('frames_per_feature', self.frames_per_feature)
        task_scope.setVariable('current_frame_for_feature', current_frame)
        task_scope.setVariable('current_animation_action', action)
        task_scope.setVariable('current_frame', self.image_counter)
        task_scope.setVariable('total_frame_count', self.total_frame_count)

        context = settings.expressionContext()
        context.appendScope(task_scope)
        settings.setExpressionContext(context)
        # Set the output file name for the render task
        mapRendererTask = QgsMapRendererTask(settings, name, "PNG")
        # We need to clone the annotations because otherwise SIP will
        # pass ownership and then cause a crash when the render task is
        # destroyed
        annotations = QgsProject.instance().annotationManager().annotations()
        annotations_list = [a.clone() for a in annotations]
        if (len(annotations_list) > 0):
            mapRendererTask.addAnnotations([a.clone() for a in annotations])
        # Add decorations to the render job
        decorations = self.iface.activeDecorations()
        mapRendererTask.addDecorations(decorations)

        # We will put this task in a separate queue and then pop them off
        # the queue at a time whenver the task manager lets us know we have
        # nothing to do.
        task_id = QgsApplication.taskManager().addTask(mapRendererTask)

    def render_image(self):
        """Render the current canvas to an image.

        .. note:: This is renders synchronously. 

        .. deprecated We should deprecate this - it is currently only used
            when making a preview 

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
