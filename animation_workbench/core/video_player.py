# coding=utf-8
"""Video player utilities for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import os
import platform
import subprocess
from typing import Optional, Tuple

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices

# Try to import multimedia components
_multimedia_available = False
_multimedia_error = None

try:
    from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
    from PyQt5.QtMultimediaWidgets import QVideoWidget

    _multimedia_available = True
except ImportError as e:
    _multimedia_error = str(e)


def is_multimedia_available() -> Tuple[bool, Optional[str]]:
    """
    Check if Qt Multimedia is available.

    :returns: Tuple of (available, error_message)
    """
    return _multimedia_available, _multimedia_error


def open_in_system_player(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Open a video file in the system's default media player.

    :param file_path: Path to the video file.
    :returns: Tuple of (success, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    system = platform.system()

    try:
        # First try QDesktopServices - this is the most cross-platform approach
        url = QUrl.fromLocalFile(file_path)
        if QDesktopServices.openUrl(url):
            return True, None

        # Fallback to platform-specific commands
        if system == "Windows":
            os.startfile(file_path)  # noqa: S606
            return True, None
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)  # noqa: S603, S607
            return True, None
        else:  # Linux and others
            # Try xdg-open first (most common on Linux)
            try:
                subprocess.run(["xdg-open", file_path], check=True)  # noqa: S603, S607
                return True, None
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Try other common players
                for player in ["vlc", "mpv", "totem", "mplayer", "smplayer"]:
                    try:
                        subprocess.Popen([player, file_path])  # noqa: S603, S607
                        return True, None
                    except FileNotFoundError:
                        continue

                return False, "No suitable video player found"

    except Exception as e:
        return False, str(e)


def get_system_player_name() -> str:
    """
    Get a user-friendly name for the system player action.

    :returns: Description string for the system player.
    """
    system = platform.system()
    if system == "Windows":
        return "Windows Media Player"
    elif system == "Darwin":
        return "QuickTime Player"
    else:
        return "System Video Player"


class VideoPlayerStatus:
    """Status codes for video player operations."""

    SUCCESS = "success"
    MULTIMEDIA_UNAVAILABLE = "multimedia_unavailable"
    CODEC_ERROR = "codec_error"
    FILE_NOT_FOUND = "file_not_found"
    UNKNOWN_ERROR = "unknown_error"


def get_video_playback_instructions() -> str:
    """
    Get platform-specific instructions for fixing video playback issues.

    :returns: HTML-formatted instructions.
    """
    system = platform.system()

    if system == "Windows":
        return """
<h3>Video Playback Not Available</h3>
<p>The embedded video player requires additional codecs.</p>

<h4>To fix this:</h4>
<ol>
<li>Install <a href="https://www.codecguide.com/download_kl.htm">K-Lite Codec Pack</a> (Basic version is sufficient)</li>
<li>Or install the <a href="https://github.com/nickaein/vlc-qt">VLC Qt plugin</a></li>
<li>Restart QGIS after installation</li>
</ol>

<p>Alternatively, click "Open in System Player" to view your video in your default media player.</p>
"""
    elif system == "Darwin":
        return """
<h3>Video Playback Not Available</h3>
<p>The embedded video player may not be available in this QGIS build.</p>

<h4>Workaround:</h4>
<p>Click "Open in System Player" to view your video in QuickTime Player or your default media application.</p>

<p>The video has been saved successfully and can be found at the output path you specified.</p>
"""
    else:  # Linux
        return """
<h3>Video Playback Not Available</h3>
<p>The embedded video player requires GStreamer plugins.</p>

<h4>To fix this (Ubuntu/Debian):</h4>
<pre>sudo apt install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav</pre>

<h4>To fix this (Fedora):</h4>
<pre>sudo dnf install gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly gstreamer1-libav</pre>

<h4>To fix this (Arch Linux):</h4>
<pre>sudo pacman -S gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav</pre>

<p>Alternatively, click "Open in System Player" to view your video in VLC or your default media player.</p>
"""
