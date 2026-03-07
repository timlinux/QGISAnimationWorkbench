# coding=utf-8
"""Dependency checking and installation utilities for AnimationWorkbench."""

__copyright__ = "Copyright 2022, Tim Sutton"
__license__ = "GPL version 3"
__email__ = "tim@kartoza.com"
__revision__ = "$Format:%H$"

import platform
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .utilities import CoreUtils


class DependencyStatus(Enum):
    """Status of a dependency check."""

    AVAILABLE = "available"
    MISSING = "missing"
    INSTALL_FAILED = "install_failed"


@dataclass
class DependencyResult:
    """Result of a dependency check."""

    name: str
    status: DependencyStatus
    path: Optional[str] = None
    message: Optional[str] = None


class DependencyInstallDialog(QDialog):
    """Dialog showing dependency installation instructions."""

    def __init__(self, title: str, instructions: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel(title)
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header.setFont(header_font)
        layout.addWidget(header)

        # Instructions
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(instructions)
        layout.addWidget(text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)


class DependencyChecker:
    """Checks for and helps install required dependencies."""

    PYQTGRAPH_INSTALL_INSTRUCTIONS = """
<h3>pyqtgraph is required for easing curve previews</h3>

<p>To install pyqtgraph, open a terminal/command prompt and run:</p>

<h4>All Platforms:</h4>
<pre>pip install pyqtgraph</pre>

<p>Or if using Python 3:</p>
<pre>pip3 install pyqtgraph</pre>

<h4>On Windows (from OSGeo4W Shell):</h4>
<pre>python -m pip install pyqtgraph</pre>

<h4>On macOS/Linux with system Python:</h4>
<pre>python3 -m pip install --user pyqtgraph</pre>

<p>After installing, please restart QGIS.</p>
"""

    @staticmethod
    def get_ffmpeg_install_instructions() -> str:
        """Get platform-specific ffmpeg installation instructions."""
        system = platform.system()

        if system == "Windows":
            return """
<h3>FFmpeg is required for video export</h3>

<p>FFmpeg is not installed or not found in your PATH.</p>

<h4>Option 1: Download from official website</h4>
<ol>
<li>Visit <a href="https://ffmpeg.org/download.html">https://ffmpeg.org/download.html</a></li>
<li>Click "Windows" and download a build (e.g., from gyan.dev)</li>
<li>Extract the zip file to a folder (e.g., <code>C:\\ffmpeg</code>)</li>
<li>Add the <code>bin</code> folder to your PATH:
    <ul>
    <li>Open Start Menu, search "Environment Variables"</li>
    <li>Click "Environment Variables..."</li>
    <li>Under "User variables", find "Path" and click "Edit"</li>
    <li>Click "New" and add <code>C:\\ffmpeg\\bin</code></li>
    <li>Click OK to save</li>
    </ul>
</li>
<li>Restart QGIS</li>
</ol>

<h4>Option 2: Using Chocolatey (if installed)</h4>
<pre>choco install ffmpeg</pre>

<h4>Option 3: Using winget</h4>
<pre>winget install ffmpeg</pre>

<p>After installing, restart QGIS for changes to take effect.</p>
"""
        elif system == "Darwin":  # macOS
            return """
<h3>FFmpeg is required for video export</h3>

<p>FFmpeg is not installed or not found in your PATH.</p>

<h4>Option 1: Using Homebrew (recommended)</h4>
<pre>brew install ffmpeg</pre>

<h4>Option 2: Using MacPorts</h4>
<pre>sudo port install ffmpeg</pre>

<h4>Option 3: Download binary</h4>
<ol>
<li>Visit <a href="https://ffmpeg.org/download.html">https://ffmpeg.org/download.html</a></li>
<li>Click "macOS" and download a static build</li>
<li>Extract and move <code>ffmpeg</code> to <code>/usr/local/bin/</code></li>
</ol>

<p>After installing, restart QGIS for changes to take effect.</p>
"""
        else:  # Linux
            return """
<h3>FFmpeg is required for video export</h3>

<p>FFmpeg is not installed or not found in your PATH.</p>

<h4>Ubuntu/Debian:</h4>
<pre>sudo apt update && sudo apt install ffmpeg</pre>

<h4>Fedora:</h4>
<pre>sudo dnf install ffmpeg</pre>

<h4>Arch Linux:</h4>
<pre>sudo pacman -S ffmpeg</pre>

<h4>openSUSE:</h4>
<pre>sudo zypper install ffmpeg</pre>

<h4>Using Nix:</h4>
<pre>nix-env -iA nixpkgs.ffmpeg</pre>

<p>After installing, restart QGIS for changes to take effect.</p>
"""

    @staticmethod
    def get_imagemagick_install_instructions() -> str:
        """Get platform-specific ImageMagick installation instructions."""
        system = platform.system()

        if system == "Windows":
            return """
<h3>ImageMagick is required for GIF export</h3>

<p>ImageMagick (convert command) is not installed or not found in your PATH.</p>

<h4>Option 1: Download installer</h4>
<ol>
<li>Visit <a href="https://imagemagick.org/script/download.php#windows">https://imagemagick.org/script/download.php</a></li>
<li>Download the Windows installer (ImageMagick-x.x.x-Q16-HDRI-x64-dll.exe)</li>
<li><b>Important:</b> During installation, check "Add application directory to your system path"</li>
<li>Complete the installation</li>
<li>Restart QGIS</li>
</ol>

<h4>Option 2: Using Chocolatey</h4>
<pre>choco install imagemagick</pre>

<p>After installing, restart QGIS for changes to take effect.</p>
"""
        elif system == "Darwin":  # macOS
            return """
<h3>ImageMagick is required for GIF export</h3>

<p>ImageMagick (convert command) is not installed or not found in your PATH.</p>

<h4>Option 1: Using Homebrew (recommended)</h4>
<pre>brew install imagemagick</pre>

<h4>Option 2: Using MacPorts</h4>
<pre>sudo port install ImageMagick</pre>

<p>After installing, restart QGIS for changes to take effect.</p>
"""
        else:  # Linux
            return """
<h3>ImageMagick is required for GIF export</h3>

<p>ImageMagick (convert command) is not installed or not found in your PATH.</p>

<h4>Ubuntu/Debian:</h4>
<pre>sudo apt update && sudo apt install imagemagick</pre>

<h4>Fedora:</h4>
<pre>sudo dnf install ImageMagick</pre>

<h4>Arch Linux:</h4>
<pre>sudo pacman -S imagemagick</pre>

<h4>openSUSE:</h4>
<pre>sudo zypper install ImageMagick</pre>

<h4>Using Nix:</h4>
<pre>nix-env -iA nixpkgs.imagemagick</pre>

<p>After installing, restart QGIS for changes to take effect.</p>
"""

    @classmethod
    def check_pyqtgraph(cls) -> DependencyResult:
        """Check if pyqtgraph is available."""
        try:
            import pyqtgraph  # noqa: F401

            return DependencyResult(
                name="pyqtgraph", status=DependencyStatus.AVAILABLE, message="pyqtgraph is installed"
            )
        except ImportError:
            return DependencyResult(
                name="pyqtgraph", status=DependencyStatus.MISSING, message="pyqtgraph is not installed"
            )

    @classmethod
    def install_pyqtgraph(cls) -> DependencyResult:
        """Attempt to install pyqtgraph using pip."""
        try:
            # Use subprocess instead of deprecated pip.main()
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyqtgraph"], capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return DependencyResult(
                    name="pyqtgraph", status=DependencyStatus.AVAILABLE, message="pyqtgraph installed successfully"
                )
            else:
                return DependencyResult(
                    name="pyqtgraph",
                    status=DependencyStatus.INSTALL_FAILED,
                    message=f"Installation failed: {result.stderr}",
                )
        except subprocess.TimeoutExpired:
            return DependencyResult(
                name="pyqtgraph", status=DependencyStatus.INSTALL_FAILED, message="Installation timed out"
            )
        except Exception as e:
            return DependencyResult(
                name="pyqtgraph", status=DependencyStatus.INSTALL_FAILED, message=f"Installation error: {str(e)}"
            )

    @classmethod
    def ensure_pyqtgraph(cls, parent=None, auto_install=True) -> bool:
        """
        Ensure pyqtgraph is available, attempting installation if needed.

        :param parent: Parent widget for dialogs.
        :param auto_install: Whether to attempt automatic installation.
        :returns: True if pyqtgraph is available, False otherwise.
        """
        result = cls.check_pyqtgraph()

        if result.status == DependencyStatus.AVAILABLE:
            return True

        if auto_install:
            # Ask user before installing
            reply = QMessageBox.question(
                parent,
                "Install Required Dependency",
                "The 'pyqtgraph' package is required for easing curve previews.\n\n"
                "Would you like to install it now?\n\n"
                "(This will run: pip install pyqtgraph)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if reply == QMessageBox.Yes:
                # Show progress
                QMessageBox.information(
                    parent,
                    "Installing...",
                    "Installing pyqtgraph. This may take a moment.\n" "QGIS may appear unresponsive briefly.",
                )

                install_result = cls.install_pyqtgraph()

                if install_result.status == DependencyStatus.AVAILABLE:
                    QMessageBox.information(
                        parent,
                        "Installation Successful",
                        "pyqtgraph has been installed successfully.\n\n"
                        "Please restart QGIS to use the easing preview feature.",
                    )
                    return False  # Need restart
                else:
                    # Show manual instructions
                    dialog = DependencyInstallDialog(
                        "Manual Installation Required",
                        f"<p>Automatic installation failed:</p>"
                        f"<pre>{install_result.message}</pre>"
                        f"{cls.PYQTGRAPH_INSTALL_INSTRUCTIONS}",
                        parent,
                    )
                    dialog.exec_()
                    return False
            else:
                return False
        else:
            # Show manual instructions
            dialog = DependencyInstallDialog(
                "Missing Dependency: pyqtgraph", cls.PYQTGRAPH_INSTALL_INSTRUCTIONS, parent
            )
            dialog.exec_()
            return False

    @classmethod
    def check_ffmpeg(cls) -> DependencyResult:
        """Check if ffmpeg is available."""
        paths = CoreUtils.which("ffmpeg")
        if paths:
            return DependencyResult(
                name="ffmpeg", status=DependencyStatus.AVAILABLE, path=paths[0], message=f"ffmpeg found at {paths[0]}"
            )
        return DependencyResult(name="ffmpeg", status=DependencyStatus.MISSING, message="ffmpeg not found in PATH")

    @classmethod
    def check_imagemagick(cls) -> DependencyResult:
        """Check if ImageMagick convert command is available."""
        paths = CoreUtils.which("convert")
        if paths:
            return DependencyResult(
                name="ImageMagick",
                status=DependencyStatus.AVAILABLE,
                path=paths[0],
                message=f"convert found at {paths[0]}",
            )
        return DependencyResult(
            name="ImageMagick", status=DependencyStatus.MISSING, message="ImageMagick (convert) not found in PATH"
        )

    @classmethod
    def check_movie_dependencies(cls, for_gif: bool = False) -> List[DependencyResult]:
        """
        Check all dependencies required for movie creation.

        :param for_gif: If True, check for GIF requirements (ImageMagick).
                       If False, check for MP4 requirements (ffmpeg).
        :returns: List of dependency check results.
        """
        results = []

        if for_gif:
            results.append(cls.check_imagemagick())
        else:
            results.append(cls.check_ffmpeg())

        return results

    @classmethod
    def show_missing_dependency_dialog(cls, results: List[DependencyResult], parent=None) -> bool:
        """
        Show dialog for missing dependencies with installation instructions.

        :param results: List of dependency check results.
        :param parent: Parent widget for dialog.
        :returns: True if all dependencies are available, False otherwise.
        """
        missing = [r for r in results if r.status == DependencyStatus.MISSING]

        if not missing:
            return True

        instructions = ""
        for result in missing:
            if result.name == "ffmpeg":
                instructions += cls.get_ffmpeg_install_instructions()
            elif result.name == "ImageMagick":
                instructions += cls.get_imagemagick_install_instructions()

        dialog = DependencyInstallDialog("Missing Dependencies", instructions, parent)
        dialog.exec_()
        return False

    @classmethod
    def validate_movie_export(cls, for_gif: bool, parent=None) -> Tuple[bool, Optional[str]]:
        """
        Validate that all dependencies for movie export are available.

        :param for_gif: Whether exporting as GIF (vs MP4).
        :param parent: Parent widget for dialogs.
        :returns: Tuple of (success, tool_path). If success is False, tool_path is None.
        """
        results = cls.check_movie_dependencies(for_gif=for_gif)
        missing = [r for r in results if r.status == DependencyStatus.MISSING]

        if missing:
            cls.show_missing_dependency_dialog(results, parent)
            return False, None

        # Return the path to the tool
        tool_result = results[0]
        return True, tool_result.path
