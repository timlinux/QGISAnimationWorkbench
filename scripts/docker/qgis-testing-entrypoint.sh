#!/usr/bin/env bash

# SPDX-FileCopyrightText: Tim Sutton
# SPDX-License-Identifier: MIT

# Entry point script for QGIS testing container

set -e

# Start Xvfb for headless display
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Wait for Xvfb to be ready
sleep 2

# Install any additional Python dependencies
if [ -f /tests_directory/requirements-dev.txt ]; then
    pip install -r /tests_directory/requirements-dev.txt
fi

# Execute the command passed to docker
exec "$@"
