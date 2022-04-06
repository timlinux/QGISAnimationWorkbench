# coding=utf-8
"""This module has the main GUI interaction logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import os
import shutil
import tempfile
from enum import Enum
from typing import List, Optional

from qgis.PyQt.QtCore import pyqtSignal, QProcess
from qgis.core import QgsTask, QgsBlockingProcess, QgsFeedback

from .utilities import CoreUtils


class MovieFormat(Enum):
    """
    Movie formats
    """
    GIF = 0
    MP4 = 1


class MovieCreationTask(QgsTask):
    """
    A background task for exporting movies
    """
    FORMAT_GIF = "FORMAT_GIF"

    message = pyqtSignal(str)
    movie_created = pyqtSignal(str)

    def __init__(
            self,
            output_file: str,
            music_file: str,
            output_format: MovieFormat,
            work_directory: str,
            frame_filename_prefix: str,
            framerate: int,
    ):
        super().__init__("Exporting Movie", QgsTask.Flag.CanCancel)

        self.output_file = output_file
        self.music_file = music_file
        self.format = output_format
        self.work_directory = work_directory
        self.frame_filename_prefix = frame_filename_prefix
        self.framerate = framerate

        self.feedback: Optional[QgsFeedback] = None

    def run_process(self, command: str, arguments: List[str]):
        """
        Runs a process in a blocking way, reporting the stdout output to the user
        """
        self.message.emit(
            "Generating Movie: {} {}".format(command, " ".join(arguments))
        )

        def on_stdout(ba):
            val = ba.data().decode("UTF-8")

            on_stdout.buffer += val
            if on_stdout.buffer.endswith("\n") or on_stdout.buffer.endswith(
                    "\r"
            ):
                # flush buffer
                self.message.emit(on_stdout.buffer.rstrip())
                on_stdout.buffer = ""

        on_stdout.progress = 0
        on_stdout.buffer = ""

        def on_stderr(ba):
            val = ba.data().decode("UTF-8")
            on_stderr.buffer += val

            if on_stderr.buffer.endswith("\n") or on_stderr.buffer.endswith(
                    "\r"
            ):
                # flush buffer
                self.message.emit(on_stderr.buffer.rstrip())
                on_stderr.buffer = ""

        on_stderr.buffer = ""

        proc = QgsBlockingProcess(command, arguments)
        proc.setStdOutHandler(on_stdout)
        proc.setStdErrHandler(on_stderr)

        res = proc.run(self.feedback)
        if self.feedback.isCanceled() and res != 0:
            self.message.emit("Process was canceled and did not complete")
        elif (
                not self.feedback.isCanceled() and proc.exitStatus() == QProcess.CrashExit
        ):
            self.message.emit("Process was unexpectedly terminated")
        elif res == 0:
            self.message.emit("Process completed successfully")
        elif proc.processError() == QProcess.FailedToStart:
            self.message.emit(
                f"Process {command} failed to start. Either {command} is missing, or you may have insufficient permissions to run the program."
            )
        else:
            self.message.emit("Process returned error code {}".format(res))

    def run(self):
        """
        Creates a movie in a background task
        """

        self.feedback = QgsFeedback()

        if self.format == MovieFormat.GIF:
            self.message.emit("Generating GIF")

            convert = CoreUtils.which("convert")[0]
            self.message.emit(f"convert found: {convert}")

            # Now generate the GIF. If this fails try to run the call from
            # the command line and check the path to convert (provided by
            # ImageMagick) is correct...
            # delay of 3.33 makes the output around 30fps

            self.run_process(
                convert,
                [
                    "-delay",
                    str(100 / self.framerate),
                    "-loop",
                    "0",
                    f"{self.work_directory}/{self.frame_filename_prefix}-*.png",
                    self.output_file,
                ],
            )

            # Now do a second pass with image magick to resize and compress the
            # gif as much as possible.  The remap option basically takes the
            # first image as a reference image for the colour palette Depending
            # on you cartography you may also want to bump up the colors param
            # to increase palette size and of course adjust the scale factor to
            # the ultimate image size you want
            self.run_process(
                convert,
                [
                    self.output_file,
                    "-coalesce",
                    "-scale",
                    "600x600",
                    "-fuzz",
                    "2%",
                    "+dither",
                    "-remap",
                    f"{self.output_file}[20]",
                    "+dither",
                    "-colors",
                    "14",
                    "-layers",
                    "Optimize",
                    f"{self.work_directory}/animation_small.gif",
                ],
            )

            self.message.emit(f"GIF written to {self.output_file}")
            self.movie_created.emit(self.output_file)
        else:
            self.message.emit("Generating MP4 Movie")
            ffmpeg = CoreUtils.which("ffmpeg")[0]
            # Also, we will make a video of the scene - useful for cases where
            # you have a larger colour palette and gif will not hack it.
            # The Pad option is to deal with cases where ffmpeg complains
            # because the h or w of the image is an odd number of pixels.
            # color=white pads the video with white pixels.
            # Change to black if needed.
            # -y to force overwrite exising file
            self.message.emit(f"ffmpeg found: {ffmpeg}")

            arguments = [
                "-y",
                "-framerate",
                str(self.framerate),
                "-pattern_type",
                "glob",
                "-i",
                f"{self.work_directory}/{self.frame_filename_prefix}-*.png",
                "-vf",
                "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
            ]

            # This will create a temporary working dir & filename
            # that is secure and clean up after itself.
            with tempfile.TemporaryDirectory() as tmp:
                temp_video_path = str(
                    os.path.join(tmp, "animation_workbench.mp4")
                )
                arguments.append(temp_video_path)
                # This will build the base vide with no soundtrack
                # in the above temporary folder
                self.run_process(ffmpeg, arguments)
                # windows_command = ("""
                #    %s -y -framerate %s -pattern_type sequence \
                #    -start_number 0000000001 \
                #    -i "%s/%s-%00000000010d.png" -vf \
                #    "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white" \
                #    -c:v libx264 -pix_fmt yuv420p %s""" % (
                #    ffmpeg,
                #    framerate,
                #    self.work_directory,
                #    self.frame_filename_prefix,
                #    self.output_file))

                # If there is a music file, we do a second pass and add the
                # file into the video container. From my testing on the CLI,
                # this works more smoothly and doesn't have issues like
                # video blanking that doing it in one pass does.

                if self.music_file:
                    self.message.emit("Adding sound track to video container")

                    arguments = [
                        "-y",
                        "-i",
                        f"{temp_video_path}",
                        "-i",
                        f"{self.music_file}",
                        "-c",
                        # Will copy the sound into the video container
                        "copy",
                        # will truncate output to shortest between vid and audio
                        "-shortest",
                        f"{self.output_file}",
                    ]

                    self.run_process(ffmpeg, arguments)
                    self.message.emit(
                        f"MP4 with soundtrack written to {self.output_file}"
                    )
                else:
                    shutil.copyfile(temp_video_path, self.output_file)
                    self.message.emit(
                        f"MP4 without soundtrack written to {self.output_file}"
                    )

        self.movie_created.emit(self.output_file)
        self.feedback = None
        return True

    def cancel(self):  # pylint: disable=missing-function-docstring
        if self.feedback is not None:
            self.feedback.cancel()

        super().cancel()
