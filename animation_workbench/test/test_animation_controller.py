# coding=utf-8
"""GUI Utils Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# pylint: disable=too-many-lines

__author__ = "(C) 2018 by Nyall Dawson"
__date__ = "20/04/2018"
__copyright__ = "Copyright 2018, North Road"
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

import unittest

from qgis.PyQt.QtCore import QSize, QEasingCurve
from qgis.core import (
    QgsMapSettings,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsReferencedRectangle,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)

from animation_workbench.core import AnimationController, MapMode
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class AnimationControllerTest(unittest.TestCase):
    """Test AnimationController works."""

    # pylint: disable=too-many-statements

    def test_fixed_extent(self):
        """
        Test a fixed extent job
        """
        map_settings = QgsMapSettings()
        map_settings.setExtent(QgsRectangle(1, 2, 3, 4))
        map_settings.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        map_settings.setOutputSize(QSize(400, 300))
        extent = QgsReferencedRectangle(
            map_settings.extent(), map_settings.destinationCrs()
        )
        controller = AnimationController.create_fixed_extent_controller(
            map_settings=map_settings,
            feature_layer=None,
            output_extent=extent,
            total_frames=5,
            frame_rate=10,
        )

        it = controller.create_jobs()
        # should be 5 frames
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 0)
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 0
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 5
        )
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 1)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 5
        )
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 2)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=1200003,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 5
        )
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 3)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 3
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 5
        )
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 4)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 4
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 5
        )

        with self.assertRaises(StopIteration):
            next(it)

    def test_fixed_extent_with_layer(self):
        """
        Test a fixed extent job with a layer
        """

        vl = QgsVectorLayer("Point?crs=EPSG:4326&field=name:string", "vl", "memory")
        self.assertTrue(vl.isValid())

        f = QgsFeature(vl.fields())
        f["name"] = "f1"
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 2)))
        self.assertTrue(vl.dataProvider().addFeature(f))

        f["name"] = "f2"
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 20)))
        self.assertTrue(vl.dataProvider().addFeature(f))

        map_settings = QgsMapSettings()
        map_settings.setExtent(QgsRectangle(1, 2, 3, 4))
        map_settings.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        map_settings.setOutputSize(QSize(400, 300))
        extent = QgsReferencedRectangle(
            map_settings.extent(), map_settings.destinationCrs()
        )
        controller = AnimationController.create_fixed_extent_controller(
            map_settings=map_settings,
            feature_layer=vl,
            output_extent=extent,
            total_frames=2,
            frame_rate=10,
        )

        it = controller.create_jobs()
        # should be 4 frames
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 0)
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 0
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            0,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(),
            1,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"),
            1,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 1)
        # self.assertEqual(job.map_settings.expressionContext().variable('total_frame_count'), 4)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 1)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            1,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(),
            1,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"),
            1,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 1)
        # self.assertEqual(job.map_settings.expressionContext().variable('total_frame_count'), 4)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 2)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            0,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature_id"), 1
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        # self.assertEqual(job.map_settings.expressionContext().variable('total_frame_count'), 4)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertAlmostEqual(job.map_settings.scale(), 748220, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 3)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            748220,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 3
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_rate"), 10
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            1,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature_id"), 1
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        # self.assertEqual(job.map_settings.expressionContext().variable('total_frame_count'), 4)

        with self.assertRaises(StopIteration):
            next(it)

    def test_planar(self):
        """
        Test a planar job
        """

        vl = QgsVectorLayer("Point?crs=EPSG:4326&field=name:string", "vl", "memory")
        self.assertTrue(vl.isValid())

        f = QgsFeature(vl.fields())
        f["name"] = "f1"
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 2)))
        self.assertTrue(vl.dataProvider().addFeature(f))

        f["name"] = "f2"
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 20)))
        self.assertTrue(vl.dataProvider().addFeature(f))

        map_settings = QgsMapSettings()
        map_settings.setExtent(QgsRectangle(1, 2, 3, 4))
        map_settings.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        map_settings.setOutputSize(QSize(400, 300))
        controller = AnimationController.create_moving_extent_controller(
            map_settings=map_settings,
            mode=MapMode.PLANAR,
            feature_layer=vl,
            travel_duration=2,
            hover_duration=1,
            min_scale=2000000,
            max_scale=1000000,
            pan_easing=QEasingCurve(QEasingCurve.Type.Linear),
            zoom_easing=QEasingCurve(QEasingCurve.Type.Linear),
            frame_rate=2,
        )

        it = controller.create_jobs()

        job = next(it)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 0)
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            266666,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 0
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"), 1
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature_id"), 2
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("from_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("from_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("to_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("to_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            0,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_travel_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("travel_frames")
        )

        self.assertEqual(job.map_settings.expressionContext().feature().id(), 1)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )
        job = next(it)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        # Changed from 44
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 1)
        # Changed from 44
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            266666,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 1
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"), 1
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature_id"), 2
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("from_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("from_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("to_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("to_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            1,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_travel_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("travel_frames")
        )

        self.assertEqual(job.map_settings.expressionContext().feature().id(), 1)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )

        # now we start panning
        job = next(it)
        # Changed from 44
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 2)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            266666,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 2
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 2
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 0
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 444444, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 4, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 8, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 3)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            444444,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 3
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 2
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 1
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        job = next(it)
        # was 16666
        self.assertAlmostEqual(job.map_settings.scale(), 444444, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 7, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 14, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 4)
        # Was 1666666
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            444444,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 2
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 2
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 1000000, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 5)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1000000,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 5
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("previous_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 2
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 3
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        # back to hovering

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 1000000, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 6)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1000000,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 6
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature_id"), 1
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("from_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("from_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("to_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("to_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            0,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_travel_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("travel_frames")
        )

        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 1000000, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 7)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1000000,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 7
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature_id"), 1
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("next_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("next_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("from_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("from_feature_id")
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("to_feature"))
        self.assertIsNone(
            job.map_settings.expressionContext().variable("to_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_hover_frame"),
            1,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_travel_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_frames"),
            2,
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("travel_frames")
        )

        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 8
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Hovering",
        )

        with self.assertRaises(StopIteration):
            next(it)

    def test_planar_loop(self):
        """
        Test a planar job with looping
        """

        vl = QgsVectorLayer("Point?crs=EPSG:4326&field=name:string", "vl", "memory")
        self.assertTrue(vl.isValid())

        f = QgsFeature(vl.fields())
        f["name"] = "f1"
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(1, 2)))
        self.assertTrue(vl.dataProvider().addFeature(f))

        f["name"] = "f2"
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 20)))
        self.assertTrue(vl.dataProvider().addFeature(f))

        map_settings = QgsMapSettings()
        map_settings.setExtent(QgsRectangle(1, 2, 3, 4))
        map_settings.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        map_settings.setOutputSize(QSize(400, 300))
        controller = AnimationController.create_moving_extent_controller(
            map_settings=map_settings,
            mode=MapMode.PLANAR,
            feature_layer=vl,
            travel_duration=2,
            hover_duration=1,
            min_scale=2000000,
            max_scale=1000000,
            pan_easing=QEasingCurve(QEasingCurve.Type.Linear),
            zoom_easing=QEasingCurve(QEasingCurve.Type.Linear),
            frame_rate=2,
            loop=True,
        )

        it = controller.create_jobs()

        job = next(it)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 0)
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            266666,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("hover_feature_id"), 1
        )
        # make sure previous_feature is set to wrap around back to start
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature_id"), 2
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 1)

        # now we start panning
        job = next(it)
        # Changed from 44
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 2)

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 444444, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 4, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 8, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 3)

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 444444, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 7, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 14, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 4)

        job = next(it)
        # Changed from 44
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 5)

        # back to hovering

        job = next(it)
        # Changed from 44
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 6)

        job = next(it)
        # Was 44444
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 7)

        # make sure next_feature is set to wrap around back to start
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("previous_feature_id"), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("next_feature_id"), 1
        )

        # travel from last to first
        job = next(it)
        # was 4444444
        self.assertAlmostEqual(job.map_settings.scale(), 266666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 10, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 20, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 8)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1000000,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 8
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 1
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 0
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 12
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 1666666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 7, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 14, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 9)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1666666,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 9
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 1
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 1
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 12
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 1666666, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 4, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 8, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 10)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1666666,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 10
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 1
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 2
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 12
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        job = next(it)
        self.assertAlmostEqual(job.map_settings.scale(), 1000000, delta=120000)
        self.assertAlmostEqual(job.map_settings.extent().center().x(), 1, 2)
        self.assertAlmostEqual(job.map_settings.extent().center().y(), 2, 2)
        self.assertEqual(job.map_settings.frameRate(), 2)
        self.assertEqual(job.map_settings.currentFrame(), 11)
        self.assertAlmostEqual(
            job.map_settings.expressionContext().variable("map_scale"),
            1000000,
            delta=120000,
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("frame_number"), 11
        )
        self.assertEqual(job.map_settings.expressionContext().variable("frame_rate"), 2)
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature")
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("hover_feature_id")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature").id(), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("from_feature_id"), 2
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature").id(), 1
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("to_feature_id"), 1
        )
        self.assertIsNone(
            job.map_settings.expressionContext().variable("current_hover_frame")
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_travel_frame"), 3
        )
        self.assertIsNone(job.map_settings.expressionContext().variable("hover_frames"))
        self.assertEqual(
            job.map_settings.expressionContext().variable("travel_frames"), 4
        )
        self.assertEqual(job.map_settings.expressionContext().feature().id(), 2)
        self.assertEqual(
            job.map_settings.expressionContext().variable("total_frame_count"), 12
        )
        self.assertEqual(
            job.map_settings.expressionContext().variable("current_animation_action"),
            "Travelling",
        )

        with self.assertRaises(StopIteration):
            next(it)


if __name__ == "__main__":
    suite = unittest.makeSuite(AnimationControllerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
