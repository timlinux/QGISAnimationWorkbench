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
# from grpc import StatusCode
import qgis  # pylint: disable=unused-import

from qgis.core import (
    QgsProject,
    QgsExpressionContextScope,
    QgsMapRendererTask,
    QgsTask,
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

    # Signals
    status_changed = pyqtSignal()
    processing_completed = pyqtSignal()
    status_message = pyqtSignal(str)
    # Sends the path to each frame as it is rendered
    image_rendered = pyqtSignal(str)

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
        # Used to keep a list of the task ids and the
        # image they will output to because we cannot find out the
        # image path from the QgsMapRendererTask
        self.task_dict = {}
        self.verbose_mode = int(setting(key='verbose_mode', default=0))
        self.total_queue_size = 0
        self.active_queue_size = 0
        self.total_completed = 0
        self.total_feature_count = 0
        self.completed_feature_count = 0
        # Records how many jobs were scheduled last
        # can differ from render_thread_pool_size if
        # we are near the end of the queue
        self.last_pool_size = 0

        self.frames_per_feature = 0
        self.image_counter = 0
        self.total_frame_count = 0
        # Queue manager for above.
        QgsApplication.taskManager().allTasksFinished.connect(
            self.process_more_tasks)
        QgsApplication.taskManager().progressChanged.connect(
            self.update_status)
        QgsApplication.taskManager().statusChanged.connect(
            self.task_status_changed)

    # slot
    def task_status_changed(self, task_id, status):
        if status == QgsTask.TaskStatus.Complete:
            try:
                file_name = self.task_dict[task_id]
                self.image_rendered.emit(file_name)
            except:
                pass

    def reset(self):
        self.renderer_queue.clear()
        self.task_dict.clear()
        self.total_queue_size = 0
        self.active_queue_size = 0
        self.total_completed = 0
        self.total_feature_count = 0
        self.completed_feature_count = 0

        self.frames_per_feature = 0
        self.image_counter = 0
        self.total_frame_count = 0
        self.status_changed.emit()

    def update_status(self):
        # make sure internal counters are consistent
        # then emit a signal to let watchers know the counts
        # have been updated
        self.active_queue_size = QgsApplication.taskManager().countActiveTasks()
        if self.frames_per_feature:
            self.total_feature_count = int(
                self.total_queue_size / self.frames_per_feature)
            self.completed_feature_count = int(
                self.total_completed / self.frames_per_feature)
        self.status_changed.emit()

    def process_more_tasks(self):
        """
        Feed the QgsTaskManager with another bundle of tasks.

        This slot is called whenever the QgsTaskManager queue is
        finished (by means of the 'allTasksFinished' signal).

        :returns: None
        """
        # Note we might get some side effects here if the task
        # manager is running other tasks not related to this plugin
        self.total_completed += self.last_pool_size
        # self.total_tasks_lcd.display(self.total_frame_count)
        # self.completed_tasks_lcd.display(
        #    self.total_frame_count - len(self.renderer_queue))
        if len(self.renderer_queue) == 0:
            # all processing done
            self.update_status()
            self.processing_completed.emit()
        else:
            self.last_pool_size = self.render_thread_pool_size
            if len(self.renderer_queue) < self.last_pool_size:
                self.last_pool_size = len(self.renderer_queue)
            for item in range(0, self.last_pool_size):
                task = self.renderer_queue.pop(0)
                task_id = QgsApplication.taskManager().addTask(
                    task)
                self.task_dict[task_id] = task.objectName()

                if self.verbose_mode:
                    self.status_message.emit(
                        'Rendering: %s' % task.objectName())
                    # Would be nicer but not supported:
                    # 'Rendering: %s' % task.name())

    def queue_task(
            self,
            name,
            current_feature_id,
            current_frame,
            action='None'):

        self.total_queue_size += 1
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

        # We use QObject.setObjectName to store the file name
        # because the QgsMapRenderer task does not store it
        mapRendererTask.setObjectName(name)
        # We will put this task in a separate queue and then pop them off
        # the queue at a time whenver the task manager lets us know we have
        # nothing to do.
        self.renderer_queue.append(mapRendererTask)
        mapRendererTask.taskCompleted.connect(self.update_status)
        #task_id = QgsApplication.taskManager().addTask(mapRendererTask)
        self.update_status()

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
