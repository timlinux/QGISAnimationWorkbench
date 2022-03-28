# coding=utf-8

"""Render Queue for keeping track of render tasks."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

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

from functools import partial
from typing import List, Optional

# DO NOT REMOVE THIS - it forces sip2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QImage
from qgis.core import QgsApplication, QgsMapRendererParallelJob
from qgis.core import (
    QgsMapRendererTask,
    QgsMapSettings,
    QgsProxyProgressTask,
    QgsFeedback,
    Qgis,
    QgsTask
)

from .settings import setting


class RenderJob:
    def __init__(self, file_name: str, map_settings: QgsMapSettings):
        self.file_name: str = file_name
        self.map_settings: QgsMapSettings = map_settings

    def render_to_image(self) -> QImage:
        render_job = QgsMapRendererParallelJob(self.map_settings)
        render_job.start()
        render_job.waitForFinished()
        return render_job.renderedImage()

    def create_task(
        self,
        annotations_list: Optional[List] = None,
        decorations: Optional[List] = None,
        hidden: bool = False
    ) -> QgsMapRendererTask:
        # Set the output file name for the render task

        if Qgis.QGIS_VERSION_INT >= 32500 and hidden:
            # can only mark tasks as hidden on 3.26+
            task = QgsMapRendererTask(self.map_settings, self.file_name, "PNG", flags=QgsTask.Flags(QgsTask.Hidden|QgsTask.CanCancel))
        else:
            task = QgsMapRendererTask(self.map_settings, self.file_name, "PNG")
        # We need to clone the annotations because otherwise SIP will
        # pass ownership and then cause a crash when the render task is
        # destroyed
        if annotations_list:
            cloned_annotations = [a.clone() for a in annotations_list]
            task.addAnnotations(cloned_annotations)

        # Add decorations to the render job
        if decorations:
            task.addDecorations(decorations)
        return task


class RenderQueueFeedback(QgsFeedback):

    def __init__(self, steps: int):
        super().__init__()
        self.steps = steps
        self.current_step = 0

    def set_current_step(self, step: int):
        self.current_step = step
        self.setProgress(100*self.current_step/self.steps)

    def set_remaining_steps(self, remaining: int):
        self.set_current_step(self.steps - remaining)


class RenderQueue(QObject):
    # Signals
    status_changed = pyqtSignal()
    processing_completed = pyqtSignal(bool)
    status_message = pyqtSignal(str)
    # Sends the path to each frame as it is rendered
    image_rendered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # The maximum number of concurrent threads to allow
        # during rendering. Probably setting to the same number
        # of CPU cores you have would be a good conservative approach
        # You could probably run 100 or more on a decently specced machine
        self.render_thread_pool_size = int(
            setting(key="render_thread_pool_size", default=100)
        )
        # A list of tasks that need to be rendered but
        # cannot be because the job queue is too full.
        # we pop items off this list self.render_thread_pool_size
        # at a time whenever the task manager tells us the queue is
        # empty.
        self.job_queue: List[RenderJob] = []
        self.active_tasks = {}

        # "parent" task which just reports overall progress of the queue
        self.proxy_task: Optional[QgsProxyProgressTask] = None
        self.proxy_feedback: Optional[RenderQueueFeedback] = None

        self.verbose_mode = int(setting(key="verbose_mode", default=0))
        self.total_queue_size = 0
        self.total_completed = 0
        self.total_feature_count = 0
        self.completed_feature_count = 0
        self.annotations_list = []
        self.decorations = []

        self.frames_per_feature = 0

    def active_queue_size(self) -> int:
        return len(self.active_tasks)

    def reset(self):
        self.job_queue.clear()
        self.active_tasks.clear()
        self.proxy_task = None
        self.proxy_feedback = None

        self.total_queue_size = 0
        self.total_completed = 0
        self.total_feature_count = 0
        self.completed_feature_count = 0

        self.frames_per_feature = 0
        self.annotations_list = []
        self.decorations = []

        self.update_status()

    def cancel_processing(self):
        self.job_queue.clear()
        self.total_queue_size = 0
        self.total_completed = 0
        self.total_feature_count = 0
        self.completed_feature_count = 0

        self.proxy_feedback.cancel()

        for _, task in self.active_tasks.items():
            task.cancel()

        if self.proxy_task:
            self.proxy_task.finalize(False)
            self.proxy_task = None

        self.frames_per_feature = 0
        self.annotations_list = []
        self.decorations = []
        self.status_message.emit(f"Cancelling...")

    def update_status(self):
        # make sure internal counters are consistent
        # then emit a signal to let watchers know the counts
        # have been updated
        self.status_changed.emit()

    def start_processing(self):
        if Qgis.QGIS_VERSION_INT >= 32500:
            self.proxy_task = QgsProxyProgressTask('Exporting frames', True)
            self.proxy_task.canceled.connect(self.cancel_processing)
        else:
            # can't set a proxy task as cancelable in < 3.26 :(
            self.proxy_task = QgsProxyProgressTask('Exporting frames')

        self.proxy_feedback = RenderQueueFeedback(len(self.job_queue))
        self.proxy_feedback.progressChanged.connect(self.proxy_task.setProxyProgress)

        QgsApplication.taskManager().addTask(self.proxy_task)

        self.process_queue()

    def process_queue(self):
        """
        Feed the QgsTaskManager with next task
        """
        if not self.job_queue and not self.active_tasks:
            # all done!
            self.update_status()
            was_canceled = self.proxy_feedback and self.proxy_feedback.isCanceled()
            self.processing_completed.emit(not was_canceled)
            if self.proxy_task:
                self.proxy_task.finalize(not was_canceled)
                self.proxy_task = None
            return

        if not self.job_queue:
            # no more jobs to add, but still running some jobs
            self.update_status()
            return

        free_threads = self.render_thread_pool_size - len(self.active_tasks)
        for _ in range(free_threads):
            job = self.job_queue.pop(0)
            if self.verbose_mode:
                self.status_message.emit(f"Rendering: {job.file_name}")

            # create a hidden task, because the proxy wrapper task will be the only one we want
            # to expose to users
            task = job.create_task(self.annotations_list, self.decorations, hidden=True)
            self.active_tasks[job.file_name] = task

            task.taskCompleted.connect(
                partial(self.task_completed, file_name=job.file_name)
            )
            task.taskTerminated.connect(
                partial(self.finalize_task, file_name=job.file_name)
            )

            QgsApplication.taskManager().addTask(task)
            self.proxy_feedback.set_remaining_steps(len(self.job_queue))

        self.update_status()

    def task_completed(self, file_name: str):
        self.image_rendered.emit(file_name)
        self.finalize_task(file_name)

    def finalize_task(self, file_name: str):
        del self.active_tasks[file_name]
        self.total_completed += 1

        if self.frames_per_feature:
            self.completed_feature_count = int(
                self.total_completed / self.frames_per_feature
            )

        self.status_changed.emit()
        self.process_queue()

    def set_annotations(self, annotations):
        self.annotations_list = [a.clone() for a in annotations]

    def set_decorations(self, decorations):
        self.decorations = decorations

    def add_job(self, job: RenderJob):
        self.job_queue.append(job)
        self.total_queue_size += 1
