# coding=utf-8
"""Widget for managing a list of media in the AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import json
from qgis.PyQt.QtWidgets import QWidget, QSizePolicy
from qgis.PyQt.QtCore import Qt

# from typing import Optional

# from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
# from PyQt5.QtMultimediaWidgets import QVideoWidget
# from qgis.PyQt.QtCore import pyqtSlot, QUrl
from qgis.PyQt.QtGui import QPixmap, QImage
from qgis.PyQt.QtWidgets import QFileDialog, QListWidgetItem
from .utilities import get_ui_class

FORM_CLASS = get_ui_class("media_list_widget_base.ui")


class MediaListWidget(QWidget, FORM_CLASS):
    """
    A widget for managing a list of media.
    """

    def __init__(self, media_type="images", parent=None):
        """Constructor for media_list_widget.

        :media_type: Types of media that can be managed. Valid options are
            "images", "images and movies", "movies", "sound".
        :type media_type: str

        :param parent: Parent widget of this widget.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.media_type = None
        self.media_filter = None
        self.set_media_type(media_type)
        self.media_list.currentRowChanged.connect(self.media_item_selected)
        self.add_media.clicked.connect(self.choose_media_file)
        self.remove_media.clicked.connect(self.remove_media_file)
        self.preview.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def set_media_type(self, media_type):
        """Setter for media_type property.

        :media_type: Types of media that can be managed. Valid options are
            "images", "images and movies", "movies", "sound".
        :type media_type: str
        """
        self.media_type = media_type
        self.images = "JPEG (*.jpg);;PNG (*.png)"
        self.movies = "MOV (*.mov);;MP4 (*.mp4)"
        self.movies_and_images = "JPEG (*.jpg);;PNG (*.png);;MOV (*.mov);;MP4 (*.mp4)"
        self.sounds = "MP3 (*.mp3);;WAV (*.wav)"
        if self.media_type == "movies":
            self.media_filter = self.movies
        if self.media_type == "images":
            self.media_filter = self.images
        if self.media_type == "images and movies":
            self.media_filter = self.movies_and_images
        if self.media_type == "sounds":
            self.media_type = self.sounds

    def media_item_selected(self, current_index):
        """Handler for when an item is selected in the media list."""
        if current_index < 0:
            return
        file_path = self.media_list.currentItem().text()
        self.load_media(file_path)
        duration = self.media_list.currentItem().data(Qt.UserRole)
        self.duration.setValue(duration)

    def choose_media_file(self):
        """
        Asks the user for the a media file path
        """
        # Popup a dialog to request the filename for music backing track
        dialog_title = "Media (jpg, png, mov, mp4) for video"

        # noinspection PyCallByClass,PyTypeChecker
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            dialog_title,
            self.media_filter,
            self.movies_and_images,
        )
        if file_path is None or file_path == "":
            return
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
            return
        args = ["-y "]
        for index in range(self.media_list.count()):
            file = self.media_list.item(index).text()
            duration = self.media_list.item(index).data(Qt.UserRole)
            args.append("-loop")
            args.append("1")
            args.append("-t")
            args.append(str(duration))
            args.append("-i")
            args.append(file)
        # Unsafe=1 used to deal with images or vids of different sizes
        args.append("-filter_complex")
        args.append(f'"concat=n={count}:v=1:a=0:unsafe=1"')
        # Next two lines raise compat issue with above two lines....
        # args.append("-vf")
        # args.append('"pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white"')
        args.append("-c:v")
        args.append("libx264")
        args.append("-pix_fmt")
        args.append("yuv420p")
        args.append("-r")
        # TODO - set this to the desired frame rate...
        args.append("25")
        args.append("-movflags")
        args.append("+faststart")
        # consumer of this output needs to add filename as last arg
        return args
