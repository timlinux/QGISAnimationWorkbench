# coding=utf-8

"""Init for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = '$Format:%H$'

#-----------------------------------------------------------
# Copyright (C) 2022 Tim Sutton
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

# DO NOT REMOVE THIS - it forces sip2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.core import (
    QgsProject,
    QgsExpressionContextScope,
    QgsMapRendererTask,
    QgsApplication)
from .animation_workbench import AnimationWorkbench
from .utilities import resources_path
from .settings import setting

def classFactory(iface):
    return AnimationWorkbenchPlugin(iface)

class AnimationWorkbenchPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        
        # If you change this to true, QGIS startup
        # will block until it can attache to the remote debugger
        debug_mode = False
        if debug_mode:
            try:
                self.initialize_debugger()
            except:
                pass

        icon = QIcon(resources_path(
            'img', 'icons', 'animation-workbench.svg'))
        self.action = QAction(
            icon, 
            'Animation Workbench', 
            self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
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

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action
    
    def initialize_debugger(self):
        import multiprocessing
        if multiprocessing.current_process().pid > 1:
            import debugpy
            debugpy.listen(("0.0.0.0", 9000))
            print("Debugger is ready to be attached, press F5", flush=True)
            debugpy.wait_for_client()
            print("Visual Studio Code debugger is now attached", flush=True)

    def run(self):
        dialog = AnimationWorkbench(iface=self.iface)
        dialog.exec_()

    def process_more_tasks(self):
        """
        Feed the QgsTaskManager with another bundle of tasks.

        This slot is called whenever the QgsTaskManager queue is 
        finished (by means of the 'allTasksFinished' signal).

        :returns: None
        """
        self.total_tasks_lcd.display(self.total_frame_count)
        self.completed_tasks_lcd.display(
            self.total_frame_count - len(self.renderer_queue))        
        if len(self.renderer_queue) == 0:
            # all processing done so go off and generate
            # the vid or gif
            self.show_status()
            self.processing_completed()
            self.progress_bar.setValue(0)
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

        # We will put this task in a separate queue and then pop them off the queue
        # at a time whenver the task manager
        # lets us know we have nothing to do
        # Start the rendering task on the queue
        task_id = QgsApplication.taskManager().addTask(mapRendererTask)