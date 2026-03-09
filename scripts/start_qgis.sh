#!/usr/bin/env bash

# SPDX-FileCopyrightText: Tim Sutton
# SPDX-License-Identifier: MIT

echo "Running QGIS with the AnimationWorkbench profile:"
echo "--------------------------------"

echo "Select run mode:"
choice=$(gum choose "Normal" "Debug Mode" "With Crash Handler (gdb)" "With Crash Handler (catchsegv)")

developer_mode=0
use_gdb=0
use_catchsegv=0

case $choice in
    "Debug Mode")
        developer_mode=1
        ;;
    "With Crash Handler (gdb)")
        use_gdb=1
        ;;
    "With Crash Handler (catchsegv)")
        use_catchsegv=1
        ;;
esac

# Running on local used to skip tests that will not work in a local dev env
ANIMATION_WORKBENCH_LOG=$HOME/AnimationWorkbench.log
ANIMATION_WORKBENCH_TEST_DIR="$(pwd)/test"
CRASH_LOG="$HOME/qgis_crash_$(date +%Y%m%d_%H%M%S).log"
rm -f "$ANIMATION_WORKBENCH_LOG"

# Enable core dumps
ulimit -c unlimited 2>/dev/null

# Get the QGIS package path
QGIS_PKG=$(nix build .#qgis --print-out-paths 2>/dev/null)
QGIS_WRAPPER="$QGIS_PKG/bin/qgis"
QGIS_REAL="$QGIS_PKG/bin/.qgis-wrapped_"

export ANIMATION_WORKBENCH_LOG=${ANIMATION_WORKBENCH_LOG}
export ANIMATION_WORKBENCH_DEBUG=${developer_mode}
export ANIMATION_WORKBENCH_TEST_DIR=${ANIMATION_WORKBENCH_TEST_DIR}
export RUNNING_ON_LOCAL=1

if [[ $use_gdb -eq 1 ]]; then
    echo "Running with gdb - stack trace will be captured on crash"
    echo "Crash log will be saved to: $CRASH_LOG"

    # Source environment from wrapper and run gdb on real binary
    # Extract PYTHONPATH and PATH setup from wrapper
    eval "$(grep -E '^(export |PATH=|PYTHONPATH=)' "$QGIS_WRAPPER" | grep -v 'exec')"

    if [[ -x "$QGIS_REAL" ]]; then
        gdb -batch \
            -ex "set pagination off" \
            -ex "run --profile AnimationWorkbench" \
            -ex "bt full" \
            -ex "info registers" \
            -ex "quit" \
            "$QGIS_REAL" 2>&1 | tee "$CRASH_LOG"
        exit_code=${PIPESTATUS[0]}
    else
        echo "Error: Real QGIS binary not found at $QGIS_REAL"
        echo "Falling back to catchsegv..."
        use_catchsegv=1
        use_gdb=0
    fi
fi

if [[ $use_catchsegv -eq 1 ]]; then
    echo "Running with catchsegv - stack trace will be captured on crash"
    echo "Crash log will be saved to: $CRASH_LOG"
    catchsegv "$QGIS_WRAPPER" --profile AnimationWorkbench 2>&1 | tee "$CRASH_LOG"
    exit_code=${PIPESTATUS[0]}
fi

if [[ $use_gdb -eq 0 ]] && [[ $use_catchsegv -eq 0 ]]; then
    # Normal run via nix
    nix run .#default -- --profile AnimationWorkbench
    exit_code=$?
fi

# Check if crashed
if [[ $exit_code -eq 139 ]] || [[ $exit_code -eq 134 ]] || [[ $exit_code -eq 136 ]] || [[ $exit_code -eq 11 ]]; then
    echo ""
    echo "========================================"
    echo "QGIS crashed with exit code: $exit_code"
    echo "========================================"
    if [[ -f "$CRASH_LOG" ]]; then
        echo "Crash log saved to: $CRASH_LOG"
        echo ""
        echo "Last 50 lines of crash log:"
        echo "----------------------------------------"
        tail -50 "$CRASH_LOG"
    else
        echo "To get a stack trace, run this script again and select 'With Crash Handler'"
    fi
fi
