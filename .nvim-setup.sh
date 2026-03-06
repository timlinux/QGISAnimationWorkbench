#!/usr/bin/env bash

# SPDX-FileCopyrightText: Tim Sutton
# SPDX-License-Identifier: MIT

# This script sets up the environment for Neovim/LSP to work with QGIS Python libraries
# Source this script before running nvim: source .nvim-setup.sh
#
# Project keybindings are under <leader>p - run :WhichKey <leader>p in neovim

# Colors
CYAN='\033[38;2;83;161;203m'
GREEN='\033[92m'
ORANGE='\033[38;2;237;177;72m'
RESET='\033[0m'

QGIS_BIN=$(which qgis 2>/dev/null)

if [[ -z "$QGIS_BIN" ]]; then
    echo -e "${ORANGE}Warning: QGIS binary not found in PATH${RESET}"
    echo "Make sure you're in the nix develop shell first"
    return 1 2>/dev/null || exit 1
fi

# Extract the Nix store path (removing /bin/qgis)
QGIS_PREFIX=$(dirname "$(dirname "$QGIS_BIN")")

# Construct the correct QGIS Python path
QGIS_PYTHON_PATH="$QGIS_PREFIX/share/qgis/python"

# Check if the Python directory exists
if [[ ! -d "$QGIS_PYTHON_PATH" ]]; then
    echo -e "${ORANGE}Warning: QGIS Python path not found at $QGIS_PYTHON_PATH${RESET}"
    return 1 2>/dev/null || exit 1
fi

# Add virtualenv if it exists
VENV_PATH=""
if [[ -d ".venv" ]]; then
    VENV_PATH=$(find .venv/lib -maxdepth 1 -name "python*" -type d | head -1)/site-packages
fi

export PYTHONPATH="$QGIS_PYTHON_PATH:$VENV_PATH:$PYTHONPATH"

echo -e "${GREEN}Neovim environment configured for QGIS development${RESET}"
echo ""
echo -e "QGIS Python: ${CYAN}$QGIS_PYTHON_PATH${RESET}"
if [[ -n "$VENV_PATH" ]]; then
    echo -e "Virtualenv:  ${CYAN}$VENV_PATH${RESET}"
fi
echo ""
echo -e "Project keybindings: ${CYAN}<leader>p${RESET}"
echo -e "  ${CYAN}<leader>pq${RESET} - QGIS commands"
echo -e "  ${CYAN}<leader>pt${RESET} - Testing"
echo -e "  ${CYAN}<leader>pc${RESET} - Code quality"
echo -e "  ${CYAN}<leader>pd${RESET} - Documentation"
echo -e "  ${CYAN}<leader>px${RESET} - Debugging"
echo ""
echo -e "Run ${CYAN}:WhichKey <leader>p${RESET} in neovim for full menu"
echo ""
echo -e "${ORANGE}Note:${RESET} Add this to your neovim config to auto-load .nvim.lua:"
echo -e "  ${CYAN}vim.opt.exrc = true${RESET}"
echo -e "  ${CYAN}-- For .nvim.lua: use neoconf.nvim or nvim-config-local plugin${RESET}"
