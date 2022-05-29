# coding=utf-8
"""Widget for managing a list of media in the AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import json
import os
from os.path import expanduser
from qgis.PyQt.QtWidgets import QWidget, QSizePolicy
from qgis.PyQt.QtCore import Qt

# from typing import Optional

# from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
# from PyQt5.QtMultimediaWidgets import QVideoWidget
# from qgis.PyQt.QtCore import pyqtSlot, QUrl
from qgis.PyQt.QtGui import QPixmap, QImage
from qgis.PyQt.QtWidgets import QFileDialog, QListWidgetItem
from .utilities import get_ui_class
from .core import (
    set_setting,
    setting,
)

FORM_CLASS = get_ui_class("media_list_widget_base.ui")


class MediaListWidget(QWidget, FORM_CLASS):
    """
    A widget for managing a list of media.
    """

    def __init__(self, parent=None):
        """Constructor for media_list_widget.

        :param parent: Parent widget of this widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # media_type:
        # Types of media that can be managed. Valid options are
        # "images", "images and movies", "movies", "sound".
        self.media_type = None
        self.media_filter = None
        self.output_mode = None
        self.media_list.currentRowChanged.connect(self.media_item_selected)
        self.add_media.clicked.connect(self.choose_media_file)
        self.remove_media.clicked.connect(self.remove_media_file)
        self.duration.valueChanged.connect(self.update_duration)
        self.preview.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.images_filter = "JPEG (*.jpg);;PNG (*.png);;All files (*.*)"
        self.movies_filter = "MOV (*.mov);;MP4 (*.mp4);;All files (*.*)"
        self.movies_and_images_filter = (
            "JPEG (*.jpg);;PNG (*.png);;MOV (*.mov);;MP4 (*.mp4);;All files (*.*)"
        )
        self.sounds_filter = "MP3 (*.mp3);;WAV (*.wav);;All files (*.*)"

    def set_media_type(self, media_type: str):
        """Setter for media_type property.

        :media_type: Types of media that can be managed. Valid options are
            "images", "images and movies", "movies", "sounds".
        :type media_type: str
        """
        self.media_type = media_type
        if media_type == "movies":
            self.media_filter = self.movies_filter
        if media_type == "images":
            self.media_filter = self.images_filter
        if media_type == "images and movies":
            self.media_filter = self.movies_and_images_filter
        if media_type == "sounds":
            self.media_filter = self.sounds_filter

    def set_output_resolution(self, mode: str):
        """Set the output resolution for the media list.
        :param mode: Mode for video - either "720p", "1080p" or "4k"
        :type mode: str

        """
        if mode == "720p":
            self.output_mode = "1280:720"
        if mode == "1080p":
            self.output_mode = "1920:1080"
        else:
            self.output_mode = "3840:2160"

    def media_item_selected(self, current_index):
        """Handler for when an item is selected in the media list."""
        if current_index < 0:
            return
        file_path = self.media_list.currentItem().text()
        self.load_media(file_path)
        duration = self.media_list.currentItem().data(Qt.UserRole)
        self.duration.setValue(duration)

    def update_duration(self):
        """Set the current item duration when the duration is changed."""
        self.media_list.currentItem().setData(Qt.UserRole, self.duration.value())

    def choose_media_file(self):
        """
        Asks the user for the a media file path
        """
        # Popup a dialog to request the filename for music backing track
        dialog_title = "Select Media File"
        home = expanduser("~")
        directory = setting(
            key="last_directory", default=home, prefer_project_setting=True
        )
        # noinspection PyCallByClass,PyTypeChecker
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            dialog_title,
            directory,
            self.media_filter,
        )
        if file_path is None or file_path == "":
            return
        directory = os.path.abspath(file_path)
        directory = os.path.dirname(directory)
        set_setting(
            key="last_directory",
            value=directory,
            store_in_project=True,
        )
        self.create_item(file_path)

    def remove_media_file(self):
        """
        Removes the currentItem from the list.
        """
        items = self.media_list.selectedItems()
        if not items:
            return
        for item in items:
            self.media_list.takeItem(self.media_list.row(item))
        total = self.total_duration()
        self.total_duration_label.setText(
            f"Total duration for all media {total} seconds"
        )

    def create_item(self, file_path, duration=2):
        """Add an item to the list widget.

        :param file_path: Path to an on disk image, movie or sound file.
        :type file_path: str

        :param duration: Duration for which to play the resource (in seconds).
            Ignored for sound files.
        :type duration: int - defaults to 2s
        """
        item = QListWidgetItem(file_path)
        item.setData(Qt.UserRole, duration)
        self.media_list.insertItem(0, item)
        self.load_media(file_path)
        total = self.total_duration()
        self.total_duration_label.setText(
            f"Total duration for all media {total} seconds"
        )

    def load_media(self, file_path):
        """Load an image, movie or sound file.

        :param file_path: Path to the media file.
        :type file_path: str
        """
        image = QImage(file_path)
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self.preview.setPixmap(pixmap)
            #    pixmap.scaled(
            #        self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            #    )
            # )
        self.details_label.setText(str(file_path))

    def to_json(self):
        """Create a json document from the list widget items and their data.

        :returns: str containing the JSON document.
        """
        items = {}
        for index in range(self.media_list.count()):
            item = {
                "file": self.media_list.item(index).text(),
                "duration": self.media_list.item(index).data(Qt.UserRole),
            }
            items[index] = item
        json_object = json.dumps(items, indent=4)
        return json_object

    def from_json(self, json_document):
        """Restore the list widget items from a json document.

        :param json_document: Json document containing list state.
        :type json_document: str

        """
        items = json.loads(json_document)
        keys = items.keys()

        for index in keys:
            item = items[index]
            self.create_item(item["file"], item["duration"])

    def total_duration(self):
        """Calculate the total duration of all the added media files."""
        total = 0
        for index in range(self.media_list.count()):
            total += self.media_list.item(index).data(Qt.UserRole)
        return total

    def video_command(self):
        """Generate command for creating a video from the media files.

        ..note:: You need to add an executable and output filename to the command
            arguments before running this command. This is done in the
            movie_creator class.
        """
        count = self.media_list.count()
        if count == 0:
            return None
        arguments = ["-y"]
        for index in range(self.media_list.count()):
            file = self.media_list.item(index).text()
            duration = self.media_list.item(index).data(Qt.UserRole)
            if self.media_type == "images":
                # Images need to loop for a certain duration
                arguments.append("-loop")
                arguments.append("1")
                arguments.append("-t")
                arguments.append(str(duration))
            arguments.append("-i")
            arguments.append(file)
        if self.media_type != "sounds":
            arguments.append("-filter_complex")
            # Unsafe=1 used to deal with images or vids of different sizes
            arguments.append(
                f"concat=n={count}:v=1:a=0:unsafe=1"
                f",pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white,scale={self.output_mode},setsar=1:1"
            )
            arguments.append("-c:v")
            arguments.append("libx264")
            arguments.append("-pix_fmt")
            arguments.append("yuv420p")
            arguments.append("-r")
            # TODO - set this to the desired frame rate...
            arguments.append("60")
            arguments.append("-movflags")
            arguments.append("+faststart")
        # args.append("-vf")
        # args.append("scale={self.output_mode}")
        # consumer of this output needs to add filename as last arg
        return arguments
