# coding=utf-8
"""This module has the main core animation logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Iterator

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA
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
)

from .render_queue import RenderJob


class MapMode(Enum):
    SPHERE = 1  # CRS will be manipulated to create a spinning globe effect
    PLANAR = 2  # CRS will not be altered, extents will as we pan and zoom
    FIXED_EXTENT = 3  # EASING and ZOOM disabled, extent stays in place


class InvalidAnimationParametersException(Exception):
    """
    Raised when animation parameters are not valid
    """


class AnimationController(QObject):
    normal_message = pyqtSignal(str)
    verbose_message = pyqtSignal(str)

    @staticmethod
    def create_fixed_extent_controller(
        map_settings: QgsMapSettings,
        output_extent: QgsReferencedRectangle,
        total_frames: int,
    ) -> "AnimationController":
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
        controller.total_frame_count = total_frames

        return controller

    @staticmethod
    def create_moving_extent_controller(
        map_settings: QgsMapSettings,
        mode: MapMode,
        feature_layer: QgsVectorLayer,
        travel_frames: int,
        dwell_frames: int,
        min_scale: float,
        max_scale: float,
        pan_easing: Optional[QEasingCurve],
        zoom_easing: Optional[QEasingCurve],
    ) -> "AnimationController":

        if not feature_layer:
            raise InvalidAnimationParametersException("No animation layer set")

        controller = AnimationController(mode, map_settings)
        controller.feature_layer = feature_layer
        controller.total_feature_count = feature_layer.featureCount()

        # Subtract one because we already start at the first feature
        controller.total_frame_count = (controller.total_feature_count - 1) * (
            dwell_frames + travel_frames
        )
        controller.dwell_frames = dwell_frames
        controller.travel_frames = travel_frames

        controller.min_scale = min_scale
        controller.max_scale = max_scale

        controller.pan_easing = pan_easing
        controller.zoom_easing = zoom_easing

        return controller

    def __init__(self, map_mode: MapMode, map_settings: QgsMapSettings):
        super().__init__()
        self.map_settings: QgsMapSettings = map_settings
        self.map_mode: MapMode = map_mode

        self.feature_layer: Optional[QgsVectorLayer] = None
        self.layer_to_map_transform: Optional[QgsCoordinateTransform] = None
        self.total_feature_count: int = 0

        self.total_frame_count: int = 0
        self.dwell_frames: int = 0
        self.travel_frames: int = 0

        self.max_scale: float = 0
        self.min_scale: float = 0

        self.pan_easing: Optional[QEasingCurve] = None
        self.zoom_easing: Optional[QEasingCurve] = None

        self.current_frame = 0

        self.working_directory: Path = Path(tempfile.gettempdir())
        self.frame_filename_prefix: str = "animation_workbench"

        self.previous_feature: Optional[QgsFeature] = None

        self.reuse_cache: bool = False

    def create_job_for_frame(self, frame: int) -> Optional[RenderJob]:
        """
        Creates a render job corresponding to a specific frame
        """
        job = None
        # inefficient, but we can rework later if needed!
        jobs = self.create_jobs()
        for _ in range(frame + 1):
            job = next(jobs)
        return job

    def create_jobs(self) -> Iterator[RenderJob]:
        if self.map_mode == MapMode.FIXED_EXTENT:
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
        for self.current_frame in range(self.total_frame_count):
            name = self.working_directory / "{}-{}.png".format(
                self.frame_filename_prefix,
                str(self.current_frame).rjust(10, "0"),
            )

            job = self.create_job(
                self.map_settings,
                name.as_posix(),
                None,
                self.current_frame,
                "Fixed Extent",
            )
            yield job

    def create_moving_extent_job(self) -> Iterator[RenderJob]:
        self.set_to_scale(self.min_scale)
        for feature in self.feature_layer.getFeatures():
            if self.previous_feature is not None:
                for job in self.fly_feature_to_feature(
                    self.previous_feature, feature
                ):
                    yield job

            self.previous_feature = feature
            for job in self.dwell_at_feature(feature):
                yield job

    def set_extent_center(self, center_x: float, center_y: float):
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
        scale_factor = scale / self.map_settings.scale()
        r = self.map_settings.extent()
        r.scale(scale_factor)
        self.map_settings.setExtent(r)

    def zoom_to_full_extent(self):
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

    def dwell_at_feature(self, feature) -> Iterator[RenderJob]:
        """
        Wait at a feature to emphasise it in the video.

        :param feature: QgsFeature to dwell at.
        :type feature: QgsFeature
        """
        center = self.geometry_to_pointxy(feature)
        if not center:
            self.normal_message.emit("Unsupported geometry, skipping.")
            return

        center = self.layer_to_map_transform.transform(center)
        self.set_extent_center(center.x(), center.y())
        self.set_to_scale(self.max_scale)
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

        for dwell_frame in range(0, self.dwell_frames, 1):
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
                job = self.create_job(
                    self.map_settings,
                    file_name.as_posix(),
                    feature.id(),
                    dwell_frame,
                    "Hovering",
                )
                yield job

            self.current_frame += 1

    def fly_feature_to_feature(
        self, start_feature: QgsFeature, end_feature: QgsFeature
    ) -> Iterator[RenderJob]:
        # In case we are iterating over lines or polygons, we
        # need to convert them to points first.
        start_point = self.geometry_to_pointxy(start_feature)
        end_point = self.geometry_to_pointxy(end_feature)
        if not start_point or not end_point:
            self.normal_message.emit("Unsupported geometry, skipping.")
            return

        delta_x = end_point.x() - start_point.x()
        delta_y = end_point.y() - start_point.y()

        for travel_frame in range(self.travel_frames):
            # will always be between 0 - 1
            progress_fraction = travel_frame / (self.travel_frames - 1)

            if self.pan_easing:
                # map progress through the easing curve
                progress_fraction = self.pan_easing.valueForProgress(
                    progress_fraction
                )

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
                else:
                    # flying down
                    # take progress from 0.5 -> 1.0 and scale to 1 ->0
                    # before apply easing
                    zoom_factor = self.zoom_easing.valueForProgress(
                        (1 - progress_fraction) * 2
                    )

                zoom_factor = self.zoom_easing.valueForProgress(zoom_factor)
                scale = (
                    self.min_scale - self.max_scale
                ) * zoom_factor + self.max_scale
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
                job = self.create_job(
                    self.map_settings,
                    file_name.as_posix(),
                    end_feature.id(),
                    travel_frame,
                    "Panning",
                )
                yield job

            self.current_frame += 1

    def create_job(
        self,
        map_settings: QgsMapSettings,
        name: str,
        current_feature_id: Optional[int],
        current_frame_for_feature: Optional[int] = None,
        action: str = "None",
    ):

        settings = QgsMapSettings(map_settings)
        # The next part sets project variables that you can use in your
        # cartography etc. to see the progress. Here is an example
        # of a QGS expression you can use in the map decoration copyright
        # widget to show current script progress
        # [%'Frame ' || to_string(coalesce(@current_frame, 0)) || '/' ||
        # to_string(coalesce(@frames_per_feature, 0)) || ' for feature ' ||
        # to_string(coalesce(@current_feature_id,0)) ||
        # ' with map mode: ' || @current_animation_action %]
        task_scope = QgsExpressionContextScope()
        task_scope.setVariable("current_feature_id", current_feature_id)
        task_scope.setVariable("frames_per_feature", self.travel_frames)
        task_scope.setVariable(
            "current_frame_for_feature", current_frame_for_feature
        )
        task_scope.setVariable("dwell_frames_per_feature", self.dwell_frames)
        task_scope.setVariable("current_animation_action", action)
        task_scope.setVariable("current_frame", self.current_frame)
        task_scope.setVariable("total_frame_count", self.total_frame_count)

        context = settings.expressionContext()
        context.appendScope(task_scope)
        settings.setExpressionContext(context)

        return RenderJob(name, settings)
