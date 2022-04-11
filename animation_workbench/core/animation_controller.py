# coding=utf-8
"""This module has the main core animation logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Iterator, List

from qgis.PyQt.QtCore import QObject, pyqtSignal, QEasingCurve
from qgis.core import (
    QgsPointXY,
    QgsWkbTypes,
    QgsProject,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsReferencedRectangle,
    QgsVectorLayer,
    QgsMapSettings,
    QgsExpressionContextScope,
    QgsRectangle,
    QgsFeature,
    QgsMapLayerUtils,
    Qgis,
    QgsPropertyDefinition,
    QgsPropertyCollection,
    QgsExpressionContext,
    QgsExpressionContextUtils,
)

from .render_queue import RenderJob
from .utilities import calculate_cardinality


class MapMode(Enum):
    """
    Map animation modes
    """

    SPHERE = 1  # CRS will be manipulated to create a spinning globe effect
    PLANAR = 2  # CRS will not be altered, extents will as we pan and zoom
    FIXED_EXTENT = 3  # EASING and ZOOM disabled, extent stays in place


class InvalidAnimationParametersException(Exception):
    """
    Raised when animation parameters are not valid
    """


class AnimationController(QObject):
    """
    Creates animation frames
    """

    normal_message = pyqtSignal(str)
    verbose_message = pyqtSignal(str)

    PROPERTY_MIN_SCALE = 1
    PROPERTY_MAX_SCALE = 2

    DYNAMIC_PROPERTIES = {
        PROPERTY_MIN_SCALE: QgsPropertyDefinition(
            "min_scale", "Minimum scale", QgsPropertyDefinition.DoublePositive
        ),
        PROPERTY_MAX_SCALE: QgsPropertyDefinition(
            "max_scale", "Maximum scale", QgsPropertyDefinition.DoublePositive
        ),
    }

    ACTION_HOVERING = "Hovering"
    ACTION_TRAVELLING = "Travelling"

    @staticmethod
    def create_fixed_extent_controller(
        map_settings: QgsMapSettings,
        feature_layer: Optional[QgsVectorLayer],
        output_extent: QgsReferencedRectangle,
        total_frames: int,
        frame_rate: float,
    ) -> "AnimationController":
        """
        Creates an animation controller for a fixed extent animation
        """
        transformed_output_extent = QgsRectangle(output_extent)
        if output_extent.crs() != map_settings.destinationCrs():
            ct = QgsCoordinateTransform(
                output_extent.crs(),
                map_settings.destinationCrs(),
                QgsProject.instance(),
            )
            ct.setBallparkTransformsAreAppropriate(True)
            transformed_output_extent = ct.transformBoundingBox(output_extent)
        map_settings.setExtent(transformed_output_extent)

        controller = AnimationController(MapMode.FIXED_EXTENT, map_settings)
        if feature_layer:
            controller.set_layer(feature_layer)
        controller.total_frame_count = total_frames
        controller.frame_rate = frame_rate

        return controller

    @staticmethod
    def create_moving_extent_controller(
        map_settings: QgsMapSettings,
        mode: MapMode,
        feature_layer: QgsVectorLayer,
        travel_duration: float,
        hover_duration: float,
        min_scale: float,
        max_scale: float,
        pan_easing: Optional[QEasingCurve],
        zoom_easing: Optional[QEasingCurve],
        frame_rate: float,
        loop: bool = False,
    ) -> "AnimationController":
        """
        Creates an animation controller for a moving extent animation
        """

        if not feature_layer:
            raise InvalidAnimationParametersException("No animation layer set")

        controller = AnimationController(mode, map_settings)
        controller.set_layer(feature_layer)
        controller.loop = loop

        hover_frames = hover_duration * frame_rate
        travel_frames = travel_duration * frame_rate

        controller.total_frame_count = int(
            (
                controller.total_feature_count * hover_frames
                + (
                    (controller.total_feature_count - 1)
                    if not loop
                    else controller.total_feature_count
                )
                * travel_frames
            )
        )  # nopep8

        controller.hover_duration = hover_duration
        controller.travel_duration = travel_duration

        controller.min_scale = min_scale
        controller.max_scale = max_scale

        controller.pan_easing = pan_easing
        controller.zoom_easing = zoom_easing

        controller.frame_rate = frame_rate

        return controller

    def __init__(self, map_mode: MapMode, map_settings: QgsMapSettings):
        super().__init__()
        self.map_settings: QgsMapSettings = map_settings
        self.map_mode: MapMode = map_mode

        self.base_expression_context = QgsExpressionContext()
        self.base_expression_context.appendScope(
            QgsExpressionContextUtils.globalScope()
        )
        self.base_expression_context.appendScope(
            QgsExpressionContextUtils.projectScope(QgsProject.instance())
        )

        self.data_defined_properties = QgsPropertyCollection()

        self.feature_layer: Optional[QgsVectorLayer] = None
        self._features: List[QgsFeature] = []
        self.layer_to_map_transform: Optional[QgsCoordinateTransform] = None
        self.total_feature_count: int = 0

        self.total_frame_count: int = 0

        self.hover_duration: float = 0
        self.travel_duration: float = 0
        self.loop: bool = False

        self.max_scale: float = 0
        self.min_scale: float = 0

        self._evaluated_min_scale = None
        self._evaluated_max_scale = None

        self.pan_easing: Optional[QEasingCurve] = None
        self.zoom_easing: Optional[QEasingCurve] = None

        self.frame_rate: float = 30

        self.current_frame = 0

        self.working_directory: Path = Path(tempfile.gettempdir())
        self.frame_filename_prefix: str = "animation_workbench"

        self.reuse_cache: bool = False

    def set_layer(self, layer: QgsVectorLayer):
        """
        Sets the layer driving the animation
        """
        self.feature_layer = layer
        self.total_feature_count = layer.featureCount()
        self.base_expression_context.appendScope(layer.createExpressionContextScope())

        # preload all features into a list, so that we can easily retrieve previous/next features
        # This is not so nice for large layers, but it's unlikely that someone will be making
        # an animation with 10k's of features anyway...!
        self._features = list(self.feature_layer.getFeatures())

    def create_job_for_frame(self, frame: int) -> Optional[RenderJob]:
        """
        Creates a render job corresponding to a specific frame
        """
        # Catch for case where preview widget asks for an invalid frame
        if frame > self.total_frame_count:
            return None
        job = None
        # inefficient, but we can rework later if needed!
        jobs = self.create_jobs()
        for _ in range(frame + 1):
            job = next(jobs)
        return job

    def create_jobs(self) -> Iterator[RenderJob]:
        """
        Yields render jobs for each animation frame
        """
        if self.map_mode == MapMode.FIXED_EXTENT:
            if self.feature_layer:
                self.layer_to_map_transform = QgsCoordinateTransform(
                    self.feature_layer.crs(),
                    self.map_settings.destinationCrs(),
                    QgsProject.instance(),
                )

            for job in self.create_fixed_extent_job():
                yield job
        else:
            self.layer_to_map_transform = QgsCoordinateTransform(
                self.feature_layer.crs(),
                self.map_settings.destinationCrs(),
                QgsProject.instance(),
            )
            for job in self.create_moving_extent_job():
                yield job

    def create_fixed_extent_job(self) -> Iterator[RenderJob]:
        """
        Yields render jobs for fixed extent animations
        """
        # If the feature_layer is set we split the job
        # across the number of features and the frame
        # count so that we can set the current feature id
        # iteratively
        if not self.feature_layer:
            for self.current_frame in range(self.total_frame_count):
                name = self.working_directory / "{}-{}.png".format(
                    self.frame_filename_prefix,
                    str(self.current_frame).rjust(10, "0"),
                )

                job = self.create_job(self.map_settings, name.as_posix())
                yield job

                self.current_frame += 1
        else:
            self.total_feature_count = len(self._features)

            # Need to refactor range param below so that it uses
            # a frames per feature option rather than the misleadingly
            # named total_frame_count (which is only storing frames per
            # feature in this context).
            hover_frames = self.total_frame_count

            for feature_idx, feature in enumerate(self._features):
                self.base_expression_context.setFeature(feature)

                for frame_for_feature in range(hover_frames):
                    name = self.working_directory / "{}-{}.png".format(
                        self.frame_filename_prefix,
                        str(self.current_frame).rjust(10, "0"),
                    )

                    scope = QgsExpressionContextScope()
                    scope.setVariable(
                        "previous_feature",
                        None if feature_idx == 0 else self._features[feature_idx - 1],
                        True,
                    )
                    scope.setVariable(
                        "previous_feature_id",
                        None
                        if feature_idx == 0
                        else self._features[feature_idx - 1].id(),
                        True,
                    )
                    scope.setVariable(
                        "next_feature",
                        None
                        if feature_idx == len(self._features) - 1
                        else self._features[feature_idx + 1],
                        True,
                    )
                    scope.setVariable(
                        "next_feature_id",
                        None
                        if feature_idx == len(self._features) - 1
                        else self._features[feature_idx + 1].id(),
                        True,
                    )

                    scope.setVariable("hover_feature", feature, True)
                    scope.setVariable("hover_feature_id", feature.id(), True)

                    scope.setVariable("current_hover_frame", frame_for_feature)
                    scope.setVariable("hover_frames", hover_frames)

                    scope.setVariable(
                        "current_animation_action", AnimationController.ACTION_HOVERING
                    )

                    job = self.create_job(
                        self.map_settings,
                        name.as_posix(),
                        additional_expression_context_scopes=[scope],
                    )
                    yield job

                    self.current_frame += 1

    def create_moving_extent_job(self) -> Iterator[RenderJob]:
        """
        Yields render jobs for moving extent animations
        """
        self._evaluated_min_scale = self.min_scale

        self.set_to_scale(self.min_scale)
        feature = None
        for feature_idx, feature in enumerate(self._features):
            self.base_expression_context.setFeature(feature)
            if feature_idx == 0:
                # first feature, need to evaluate the starting scale
                context = QgsExpressionContext(self.base_expression_context)
                context.appendScope(
                    QgsExpressionContextUtils.mapSettingsScope(self.map_settings)
                )

                self._evaluated_max_scale = self.max_scale
                if self.data_defined_properties.hasActiveProperties():
                    (
                        self._evaluated_max_scale,
                        _,
                    ) = self.data_defined_properties.valueAsDouble(
                        AnimationController.PROPERTY_MAX_SCALE,
                        context,
                        self.max_scale,
                    )

            context = QgsExpressionContext(self.base_expression_context)
            context.appendScope(
                QgsExpressionContextUtils.mapSettingsScope(self.map_settings)
            )
            context.setFeature(feature)

            scope = QgsExpressionContextScope()
            scope.setVariable(
                "from_feature",
                None if feature_idx == 0 else self._features[feature_idx - 1],
                True,
            )
            scope.setVariable(
                "from_feature_id",
                None if feature_idx == 0 else self._features[feature_idx - 1].id(),
                True,
            )
            scope.setVariable("to_feature", feature, True)
            scope.setVariable("to_feature_id", feature.id(), True)

            scope.setVariable("hover_feature", feature, True)
            scope.setVariable("hover_feature_id", feature.id(), True)
            context.appendScope(scope)

            # update min scale as soon as we are ready to move to the next feature
            self._evaluated_min_scale = self.min_scale
            if self.data_defined_properties.hasActiveProperties():
                (
                    self._evaluated_min_scale,
                    _,
                ) = self.data_defined_properties.valueAsDouble(
                    AnimationController.PROPERTY_MIN_SCALE,
                    context,
                    self.min_scale,
                )

            if feature_idx > 0:
                for job in self.fly_feature_to_feature(
                    self._features[feature_idx - 1], feature
                ):
                    yield job

            for job in self.hover_at_feature(feature_idx):
                yield job

        if self.loop and len(self._features) > 1:
            # insert extra loop back to first feature
            for job in self.fly_feature_to_feature(feature, self._features[0]):
                yield job

    def set_extent_center(self, center_x: float, center_y: float):
        """
        Sets the animation to a specific map center coordinate
        """
        prev_extent = self.map_settings.visibleExtent()
        x_min = center_x - prev_extent.width() / 2
        y_min = center_y - prev_extent.height() / 2
        new_extent = QgsRectangle(
            x_min,
            y_min,
            x_min + prev_extent.width(),
            y_min + prev_extent.height(),
        )
        self.map_settings.setExtent(new_extent)

    def set_to_scale(self, scale: float):
        """
        Sets the animation to a specific scale
        """
        scale_factor = scale / self.map_settings.scale()
        r = self.map_settings.extent()
        r.scale(scale_factor)
        self.map_settings.setExtent(r)

    def zoom_to_full_extent(self):
        """
        Zoom to the full extent of layers in map settings
        """
        full_extent = QgsMapLayerUtils.combinedExtent(
            self.map_settings.layers(),
            self.map_settings.destinationCrs(),
            QgsProject.instance().transformContext(),
        )
        if not full_extent.isEmpty():
            # add 5% margin around full extent
            full_extent.scale(1.05)
            self.map_settings.setExtent(full_extent)

    def geometry_to_pointxy(self, feature: QgsFeature) -> Optional[QgsPointXY]:
        """
        Converts a feature's geometry to a single point
        """
        geom = feature.geometry()

        # use simplified type, so that we don't have to care
        # about multipolygons/lines with just single part!
        raw_geom = geom.constGet().simplifiedTypeRef()
        flat_type = QgsWkbTypes.flatType(raw_geom.wkbType())

        if flat_type == QgsWkbTypes.Point:
            x = raw_geom.x()
            y = raw_geom.y()
            center = QgsPointXY(x, y)
        elif flat_type == QgsWkbTypes.LineString:
            length = geom.length()
            point = geom.interpolate(length / 2.0)
            x = point.geometry().x()
            y = point.geometry().y()
            center = QgsPointXY(x, y)
        elif flat_type == QgsWkbTypes.Polygon:
            center = geom.centroid().asPoint()
        else:
            self.verbose_message.emit(
                "Unsupported Feature Geometry Type: {}".format(
                    QgsWkbTypes.displayString(raw_geom.wkbType())
                )
            )
            center = None
        return center

    def hover_at_feature(self, feature_idx: int) -> Iterator[RenderJob]:
        """
        Wait at a feature to emphasise it in the video.

        :param feature_idx: index of feature to hover at
        """
        feature = self._features[feature_idx]
        if not self.loop:
            previous_feature = (
                None if feature_idx == 0 else self._features[feature_idx - 1]
            )
            next_feature = (
                None
                if feature_idx == len(self._features) - 1
                else self._features[feature_idx + 1]
            )
        else:
            # next and previous features must wrap around
            previous_feature = (
                self._features[-1]
                if feature_idx == 0
                else self._features[feature_idx - 1]
            )
            next_feature = (
                self._features[0]
                if feature_idx == len(self._features) - 1
                else self._features[feature_idx + 1]
            )

        center = self.geometry_to_pointxy(feature)
        if not center:
            self.normal_message.emit("Unsupported geometry, skipping.")
            return

        center = self.layer_to_map_transform.transform(center)
        self.set_extent_center(center.x(), center.y())
        self.set_to_scale(self._evaluated_max_scale)
        # Change CRS if needed
        if self.map_mode == MapMode.SPHERE:
            definition = """ +proj=ortho \
                +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 \
                +ellps=sphere +units=m +no_defs""" % (
                center.y(),
                center.x(),
            )
            crs = QgsCoordinateReferenceSystem()
            crs.createFromProj(definition)
            self.map_settings.setDestinationCrs(crs)

            if self.zoom_easing is None:
                self.zoom_to_full_extent()

        hover_frames = int(self.hover_duration * self.frame_rate)
        for hover_frame in range(hover_frames):
            # Pad the numbers in the name so that they form a
            # 10 digit string with left padding of 0s

            file_name = self.working_directory / "{}-{}.png".format(
                self.frame_filename_prefix,
                str(self.current_frame).rjust(10, "0"),
            )
            self.verbose_message.emit(f"Dwell : {str(file_name)}")

            if file_name.exists() and self.reuse_cache:
                # User opted to re-used cached images to do nothing for now
                pass
            else:

                scope = QgsExpressionContextScope()
                scope.setVariable("from_feature", None, True)
                scope.setVariable("from_feature_id", None, True)
                scope.setVariable("to_feature", None, True)
                scope.setVariable("to_feature_id", None, True)

                scope.setVariable("hover_feature", feature, True)
                scope.setVariable("hover_feature_id", feature.id(), True)

                scope.setVariable(
                    "previous_feature",
                    previous_feature,
                    True,
                )
                scope.setVariable(
                    "previous_feature_id",
                    None if not previous_feature else previous_feature.id(),
                    True,
                )
                scope.setVariable(
                    "next_feature",
                    next_feature,
                    True,
                )
                scope.setVariable(
                    "next_feature_id",
                    None if not next_feature else next_feature.id(),
                    True,
                )

                scope.setVariable("current_hover_frame", hover_frame, True)
                scope.setVariable("current_travel_frame", None, True)

                scope.setVariable("hover_frames", hover_frames, True)
                scope.setVariable("travel_frames", None, True)

                scope.setVariable(
                    "current_animation_action", AnimationController.ACTION_HOVERING
                )

                job = self.create_job(self.map_settings, file_name.as_posix(), [scope])
                yield job

            self.current_frame += 1

    def fly_feature_to_feature(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self, start_feature: QgsFeature, end_feature: QgsFeature
    ) -> Iterator[RenderJob]:
        """
        Yields render jobs for an animation between two features
        """

        # In case we are iterating over lines or polygons, we
        # need to convert them to points first.
        start_point = self.geometry_to_pointxy(start_feature)
        end_point = self.geometry_to_pointxy(end_feature)
        if not start_point or not end_point:
            self.normal_message.emit("Unsupported geometry, skipping.")
            return

        delta_x = end_point.x() - start_point.x()
        delta_y = end_point.y() - start_point.y()

        travel_frames = int(self.travel_duration * self.frame_rate)
        flying_up = True
        for travel_frame in range(travel_frames):
            # will always be between 0 - 1
            progress_fraction = travel_frame / (travel_frames - 1)

            if self.pan_easing:
                # map progress through the easing curve
                progress_fraction = self.pan_easing.valueForProgress(progress_fraction)

            x = start_point.x() + delta_x * progress_fraction
            y = start_point.y() + delta_y * progress_fraction

            if self.map_mode == MapMode.PLANAR:
                center = QgsPointXY(x, y)
                center = self.layer_to_map_transform.transform(center)
                self.set_extent_center(center.x(), center.y())

            # zoom in and out to each feature if we are doing zoom easing
            if self.zoom_easing is not None:
                # Now use easings for zoom level too
                # first figure out if we are flying up or down
                if progress_fraction < 0.5:
                    # Flying up
                    # take progress from 0 -> 0.5 and scale to 0 -> 1
                    #  before apply easing
                    zoom_factor = self.zoom_easing.valueForProgress(
                        progress_fraction * 2
                    )
                    flying_up = True
                else:
                    # flying down
                    # take progress from 0.5 -> 1.0 and scale to 1 ->0
                    # before apply easing

                    if flying_up:
                        # update max scale at the halfway point
                        context = QgsExpressionContext(self.base_expression_context)
                        context.setFeature(end_feature)
                        context.appendScope(
                            QgsExpressionContextUtils.mapSettingsScope(
                                self.map_settings
                            )
                        )
                        scope = QgsExpressionContextScope()
                        scope.setVariable("from_feature", start_feature, True)
                        scope.setVariable("from_feature_id", start_feature.id(), True)
                        scope.setVariable("to_feature", end_feature, True)
                        scope.setVariable("to_feature_id", end_feature.id(), True)
                        scope.setVariable("hover_feature", end_feature, True)
                        scope.setVariable("hover_feature_id", end_feature.id(), True)
                        scope.setVariable("previous_feature", None, True)
                        scope.setVariable("previous_feature_id", None, True)
                        scope.setVariable("next_feature", None, True)
                        scope.setVariable("next_feature_id", None, True)
                        context.appendScope(scope)

                        self._evaluated_max_scale = self.max_scale
                        if self.data_defined_properties.hasActiveProperties():
                            (
                                self._evaluated_max_scale,
                                _,
                            ) = self.data_defined_properties.valueAsDouble(
                                AnimationController.PROPERTY_MAX_SCALE,
                                context,
                                self.max_scale,
                            )

                    flying_up = False

                    zoom_factor = self.zoom_easing.valueForProgress(
                        (1 - progress_fraction) * 2
                    )

                zoom_factor = self.zoom_easing.valueForProgress(zoom_factor)
                scale = (
                    self._evaluated_min_scale - self._evaluated_max_scale
                ) * zoom_factor + self._evaluated_max_scale
                self.set_to_scale(scale)

            # Change CRS if needed
            if self.map_mode == MapMode.SPHERE:
                definition = """ +proj=ortho \
                    +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 \
                    +ellps=sphere +units=m +no_defs""" % (
                    y,
                    x,
                )
                crs = QgsCoordinateReferenceSystem()
                crs.createFromProj(definition)
                self.map_settings.setDestinationCrs(crs)

                if self.zoom_easing is None:
                    self.zoom_to_full_extent()

            # Pad the numbers in the name so that they form a 10 digit
            # string with left padding of 0s

            file_name = self.working_directory / "{}-{}.png".format(
                self.frame_filename_prefix,
                str(self.current_frame).rjust(10, "0"),
            )
            self.verbose_message.emit(f"Fly : {str(file_name)}")

            if file_name.exists() and self.reuse_cache:
                # User opted to re-used cached images to do nothing for now
                pass
            else:
                scope = QgsExpressionContextScope()
                scope.setVariable("from_feature", start_feature, True)
                scope.setVariable("from_feature_id", start_feature.id(), True)
                scope.setVariable("to_feature", end_feature, True)
                scope.setVariable("to_feature_id", end_feature.id(), True)

                scope.setVariable("hover_feature", None, True)
                scope.setVariable("hover_feature_id", None, True)

                scope.setVariable("current_hover_frame", None, True)
                scope.setVariable("current_travel_frame", travel_frame, True)

                scope.setVariable("hover_frames", None, True)
                scope.setVariable("travel_frames", travel_frames, True)

                scope.setVariable(
                    "current_animation_action", AnimationController.ACTION_TRAVELLING
                )

                job = self.create_job(
                    self.map_settings,
                    file_name.as_posix(),
                    [scope],
                )
                yield job

            self.current_frame += 1

    def create_job(
        self,
        map_settings: QgsMapSettings,
        name: str,
        additional_expression_context_scopes: Optional[
            List[QgsExpressionContextScope]
        ] = None,
    ) -> RenderJob:
        """
        Creates a render job for the given map settings
        """

        settings = QgsMapSettings(map_settings)

        if Qgis.QGIS_VERSION_INT >= 32500:
            settings.setFrameRate(self.frame_rate)
            settings.setCurrentFrame(self.current_frame)

        context = QgsExpressionContext(self.base_expression_context)
        context.appendScope(QgsExpressionContextUtils.mapSettingsScope(settings))
        if additional_expression_context_scopes:
            for scope in additional_expression_context_scopes:
                context.appendScope(scope)

        task_scope = QgsExpressionContextScope()

        if Qgis.QGIS_VERSION_INT < 32500:
            # we only set these variables for older QGIS versions -- since 3.26 they will be automatically
            # set to match the QgsMapSettings currentFrame/frameRate value, which we set above
            task_scope.setVariable("frame_number", self.current_frame)
            task_scope.setVariable("frame_rate", self.frame_rate)

        task_scope.setVariable("total_frame_count", self.total_frame_count)

        context.appendScope(task_scope)
        settings.setExpressionContext(context)

        return RenderJob(name, settings)
