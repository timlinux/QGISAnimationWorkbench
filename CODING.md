# Animation Workbench Coding Guide

This guide outlines coding practices for developing Python code in the Animation Workbench project, including adherence to Python naming conventions, formatting styles, type declarations, and logging mechanisms.

## General Guidelines

- **Consistency**: Ensure consistent naming conventions, formatting, and structure throughout the codebase.
- **Readability**: Code should be clear and easy to read, with well-defined logical flows and separation of concerns.
- **Robustness**: Implement error handling to gracefully manage unexpected situations.

## Naming Conventions

Follow the standard Python naming conventions as defined in [PEP 8](https://peps.python.org/pep-0008/):

- **Variable and Function Names**: Use `snake_case`.

  ```python
  def create_animation_frame(frame_number: int) -> QImage:
      ...
  ```

- **Class Names**: Use `PascalCase`.

  ```python
  class AnimationController:
      ...
  ```

- **Constants**: Use `UPPER_SNAKE_CASE`.

  ```python
  DEFAULT_FRAME_RATE = 30
  ```

- **Private Variables and Methods**: Use a leading underscore.

  ```python
  def _calculate_frame_duration(self, total_frames: int) -> float:
      ...
  ```

### Exceptions for PyQt Naming Conventions

Follow the standard conventions for PyQt widgets and properties, even when they do not adhere to typical Python naming conventions:

- **Signals and Slots**: Use `camelCase`.
- **PyQt Widget Properties and Methods**: Use the default `camelCase` as provided by PyQt.

Example:

```python
self.frame_slider.valueChanged.connect(self.on_frame_changed)
```

## Code Formatting

### Black Formatter

- **Use Black**: All Python code should be formatted with [black](https://black.readthedocs.io/en/stable/), the opinionated code formatter.
- **Configuration**: Use a line length of 120 characters as configured in `pyproject.toml`.

To format code with Black:

```bash
black .
```

### Indentation and Spacing

- Use **4 spaces** per indentation level.
- Leave **1 blank line** between functions and class definitions.
- Leave **2 blank lines** before class definitions.

## Type Annotations

### Variable Declarations

- Always declare types for variables, parameters, and return values to enhance code clarity and type safety.

Examples:

```python
def render_frame(frame_number: int, output_path: str) -> bool:
    frame_image: QImage = self.generate_frame(frame_number)
    ...
```

```python
layer: QgsVectorLayer = self.layer_combo.currentLayer()
```

### Function Signatures

- Use type hints for all function parameters and return values.
- If a function does not return any value, use `-> None`.

Example:

```python
def start_animation(self) -> None:
    ...
```

### Type Imports

- Import types from `typing` where necessary:
  - `Optional`: To indicate optional parameters.
  - `List`, `Dict`, `Tuple`: For more complex types.

Example:

```python
from typing import List, Optional

def export_frames(frames: List[QImage], output_dir: str) -> None:
    ...
```

## Logging

### Use `QgsMessageLog` for Logging

- **Do not use `print()` statements** for debugging or outputting messages.
- Use `QgsMessageLog` for all logging to ensure messages are appropriately directed to QGIS's logging system.

### Standardize Log Tags

- **Tag all messages with `'AnimationWorkbench'`** to allow filtering in the QGIS log.
- Use appropriate log levels:
  - **`Qgis.Info`**: For informational messages.
  - **`Qgis.Warning`**: For warnings that do not interrupt the workflow.
  - **`Qgis.Critical`**: For errors that need immediate attention.

Examples:

```python
QgsMessageLog.logMessage("Animation started.", tag="AnimationWorkbench", level=Qgis.Info)
QgsMessageLog.logMessage("Warning: Frame skipped.", tag="AnimationWorkbench", level=Qgis.Warning)
QgsMessageLog.logMessage("Error rendering frame.", tag="AnimationWorkbench", level=Qgis.Critical)
```

## Error Handling

- **Graceful Error Handling**: Always catch exceptions and provide meaningful error messages through `QgsMessageLog`.
- **Use `try`/`except` Blocks**: Wrap code that may raise exceptions in `try`/`except` blocks and log the error.

Example:

```python
try:
    self.render_animation()
except Exception as e:
    QgsMessageLog.logMessage(f"Error rendering animation: {e}", tag="AnimationWorkbench", level=Qgis.Critical)
```

## GUI Development with PyQt5

- Follow the conventions required by PyQt5, using `camelCase` where necessary for properties and methods.
- Use descriptive variable names for widgets:
  - **`frame_slider`** for `QSlider`
  - **`output_path_edit`** for `QLineEdit`
  - **`render_button`** for `QPushButton`
- Maintain a consistent naming pattern throughout the user interface code.

## Code Structure

### Order of Methods

- **Class Methods Order**:
  1. **`__init__` method**
  2. **Public methods** in the order of their usage
  3. **Private (helper) methods** prefixed with `_`

## Comments and Docstrings

### Use Docstrings

- Add docstrings to all functions, classes, and modules using the `"""triple quotes"""` format.
- Include a brief description, parameters, and return values where applicable.
- Use Google-style docstrings.

Example:

```python
def export_animation(self, output_path: str) -> bool:
    """
    Exports the animation to a video file.

    Args:
        output_path: The path where the video file will be saved.

    Returns:
        True if the export was successful, False otherwise.
    """
    ...
```

### Inline Comments

- Use inline comments sparingly and only when necessary to clarify complex logic.
- Use the `#` symbol with a space to start the comment.

Example:

```python
# Calculate the interpolated position between keyframes
position = self._interpolate(start_pos, end_pos, t)
```

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. Before committing, run:

```bash
./scripts/checks.sh
```

Or install the hooks to run automatically:

```bash
pre-commit install
```

## Development Environment

### Using Nix Flakes

This project uses Nix flakes for reproducible development environments. After enabling direnv:

```bash
cd /path/to/QGISAnimationWorkbench
direnv allow
```

This will automatically set up your development environment with all required dependencies.

### Launching QGIS

Use the provided scripts to launch QGIS with the correct profile:

```bash
./scripts/start_qgis.sh        # Latest QGIS
./scripts/start_qgis_ltr.sh    # LTR version
./scripts/start_qgis_master.sh # Development version
```

### VSCode Setup

For VSCode development with proper Python paths and extensions:

```bash
./scripts/vscode.sh
```

## Summary Checklist

- **Naming**: Use `snake_case`, `PascalCase`, or `camelCase` as appropriate.
- **Formatting**: Use `black` for consistent code formatting.
- **Type Declarations**: Declare types for all variables and function signatures.
- **Logging**: Use `QgsMessageLog` with the tag `'AnimationWorkbench'`.
- **Error Handling**: Catch and log exceptions appropriately.
- **PyQt5**: Follow PyQt5's conventions for widget naming and handling.
- **Docstrings and Comments**: Use meaningful docstrings and comments to explain the code.
- **Pre-commit**: Run pre-commit hooks before committing code.

Following these guidelines ensures that code within the Animation Workbench project is clear, consistent, and maintainable.
