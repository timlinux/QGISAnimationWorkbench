" SPDX-FileCopyrightText: Tim Sutton
" SPDX-License-Identifier: MIT
"
" QGIS Animation Workbench - Neovim Project Configuration
" All shortcuts are under <leader>p (project commands)
"
" Usage: This file is automatically loaded by neovim when you open a file
" in this project directory (requires 'exrc' option enabled).

" Ensure we're in a safe environment
if !exists('g:loaded_animation_workbench_exrc')
  let g:loaded_animation_workbench_exrc = 1

  " ============================================================================
  " Which-key setup for project commands under <leader>p
  " ============================================================================

  " Check if which-key is available
  lua << EOF
  local ok, wk = pcall(require, "which-key")
  if ok then
    wk.add({
      { "<leader>p", group = "Project (Animation Workbench)" },

      -- Running QGIS
      { "<leader>pq", group = "QGIS" },
      { "<leader>pqs", "<cmd>!./scripts/start_qgis.sh &<cr>", desc = "Start QGIS (stable)" },
      { "<leader>pql", "<cmd>!./scripts/start_qgis_ltr.sh &<cr>", desc = "Start QGIS LTR" },
      { "<leader>pqm", "<cmd>!./scripts/start_qgis_master.sh &<cr>", desc = "Start QGIS master" },

      -- Testing
      { "<leader>pt", group = "Test" },
      { "<leader>ptt", "<cmd>!pytest animation_workbench/test/ -v<cr>", desc = "Run all tests" },
      { "<leader>ptf", "<cmd>!pytest % -v<cr>", desc = "Run tests in current file" },
      { "<leader>ptl", "<cmd>!pytest --lf -v<cr>", desc = "Re-run last failed tests" },
      { "<leader>ptc", "<cmd>!pytest --cov=animation_workbench --cov-report=html<cr>", desc = "Run with coverage" },

      -- Code Quality
      { "<leader>pc", group = "Code Quality" },
      { "<leader>pcc", "<cmd>!./scripts/checks.sh<cr>", desc = "Run all pre-commit checks" },
      { "<leader>pcf", "<cmd>!black % && isort %<cr>", desc = "Format current file" },
      { "<leader>pca", "<cmd>!black . && isort .<cr>", desc = "Format all files" },
      { "<leader>pcl", "<cmd>!flake8 %<cr>", desc = "Lint current file" },
      { "<leader>pcs", "<cmd>!bandit -r animation_workbench -c pyproject.toml<cr>", desc = "Security scan" },
      { "<leader>pct", "<cmd>!pyright %<cr>", desc = "Type check current file" },
      { "<leader>pcT", "<cmd>!pyright animation_workbench<cr>", desc = "Type check all" },

      -- Documentation
      { "<leader>pd", group = "Documentation" },
      { "<leader>pds", "<cmd>!mkdocs serve &<cr>", desc = "Serve docs locally" },
      { "<leader>pdb", "<cmd>!mkdocs build<cr>", desc = "Build docs" },
      { "<leader>pdo", "<cmd>!xdg-open http://localhost:8000<cr>", desc = "Open docs in browser" },

      -- Debugging
      { "<leader>px", group = "Debug" },
      { "<leader>pxb", function() require('dap').toggle_breakpoint() end, desc = "Toggle breakpoint" },
      { "<leader>pxc", function() require('dap').continue() end, desc = "Continue" },
      { "<leader>pxs", function() require('dap').step_over() end, desc = "Step over" },
      { "<leader>pxi", function() require('dap').step_into() end, desc = "Step into" },
      { "<leader>pxo", function() require('dap').step_out() end, desc = "Step out" },
      { "<leader>pxr", function() require('dap').repl.open() end, desc = "Open REPL" },

      -- Utilities
      { "<leader>pu", group = "Utilities" },
      { "<leader>puc", "<cmd>!./scripts/clean.sh<cr>", desc = "Clean workspace" },
      { "<leader>pui", "<cmd>!pip install -r requirements-dev.txt<cr>", desc = "Install dependencies" },
      { "<leader>pup", "<cmd>!pre-commit install<cr>", desc = "Install pre-commit hooks" },
      { "<leader>pus", "<cmd>!./scripts/update-strings.sh<cr>", desc = "Update translation strings" },
      { "<leader>put", "<cmd>!./scripts/compile-strings.sh<cr>", desc = "Compile translations" },

      -- Git shortcuts
      { "<leader>pg", group = "Git" },
      { "<leader>pgs", "<cmd>Git status<cr>", desc = "Git status" },
      { "<leader>pgd", "<cmd>Git diff<cr>", desc = "Git diff" },
      { "<leader>pgb", "<cmd>Git blame<cr>", desc = "Git blame" },
      { "<leader>pgl", "<cmd>Git log --oneline -20<cr>", desc = "Git log" },

      -- Plugin packaging
      { "<leader>pp", group = "Package" },
      { "<leader>ppb", "<cmd>!cd animation_workbench && zip -r ../animation_workbench.zip . -x '*.pyc' -x '__pycache__/*' -x 'test/*'<cr>", desc = "Build plugin zip" },

      -- Profiling
      { "<leader>pr", group = "Profile" },
      { "<leader>prp", "<cmd>!python -m cProfile -o profile.prof %<cr>", desc = "Profile current file" },
      { "<leader>prv", "<cmd>!snakeviz profile.prof &<cr>", desc = "View profile (snakeviz)" },
      { "<leader>prk", "<cmd>!pyprof2calltree -i profile.prof -o profile.callgrind && kcachegrind profile.callgrind &<cr>", desc = "View profile (kcachegrind)" },
    })
  else
    -- Fallback mappings without which-key
    vim.keymap.set('n', '<leader>pqs', '<cmd>!./scripts/start_qgis.sh &<cr>', { desc = 'Start QGIS' })
    vim.keymap.set('n', '<leader>ptt', '<cmd>!pytest animation_workbench/test/ -v<cr>', { desc = 'Run tests' })
    vim.keymap.set('n', '<leader>pcc', '<cmd>!./scripts/checks.sh<cr>', { desc = 'Run checks' })
    vim.keymap.set('n', '<leader>pcf', '<cmd>!black % && isort %<cr>', { desc = 'Format file' })
    vim.keymap.set('n', '<leader>pds', '<cmd>!mkdocs serve &<cr>', { desc = 'Serve docs' })
  end
EOF

endif
