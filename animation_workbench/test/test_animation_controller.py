# coding=utf-8
"""GUI Utils Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = '(C) 2018 by Nyall Dawson'
__date__ = '20/04/2018'
__copyright__ = 'Copyright 2018, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import unittest
from qgis.core import (
    QgsMapSettings,
    QgsReferencedRectangle
)

from animation_workbench.core import AnimationController
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class AnimationControllerTest(unittest.TestCase):
    """Test AnimationController works."""

    def test_fixed_extent(self):
        """
        Test a fixed extent job
        """
        map_settings = QgsMapSettings()
        extent = QgsReferencedRectangle(map_settings.extent(), map_settings.destinationCrs())
        controller = AnimationController.create_fixed_extent_controller(map_settings=map_settings,
                                                                        feature_layer=None,
                                                                        output_extent=extent,
                                                                        total_frames=5,
                                                                        frame_rate=10)

        it = controller.create_jobs()
        # should be 5 frames
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 0)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 1)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 2)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 3)
        job = next(it)
        self.assertEqual(job.map_settings.extent(), map_settings.extent())
        self.assertEqual(job.map_settings.frameRate(), 10)
        self.assertEqual(job.map_settings.currentFrame(), 4)
        with self.assertRaises(StopIteration):
            next(it)





if __name__ == "__main__":
    suite = unittest.makeSuite(AnimationControllerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
