# Version 1.4

Adds QGIS 4 / Qt6 compatibility. The plugin previously crashed immediately
on QGIS 4 (PyQt6); it now runs on both QGIS 3.x (PyQt5) and QGIS 4.x (PyQt6).

### Fixed

* Declare QGIS 4.x compatibility (`qgisMaximumVersion=4.99`) so the plugin
  is no longer blocked from loading on QGIS 4.
* Fix `AttributeError` crashes from PyQt5-style unscoped enum access, which
  PyQt6 removed (e.g. `QEasingCurve.Linear` -> `QEasingCurve.Type.Linear`,
  `Qt.AlignCenter` -> `Qt.AlignmentFlag.AlignCenter`, and the same pattern
  across `QDialogButtonBox`, `QMessageBox`, `QStyle`, `QSizePolicy`,
  `QPalette`, `QProcess`, and `Qt.WA_DeleteOnClose`).
* Fix `TypeError` crash from passing a raw `int` to `setToolButtonStyle`,
  which PyQt6 requires as a real enum value.
* Port the embedded video player to Qt6's `QtMultimedia` API: `QMediaContent`
  was removed (replaced by `QMediaPlayer.setSource`), and the
  `stateChanged`/`error` signals were renamed to
  `playbackStateChanged`/`errorOccurred`. Qt5 (QGIS 3.x) behaviour is
  preserved via a runtime Qt-version check.
* Replace `PyQt5`-hardcoded imports with the canonical `qgis.PyQt` shim
  (which resolves to whichever Qt binding QGIS itself uses) in the video
  player and the test suite's mock `qgis_interface`.
* Fix invisible media-list add/remove buttons: their `.ui`-defined emoji
  glyphs (`➕`/`➖`) have no glyph in the available font stack and rendered
  as blank "tofu" boxes; replaced with plain `+`/`-` text.
* Fix invisible spin-box up/down arrows: styling `QSpinBox`/`QDoubleSpinBox`
  with custom QSS switches Qt off its native paint path for the whole
  compound control, so the arrow sub-controls (left unstyled) rendered as
  blank blocks. Spin boxes are now excluded from the shared input-styling
  rule and keep their native, fully visible arrows.

# Version 1.3

* Auto install pyqtgraph

# Version 1.0.0 - date

* Initial version of the QGIS Animation Workbench
