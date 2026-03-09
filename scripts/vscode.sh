#!/usr/bin/env bash

# ----------------------------------------------
# User-adjustable parameters
# ----------------------------------------------

VSCODE_PROFILE="AnimationWorkbench"
EXT_DIR=".vscode-extensions"
VSCODE_DIR=".vscode"
LOG_FILE="vscode.log"
EXT_LIST_FILE="$(dirname "$0")/vscode-extensions.txt"

# Read extensions from file
if [[ ! -f "$EXT_LIST_FILE" ]]; then
    echo "Extension list file not found: $EXT_LIST_FILE"
    exit 1
fi
mapfile -t REQUIRED_EXTENSIONS <"$EXT_LIST_FILE"

# ----------------------------------------------
# Functions
# ----------------------------------------------

launch_vscode() {
    code --user-data-dir="$VSCODE_DIR" \
        --profile="${VSCODE_PROFILE}" \
        --extensions-dir="$EXT_DIR" "$@"
}

list_installed_extensions() {
    echo "Installed extensions:"
    echo "" >"$EXT_LIST_FILE"
    find "$EXT_DIR" -maxdepth 1 -mindepth 1 -type d | while read -r dir; do
        pkg="$dir/package.json"
        if [[ -f "$pkg" ]]; then
            name=$(jq -r '.name' <"$pkg")
            publisher=$(jq -r '.publisher' <"$pkg")
            version=$(jq -r '.version' <"$pkg")
            echo "${publisher}.${name}@${version}" >>"$EXT_LIST_FILE"
        fi
    done
    # Now sort the extension list and pipe it through uniq to remove duplicates
    sort -u "$EXT_LIST_FILE" -o "$EXT_LIST_FILE"
    cat "$EXT_LIST_FILE"
}

clean() {
    rm -rf .vscode .vscode-extensions
}
print_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

This script sets up and launches VSCode with a custom profile and extensions for the Animation Workbench project.

Actions performed:
    - Checks for required files and directories
    - Ensures VSCode and Docker are installed
    - Initializes VSCode user and extension directories if needed
    - Updates VSCode settings for commit signing, formatters, and linters (Markdown, Shell, Python)
    - Installs all required VSCode extensions
    - Launches VSCode with the specified profile and directories

Options:
    --help             Show this help message and exit
    --verbose          Print final settings.json contents before launching VSCode
    --list-extensions  List installed VSCode extensions in the custom extensions directory
    --clean            Remove the .vscode and .vscode-extensions directories completely

EOF
}

# Parameter handler
for arg in "$@"; do
    case "$arg" in
        --help)
            print_help
            exit 0
            ;;
        --verbose)
            # Handled later in the script
            ;;
        --list-extensions)
            list_installed_extensions
            exit 0
            ;;
        --clean)
            echo "Remove .vscode and .vscode-extensions folders:"
            clean
            exit 0
            ;;
        *) ;;
    esac
done

# ----------------------------------------------
# Script starts here
# ----------------------------------------------

# Truncate the log file at the start
echo "Truncating $LOG_FILE..."
true >"$LOG_FILE"

# Locate QGIS binary
QGIS_BIN=$(which qgis)

if [[ -z "$QGIS_BIN" ]]; then
    echo "Error: QGIS binary not found!"
    exit 1
fi

# Extract the Nix store path (removing /bin/qgis)
QGIS_PREFIX=$(dirname "$(dirname "$QGIS_BIN")")

# Construct the correct QGIS Python path
QGIS_PYTHON_PATH="$QGIS_PREFIX/share/qgis/python"

# Check if the Python directory exists
if [[ ! -d "$QGIS_PYTHON_PATH" ]]; then
    echo "Error: QGIS Python path not found at $QGIS_PYTHON_PATH"
    exit 1
fi

# Create .env file for VSCode
ENV_FILE=".env"

echo "Creating VSCode .env file..."
cat <<EOF >"$ENV_FILE"
PYTHONPATH=$QGIS_PYTHON_PATH
# needed for launch.json
QGIS_EXECUTABLE=$QGIS_BIN
QGIS_PREFIX_PATH=$QGIS_PREFIX
PYQT5_PATH="$QGIS_PREFIX/share/qgis/python/PyQt"
QT_QPA_PLATFORM=offscreen
EOF

echo ".env file created successfully!"
echo "Contents of .env:"
cat "$ENV_FILE"

# Also set the python path in this shell in case we want to run tests etc from the command line
export PYTHONPATH=$PYTHONPATH:$QGIS_PYTHON_PATH

echo "Checking VSCode is installed ..."
if ! command -v code &>/dev/null; then
    echo "  'code' CLI not found. Please install VSCode and add 'code' to your PATH."
    exit 1
else
    echo "  VSCode found ok."
fi

# Ensure .vscode directory exists
echo "Checking if VSCode has been run before..."
if [ ! -d .vscode ]; then
    echo "  It appears you have not run vscode in this project before."
    echo "     After it opens, please close vscode and then rerun this script"
    echo "     so that the extensions directory initialises properly."
    mkdir -p .vscode
    mkdir -p .vscode-extensions
    # Launch VSCode with the sandboxed environment
    launch_vscode .
    exit 1
else
    echo "  VSCode directory found from previous runs of vscode."
fi

echo "Checking if VSCode has been run before..."
if [ ! -d "$VSCODE_DIR" ]; then
    echo "  First-time VSCode run detected. Opening VSCode to initialize..."
    mkdir -p "$VSCODE_DIR"
    mkdir -p "$EXT_DIR"
    launch_vscode .
    exit 1
else
    echo "  VSCode directory detected."
fi

SETTINGS_FILE="$VSCODE_DIR/settings.json"

echo "Checking if settings.json exists..."
if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo "{}" >"$SETTINGS_FILE"
    echo "  Created new settings.json"
else
    echo "  settings.json exists"
fi

echo "Updating git commit signing setting..."
jq '.["git.enableCommitSigning"] = true' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
echo "  git.enableCommitSigning enabled"

echo "Ensuring markdown formatter is set..."
if ! jq -e '."[markdown]".editor.defaultFormatter' "$SETTINGS_FILE" >/dev/null; then
    jq '."[markdown]" += {"editor.defaultFormatter": "DavidAnson.vscode-markdownlint"}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Markdown formatter set"
else
    echo "  Markdown formatter already configured"
fi

echo "Ensuring shell script formatter and linter are set..."
if ! jq -e '."[shellscript]".editor.defaultFormatter' "$SETTINGS_FILE" >/dev/null; then
    jq '."[shellscript]" += {"editor.defaultFormatter": "foxundermoon.shell-format", "editor.formatOnSave": true}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Shell script formatter set to foxundermoon.shell-format, formatOnSave enabled"
else
    echo "  Shell script formatter already configured"
fi

if ! jq -e '.["shellcheck.enable"]' "$SETTINGS_FILE" >/dev/null; then
    jq '. + {"shellcheck.enable": true}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  ShellCheck linting enabled"
else
    echo "  ShellCheck linting already configured"
fi

if ! jq -e '.["shellformat.flag"]' "$SETTINGS_FILE" >/dev/null; then
    jq '. + {"shellformat.flag": "-i 4 -bn -ci"}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Shell format flags set (-i 4 -bn -ci)"
else
    echo "  Shell format flags already configured"
fi
echo "Ensuring global format-on-save is enabled..."
if ! jq -e '.["editor.formatOnSave"]' "$SETTINGS_FILE" >/dev/null; then
    jq '. + {"editor.formatOnSave": true}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Global formatOnSave enabled"
else
    echo "  Global formatOnSave already configured"
fi

# Python formatter and linter
echo "Ensuring Python formatter and linter are set..."
if ! jq -e '."[python]".editor.defaultFormatter' "$SETTINGS_FILE" >/dev/null; then
    jq '."[python]" += {"editor.defaultFormatter": "ms-python.black-formatter"}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Python formatter set to Black"
else
    echo "  Python formatter already configured"
fi

if ! jq -e '.["python.linting.enabled"]' "$SETTINGS_FILE" >/dev/null; then
    jq '. + {"python.linting.enabled": true, "python.linting.pylintEnabled": true}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Python linting enabled (pylint)"
else
    echo "  Python linting already configured"
fi

echo "Ensuring Python Testing Env is set..."
if ! jq -e '."[python]".editor.pytestArgs' "$SETTINGS_FILE" >/dev/null; then
    jq '."[python]" += {"editor.pytestArgs": "test"}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Python test set up"
else
    echo "  Python tests already configured"
fi
if ! jq -e '."[python]".testing.unittestEnabled' "$SETTINGS_FILE" >/dev/null; then
    jq '. + {"python.editor.unittestEnabled": false, "python.testing.pytestEnabled": true}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Python unit test set up"
else
    echo "  Python unit tests already configured"
fi
echo "Ensuring Python Env File is set..."
if ! jq -e '."[python]".envFile' "$SETTINGS_FILE" >/dev/null; then
    jq '."[python]" += {"envFile": "${workspaceFolder}/.env"}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Python Env file set up"
else
    echo "  Python Env File already configured"
fi

echo "Ensuring nixfmt is run on save for .nix files..."
if ! jq -e '."[nix]".editor.defaultFormatter' "$SETTINGS_FILE" >/dev/null; then
    jq '."[nix]" += {"editor.defaultFormatter": "brettm12345.nixfmt", "editor.formatOnSave": true}' "$SETTINGS_FILE" >"$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    echo "  Nix formatter set to brettm12345.nixfmt, formatOnSave enabled"
else
    echo "  Nix formatter already configured"
fi

if [[ " $* " == *" --verbose "* ]]; then
    echo "Final settings.json contents:"
    cat "$SETTINGS_FILE"
fi

# Add VSCode runner configuration
# shellcheck disable=SC2154
cat <<EOF >.vscode/launch.json
{
    "version": "0.2.0",

    "configurations": [
        {
            "name": "QGIS Plugin Debug",
            "type": "debugpy",
            "request": "launch",

            "program": "\${env:QGIS_EXECUTABLE}",
            "args": ["--profile", "AnimationWorkbench"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/animation_workbench"
            }
        },
        {
            "name": "Python: Remote Attach 9000",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 9000
            },
            "pathMappings": [
                {
                    "localRoot": "\${workspaceFolder}/animation_workbench",
                    "remoteRoot": "\${env:HOME}/.local/share/QGIS/QGIS3/profiles/AnimationWorkbench/python/plugins/animation_workbench"
                }
            ]
        }
    ]
}
EOF

echo "Installing required extensions..."
installed_exts=$(list_installed_extensions)
for ext in "${REQUIRED_EXTENSIONS[@]}"; do
    if echo "$installed_exts" | grep -q "^${ext}$"; then
        echo "  Extension ${ext} already installed."
    else
        echo "  Installing ${ext}..."
        # Capture both stdout and stderr to log file
        if launch_vscode --install-extension "${ext}" >>"$LOG_FILE" 2>&1; then
            # Refresh installed_exts after install
            installed_exts=$(list_installed_extensions)
            if echo "$installed_exts" | grep -q "^${ext}$"; then
                echo "  Successfully installed ${ext}."
            else
                echo "  Failed to install ${ext} (not found after install)."
                exit 1
            fi
        else
            echo "  Failed to install ${ext} (error during install). Check $LOG_FILE for details."
            exit 1
        fi
    fi
done

echo "Launching VSCode..."
launch_vscode .
