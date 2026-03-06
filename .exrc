" SPDX-FileCopyrightText: Tim Sutton
" SPDX-License-Identifier: MIT
"
" QGIS Animation Workbench - Neovim Project Configuration
"
" This file loads .nvim.lua which contains all project keybindings
" All shortcuts are under <leader>p (project commands)
"
" Usage: Requires 'exrc' option enabled in neovim:
"   vim.opt.exrc = true
"
" Project Keybindings (<leader>p):
"   q - QGIS (stable/LTR/master, debug/standard)
"   t - Testing
"   c - Code Quality (format, lint, checks)
"   d - Documentation
"   x - Debug (DAP breakpoints, attach to QGIS)
"   p - Packaging (build zip, symlink to profile, copy install)
"   r - Profiling
"   u - Utilities
"   g - Git

" Load .nvim.lua if it exists and hasn't been loaded
if !exists('g:loaded_animation_workbench_project')
  let g:loaded_animation_workbench_project = 1

  " Source the Lua configuration
  if filereadable(expand('<sfile>:p:h') . '/.nvim.lua')
    lua dofile(vim.fn.expand('<sfile>:p:h') .. '/.nvim.lua')
  endif
endif
