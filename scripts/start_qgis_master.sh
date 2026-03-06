#!/usr/bin/env bash
echo "Running QGIS Master with the AnimationWorkbench profile:"
echo "--------------------------------"
echo "Do you want to enable debug mode?"
choice=$(gum choose "Yes" "No")
case $choice in
    "Yes") developer_mode=1 ;;
    "No") developer_mode=0 ;;
esac

# Running on local used to skip tests that will not work in a local dev env
ANIMATION_WORKBENCH_LOG=$HOME/AnimationWorkbench.log
ANIMATION_WORKBENCH_TEST_DIR="$(pwd)/test" # Set test directory relative to project root
rm -f "$ANIMATION_WORKBENCH_LOG"

# This is the new way, using Ivan Mincis nix spatial project and a flake
# see flake.nix for implementation details
ANIMATION_WORKBENCH_LOG=${ANIMATION_WORKBENCH_LOG} \
    ANIMATION_WORKBENCH_DEBUG=${developer_mode} \
    ANIMATION_WORKBENCH_TEST_DIR=${ANIMATION_WORKBENCH_TEST_DIR} \
    RUNNING_ON_LOCAL=1 \
    nix run .#qgis-master -- --profile AnimationWorkbench
