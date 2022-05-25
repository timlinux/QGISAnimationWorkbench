# coding=utf-8
"""This module has the main GUI interaction logic for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import os
import tempfile
from enum import Enum
from typing import List, Optional, Tuple

from qgis.PyQt.QtCore import pyqtSignal, QProcess
from qgis.core import QgsTask, QgsBlockingProcess, QgsFeedback

from .utilities import CoreUtils


class MovieFormat(Enum):
    """
    Movie formats
    """

    GIF = 0
    MP4 = 1


class MovieCommandGenerator:
    """
    Generates the command line strings for movie creation
    """

    def __init__(
        self,
        output_file: str,
        intro_command: Optional[tuple],
        outro_command: Optional[tuple],
        music_command: Optional[tuple],
        output_format: MovieFormat,
        work_directory: str,
        frame_filename_prefix: str,
        framerate: int,
        temp_dir: str,
    ):
        self.output_file = output_file
        self.intro_command = intro_command
        self.outro_command = outro_command
        self.music_command = music_command
        self.format = output_format
        self.work_directory = work_directory
        self.frame_filename_prefix = frame_filename_prefix
        self.framerate = framerate
        self.temp_dir = temp_dir

    def as_commands(self) -> List[Tuple[str, List]]:  # pylint: disable= R0915
        """
        Returns a list of commands necessary for the movie generation.

        :returns tuple: Returned as tuples of the command and arguments list.
        """
        results = []
        if self.format == MovieFormat.GIF:
            convert = CoreUtils.which("convert")[0]

            # First generate the GIF. If this fails try to run the call from
            # the command line and check the path to convert (provided by
            # ImageMagick) is correct...
            # delay of 3.33 makes the output around 30fps

            results.append(
                (
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
            )

            # Now do a second pass with image magick to resize and compress the
            # gif as much as possible.  The remap option basically takes the
            # first image as a reference image for the colour palette Depending
            # on you cartography you may also want to bump up the colors param
            # to increase palette size and of course adjust the scale factor to
            # the ultimate image size you want
            results.append(
                (
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
            )
        else:
            ffmpeg = CoreUtils.which("ffmpeg")[0]
            # Also, we will make a video of the scene - useful for cases where
            # you have a larger colour palette and gif will not hack it.
            # The Pad option is to deal with cases where ffmpeg complains
            # because the h or w of the image is an odd number of pixels.
            # color=white pads the video with white pixels.
            # Change to black if needed.
            # -y to force overwrite exising file

            # Generate the intro video, if any
            intro_file = None
            outro_file = None
            music_file = None
            if self.intro_command:
                intro_file = str(os.path.join(self.temp_dir, "intro.mp4"))
                self.intro_command.append(intro_file)
                results.append((ffmpeg, self.intro_command))
            # Generate the outro video, if any
            if self.outro_command:
                outro_file = str(os.path.join(self.temp_dir, "outro.mp4"))
                self.outro_command.append(outro_file)
                results.append((ffmpeg, self.outro_command))
            # Generate the sound track, if any
            if self.music_command:
                music_file = str(os.path.join(self.temp_dir, "music.mp4"))
                self.music_command.append(music_file)
                results.append((ffmpeg, self.music_command))

            arguments = [
                "-hide_banner",
                "-y",
                "-framerate",
                str(self.framerate),
                "-i",
                # Assumes numbers of files are 10 digits
                f"{self.work_directory}/{self.frame_filename_prefix}-%010d.png",
                "-vf",
                "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
            ]

            main_file = str(os.path.join(self.temp_dir, "main.mp4"))
            arguments.append(main_file)
            # This will build the base video with no soundtrack
            # in the above temporary folder
            results.append((ffmpeg, arguments))

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

            # Second pass - now we add the intro and outro videos to the main
            # video if they exist. See https://trac.ffmpeg.org/wiki/Concatenate
            combined_file = None

            if music_file:
                # Write to a temporary file that we will add music to after
                combined_file = str(os.path.join(self.temp_dir, "combined.mp4"))
            else:
                # Write to the final output file
                combined_file = self.output_file

            file_list_text = ""
            if intro_file:
                file_list_text += f"file {intro_file}\n"
            file_list_text += f"file {main_file}\n"
            if outro_file:
                file_list_text += f"file {outro_file}\n"

            file_list_path = str(os.path.join(self.temp_dir, "list.txt"))
            with open(file_list_path, "w", encoding="utf-8") as file_list_file:
                file_list_file.write(file_list_text)

            arguments = [
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                file_list_path,
                "-c",
                "copy",
                "-vf",
                "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white,scale=1920:1080,setsar=1:1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                # "-vf",
                # "scale=1920:1080",  # output resolution
                combined_file,
            ]

            # This will build the base video with no soundtrack
            # in the above temporary folder
            results.append((ffmpeg, arguments))

            # Third pass - now we add the soundtrack to the main video if it exists

            # If there is a music file, we add the
            # file into the video container. From my testing on the CLI,
            # this works more smoothly and doesn't have issues like
            # video blanking that doing it in the first pass does.
            if music_file:
                arguments.append("-i")
                arguments.append(music_file)
                arguments.append("-c")
                # Will copy the sound into the video container
                arguments.append("copy")
                # will truncate output to shortest between vid and audio
                arguments.append(
                    "-shortest",
                )
                arguments.append("-i")
                arguments.append(combined_file)
                arguments.append(self.output_file)

                results.append((ffmpeg, arguments))

        return results


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
        intro_command: str,
        outro_command: str,
        music_command: str,
        output_format: MovieFormat,
        work_directory: str,
        frame_filename_prefix: str,
        framerate: int,
    ):
        super().__init__("Exporting Movie", QgsTask.Flag.CanCancel)

        self.output_file = output_file
        self.intro_command = intro_command
        self.outro_command = outro_command
        self.music_command = music_command
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
            if on_stdout.buffer.endswith("\n") or on_stdout.buffer.endswith("\r"):
                # flush buffer
                self.message.emit(on_stdout.buffer.rstrip())
                on_stdout.buffer = ""

        on_stdout.progress = 0
        on_stdout.buffer = ""

        def on_stderr(ba):
            val = ba.data().decode("UTF-8")
            on_stderr.buffer += val

            if on_stderr.buffer.endswith("\n") or on_stderr.buffer.endswith("\r"):
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
        elif not self.feedback.isCanceled() and proc.exitStatus() == QProcess.CrashExit:
            self.message.emit("Process was unexpectedly terminated")
        elif res == 0:
            self.message.emit("Process completed successfully")
        elif proc.processError() == QProcess.FailedToStart:
            self.message.emit(
                f"Process {command} failed to start. Either {command} "
                "is missing, or you may have insufficient permissions to "
                "run the program."
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
        else:
            self.message.emit("Generating MP4 Movie")
            ffmpeg = CoreUtils.which("ffmpeg")[0]
            self.message.emit(f"ffmpeg found: {ffmpeg}")

        # This will create a temporary working dir & filename
        # that is secure and clean up after itself.
        with tempfile.TemporaryDirectory() as tmp:
            generator = MovieCommandGenerator(
                output_file=self.output_file,
                intro_command=self.intro_command,
                outro_command=self.outro_command,
                music_command=self.music_command,
                output_format=self.format,
                work_directory=self.work_directory,
                frame_filename_prefix=self.frame_filename_prefix,
                framerate=self.framerate,
                temp_dir=tmp,
            )

            for command, arguments in generator.as_commands():
                self.run_process(command, arguments)

        self.movie_created.emit(self.output_file)
        self.feedback = None
        return True

    def cancel(self):  # pylint: disable=missing-function-docstring
        if self.feedback is not None:
            self.feedback.cancel()

        super().cancel()
