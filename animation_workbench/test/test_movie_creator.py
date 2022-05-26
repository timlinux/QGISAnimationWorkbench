# coding=utf-8
"""Movie creator test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "(C) 2018 by Nyall Dawson"
__date__ = "20/04/2018"
__copyright__ = "Copyright 2018, North Road"
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

import unittest

from animation_workbench.core import MovieCommandGenerator, MovieFormat
from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class MovieCreatorTest(unittest.TestCase):
    """Test MovieCommandGenerator works."""

    # pylint: disable=too-many-statements

    def test_mp4(self):
        """
        Test mp4 command generation
        """
        generator = MovieCommandGenerator(
            output_file="/home/me/videos/test.mp4",
            intro_command=None,
            outro_command=None,
            music_command=None,
            output_format=MovieFormat.MP4,
            work_directory="/tmp/movies",
            frame_filename_prefix="frames",
            framerate=90,
            temp_dir="/tmp",
        )

        commands = generator.as_commands()
        self.assertEqual(
            commands,
            [
                (
                    "/usr/bin/ffmpeg",
                    [
                        "-hide_banner",
                        "-y",
                        "-framerate",
                        "90",
                        "-i",
                        "/tmp/movies/frames-%010d.png",
                        "-vf",
                        "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white",
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "/home/me/videos/test.mp4",
                    ],
                )
            ],
        )

    def test_mp4_with_music(self):
        """
        Test mp4 command generation
        """
        self.maxDiff = None
        generator = MovieCommandGenerator(
            output_file="/home/me/videos/test.mp4",
            intro_command=None,
            outro_command=None,
            music_command=None,
            output_format=MovieFormat.MP4,
            work_directory="/tmp/movies",
            frame_filename_prefix="frames",
            framerate=90,
            temp_dir="/tmp",
        )

        commands = generator.as_commands()
        self.assertEqual(
            commands,
            [
                (
                    "/usr/bin/ffmpeg",
                    [
                        "-hide_banner",
                        "-y",
                        "-framerate",
                        "90",
                        "-i",
                        "/tmp/movies/frames-%010d.png",
                        "-vf",
                        "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white",
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "/tmp/main.mp4",
                    ],
                ),
                (
                    "/usr/bin/ffmpeg",
                    [
                        "-y",
                        "-i",
                        "/tmp/animation_workbench.mp4",
                        "-i",
                        "/home/me/music/lalala.mp3",
                        "-c",
                        "copy",
                        "-shortest",
                        "/home/me/videos/test.mp4",
                    ],
                ),
            ],
        )

    def test_gif(self):
        """
        Test gif command generation
        """
        generator = MovieCommandGenerator(
            output_file="/home/me/videos/test.gif",
            intro_command=None,
            outro_command=None,
            music_command=None,
            output_format=MovieFormat.GIF,
            work_directory="/tmp/movies",
            frame_filename_prefix="frames",
            framerate=90,
            temp_dir="/tmp/",
        )

        commands = generator.as_commands()
        self.assertEqual(
            commands,
            [
                (
                    "/usr/bin/convert",
                    [
                        "-delay",
                        "1.1111111111111112",
                        "-loop",
                        "0",
                        "/tmp/movies/frames-*.png",
                        "/home/me/videos/test.gif",
                    ],
                ),
                (
                    "/usr/bin/convert",
                    [
                        "/home/me/videos/test.gif",
                        "-coalesce",
                        "-scale",
                        "600x600",
                        "-fuzz",
                        "2%",
                        "+dither",
                        "-remap",
                        "/home/me/videos/test.gif[20]",
                        "+dither",
                        "-colors",
                        "14",
                        "-layers",
                        "Optimize",
                        "/tmp/movies/animation_small.gif",
                    ],
                ),
            ],
        )


if __name__ == "__main__":
    suite = unittest.makeSuite(MovieCreatorTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
