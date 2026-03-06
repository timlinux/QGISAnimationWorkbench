# coding=utf-8
"""Kartoza branding utilities for the Animation Workbench plugin."""

__copyright__ = "Copyright 2024, Kartoza"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"

import os
from typing import Optional

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QPixmap
from qgis.PyQt.QtWidgets import QHBoxLayout, QLabel, QWidget


# Kartoza Brand Colors
KARTOZA_GREEN_DARK = "#589632"
KARTOZA_GREEN_LIGHT = "#93b023"
KARTOZA_GOLD = "#E8B849"


def get_stylesheet_path() -> str:
    """Get the path to the Kartoza stylesheet.

    Returns:
        str: Absolute path to the kartoza.qss file.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "resources", "styles", "kartoza.qss")


def load_stylesheet() -> str:
    """Load the Kartoza stylesheet content.

    Returns:
        str: The stylesheet content as a string.
    """
    stylesheet_path = get_stylesheet_path()
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def apply_kartoza_styling(widget: QWidget) -> None:
    """Apply Kartoza branding stylesheet to a widget.

    Args:
        widget: The widget to apply styling to.
    """
    stylesheet = load_stylesheet()
    if stylesheet:
        widget.setStyleSheet(stylesheet)


class KartozaFooter(QWidget):
    """A branded footer widget showing Kartoza attribution and links."""

    GITHUB_REPO = "https://github.com/timlinux/QGISAnimationWorkbench"
    KARTOZA_URL = "https://kartoza.com"
    SPONSOR_URL = "https://github.com/sponsors/timlinux"

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the Kartoza footer widget.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the footer UI with simple hyperlinks."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        # Create a single label with HTML hyperlinks
        footer_label = QLabel()
        footer_label.setOpenExternalLinks(True)
        footer_label.setTextFormat(Qt.RichText)
        footer_label.setAlignment(Qt.AlignCenter)

        html = f"""
        <span style="font-size: 11px;">
            Made with <span style="color: #e25555;">\u2764</span> by
            <a href="{self.KARTOZA_URL}" style="color: {KARTOZA_GREEN_LIGHT}; font-weight: bold;">Kartoza</a>
            |
            <a href="{self.SPONSOR_URL}" style="color: {KARTOZA_GOLD}; font-weight: bold;">Donate!</a>
            |
            <a href="{self.GITHUB_REPO}" style="color: {KARTOZA_GREEN_LIGHT}; font-weight: bold;">GitHub</a>
        </span>
        """
        footer_label.setText(html)
        layout.addWidget(footer_label)


class KartozaHeader(QWidget):
    """A branded header widget with logo and title."""

    def __init__(
        self,
        title: str = "Animation Workbench",
        subtitle: str = "",
        parent: Optional[QWidget] = None,
    ):
        """Initialize the header widget.

        Args:
            title: Main title text.
            subtitle: Optional subtitle text.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the header UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "icons",
            "animation-workbench.svg",
        )
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_label)

        # Title container
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        # Title
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {KARTOZA_GREEN_DARK};")
        title_layout.addWidget(title_label)

        # Subtitle
        if self.subtitle:
            subtitle_label = QLabel(f"- {self.subtitle}")
            subtitle_font = QFont()
            subtitle_font.setPointSize(12)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setStyleSheet(f"color: {KARTOZA_GREEN_LIGHT};")
            title_layout.addWidget(subtitle_label)

        title_layout.addStretch()
        layout.addWidget(title_container)
        layout.addStretch()

        # Set background gradient
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(88, 150, 50, 0.1),
                    stop:0.5 rgba(147, 176, 35, 0.05),
                    stop:1 rgba(88, 150, 50, 0.1)
                );
                border-bottom: 2px solid {KARTOZA_GREEN_DARK};
            }}
        """)
