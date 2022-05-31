# coding=utf-8
"""This module has the expression context for the AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

# This will make the QGIS use a world projection and then move the center
# of the CRS sequentially to create a spinning globe effect

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProject,
    QgsExpressionContextGenerator,
    QgsExpressionContext,
    QgsVectorLayer,
)


class DialogExpressionContextGenerator(QgsExpressionContextGenerator):
    """
    An expression context generator for widgets in the dialog
    """

    def __init__(self):
        super().__init__()
        self.layer = None

    def set_layer(self, layer: QgsVectorLayer):
        """
        Sets the layer associated with the dialog
        """
        self.layer = layer

    # pylint: disable=missing-function-docstring
    def createExpressionContext(
        self,
    ) -> QgsExpressionContext:
        context = QgsExpressionContext()
        context.appendScope(QgsExpressionContextUtils.globalScope())
        context.appendScope(
            QgsExpressionContextUtils.projectScope(QgsProject.instance())
        )
        if self.layer:
            context.appendScope(self.layer.createExpressionContextScope())
        return context
