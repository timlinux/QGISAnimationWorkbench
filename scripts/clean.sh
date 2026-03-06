#!/usr/bin/env bash

# Run precommit checks
#
RESET='\033[0m'
ORANGE='\033[38;2;237;177;72m'
# Clear screen and show welcome banner
clear
echo -e "$RESET$ORANGE"
if [ -f animation_workbench/resources/animation-workbench-sketched.png ]; then
    chafa animation_workbench/resources/animation-workbench-sketched.png --size=30x80 --colors=256 | sed 's/^/                  /'
fi
# Quick tips with icons
echo -e "$RESET$ORANGE \n__________________________________________________________________\n"
echo "Removing pycaches, .venv etc ..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".venv" -exec rm -rf {} +
echo "Removing core dumps and other unneeded files ..."
find . -type f -name "core.*" -exec rm -f {} +
find . -type f -name "*.log" -exec rm -f {} +
find . -type f -name "*.tmp" -exec rm -f {} +
echo -e "$RESET$ORANGE \n__________________________________________________________________\n"
