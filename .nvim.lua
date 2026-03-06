-- SPDX-FileCopyrightText: Tim Sutton
-- SPDX-License-Identifier: MIT
--
-- QGIS Animation Workbench - Neovim Project Configuration
-- All project keybindings are under <leader>p
--
-- This file is auto-loaded by neovim with exrc enabled or via neoconf/nvim-config-local

local M = {}

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Run a command in a new terminal split
local function run_in_terminal(cmd, opts)
  opts = opts or {}
  local direction = opts.direction or "horizontal"
  local size = opts.size or 15

  if direction == "horizontal" then
    vim.cmd("botright " .. size .. "split | terminal " .. cmd)
  elseif direction == "vertical" then
    vim.cmd("vertical " .. size .. "split | terminal " .. cmd)
  elseif direction == "float" then
    vim.cmd("terminal " .. cmd)
  end

  -- Enter insert mode in terminal
  vim.cmd("startinsert")
end

-- Run a command in background (no terminal output)
local function run_background(cmd)
  vim.fn.jobstart(cmd, { detach = true })
  vim.notify("Started: " .. cmd, vim.log.levels.INFO)
end

-- ============================================================================
-- Which-Key Registration
-- ============================================================================

M.setup_keymaps = function()
  local ok, wk = pcall(require, "which-key")
  if not ok then
    vim.notify("which-key not found, using basic keymaps", vim.log.levels.WARN)
    M.setup_basic_keymaps()
    return
  end

  wk.add({
    { "<leader>p", group = "Project (Animation Workbench)" },

    -- ========================================================================
    -- QGIS
    -- ========================================================================
    { "<leader>pq", group = "QGIS" },
    {
      "<leader>pqs",
      function()
        run_background("ANIMATION_WORKBENCH_DEBUG=0 nix run .#qgis --impure")
      end,
      desc = "QGIS Stable",
    },
    {
      "<leader>pqd",
      function()
        run_in_terminal(
          "ANIMATION_WORKBENCH_DEBUG=1 ANIMATION_WORKBENCH_LOG=$HOME/AnimationWorkbench.log nix run .#qgis --impure",
          { direction = "horizontal", size = 20 }
        )
      end,
      desc = "QGIS Stable (Debug)",
    },
    {
      "<leader>pql",
      function()
        run_background("ANIMATION_WORKBENCH_DEBUG=0 nix run .#qgis-ltr --impure")
      end,
      desc = "QGIS LTR",
    },
    {
      "<leader>pqL",
      function()
        run_in_terminal(
          "ANIMATION_WORKBENCH_DEBUG=1 ANIMATION_WORKBENCH_LOG=$HOME/AnimationWorkbench.log nix run .#qgis-ltr --impure",
          { direction = "horizontal", size = 20 }
        )
      end,
      desc = "QGIS LTR (Debug)",
    },
    {
      "<leader>pqm",
      function()
        run_background("ANIMATION_WORKBENCH_DEBUG=0 nix run .#qgis-master --impure")
      end,
      desc = "QGIS Master",
    },
    {
      "<leader>pqM",
      function()
        run_in_terminal(
          "ANIMATION_WORKBENCH_DEBUG=1 ANIMATION_WORKBENCH_LOG=$HOME/AnimationWorkbench.log nix run .#qgis-master --impure",
          { direction = "horizontal", size = 20 }
        )
      end,
      desc = "QGIS Master (Debug)",
    },
    {
      "<leader>pqo",
      function()
        vim.cmd("edit $HOME/AnimationWorkbench.log")
      end,
      desc = "Open debug log",
    },

    -- ========================================================================
    -- Testing
    -- ========================================================================
    { "<leader>pt", group = "Test" },
    {
      "<leader>ptt",
      function()
        run_in_terminal("nix run .#test", { size = 20 })
      end,
      desc = "Run all tests",
    },
    {
      "<leader>ptf",
      function()
        local file = vim.fn.expand("%")
        run_in_terminal("pytest " .. file .. " -v", { size = 20 })
      end,
      desc = "Test current file",
    },
    {
      "<leader>ptl",
      function()
        run_in_terminal("pytest --lf -v", { size = 20 })
      end,
      desc = "Re-run last failed",
    },
    {
      "<leader>ptc",
      function()
        run_in_terminal("pytest --cov=animation_workbench --cov-report=html && xdg-open htmlcov/index.html", { size = 20 })
      end,
      desc = "Run with coverage",
    },

    -- ========================================================================
    -- Code Quality
    -- ========================================================================
    { "<leader>pc", group = "Code Quality" },
    {
      "<leader>pcc",
      function()
        run_in_terminal("nix run .#checks", { size = 25 })
      end,
      desc = "Pre-commit checks (all)",
    },
    {
      "<leader>pcf",
      function()
        run_in_terminal("nix run .#format", { size = 15 })
      end,
      desc = "Format all (black + isort)",
    },
    {
      "<leader>pcF",
      function()
        local file = vim.fn.expand("%")
        run_in_terminal("black " .. file .. " && isort " .. file, { size = 10 })
      end,
      desc = "Format current file",
    },
    {
      "<leader>pcl",
      function()
        run_in_terminal("nix run .#lint", { size = 20 })
      end,
      desc = "Lint all (flake8 + pyright)",
    },
    {
      "<leader>pcL",
      function()
        local file = vim.fn.expand("%")
        run_in_terminal("flake8 " .. file .. " && pyright " .. file, { size = 15 })
      end,
      desc = "Lint current file",
    },
    {
      "<leader>pcs",
      function()
        run_in_terminal("nix run .#security", { size = 20 })
      end,
      desc = "Security scan (bandit)",
    },

    -- ========================================================================
    -- Documentation
    -- ========================================================================
    { "<leader>pd", group = "Documentation" },
    {
      "<leader>pds",
      function()
        run_in_terminal("nix run .#docs-serve", { size = 10 })
      end,
      desc = "Serve docs locally",
    },
    {
      "<leader>pdb",
      function()
        run_in_terminal("nix run .#docs-build", { size = 15 })
      end,
      desc = "Build docs",
    },
    {
      "<leader>pdo",
      function()
        run_background("xdg-open http://localhost:8000")
      end,
      desc = "Open docs in browser",
    },

    -- ========================================================================
    -- Debugging (DAP)
    -- ========================================================================
    { "<leader>px", group = "Debug (DAP)" },
    {
      "<leader>pxb",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.toggle_breakpoint()
        else
          vim.notify("DAP not available", vim.log.levels.WARN)
        end
      end,
      desc = "Toggle breakpoint",
    },
    {
      "<leader>pxc",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.continue()
        end
      end,
      desc = "Continue",
    },
    {
      "<leader>pxs",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.step_over()
        end
      end,
      desc = "Step over",
    },
    {
      "<leader>pxi",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.step_into()
        end
      end,
      desc = "Step into",
    },
    {
      "<leader>pxo",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.step_out()
        end
      end,
      desc = "Step out",
    },
    {
      "<leader>pxr",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.repl.open()
        end
      end,
      desc = "Open REPL",
    },
    {
      "<leader>pxa",
      function()
        local dap_ok, dap = pcall(require, "dap")
        if dap_ok then
          dap.run({
            type = "python",
            request = "attach",
            name = "Attach to QGIS",
            connect = { host = "127.0.0.1", port = 5678 },
            pathMappings = {
              {
                localRoot = vim.fn.getcwd() .. "/animation_workbench",
                remoteRoot = vim.fn.expand("~/.local/share/QGIS/QGIS3/profiles/AnimationWorkbench/python/plugins/animation_workbench"),
              },
            },
          })
        end
      end,
      desc = "Attach to QGIS (debugpy)",
    },

    -- ========================================================================
    -- Packaging
    -- ========================================================================
    { "<leader>pp", group = "Package" },
    {
      "<leader>ppb",
      function()
        run_in_terminal("nix run .#package", { size = 10 })
      end,
      desc = "Build plugin zip",
    },
    {
      "<leader>pps",
      function()
        run_in_terminal("nix run .#symlink", { size = 12 })
      end,
      desc = "Symlink plugin to QGIS profile",
    },
    {
      "<leader>ppi",
      function()
        local plugin_dir = vim.fn.expand("~/.local/share/QGIS/QGIS3/profiles/AnimationWorkbench/python/plugins/")
        run_in_terminal("mkdir -p " .. plugin_dir .. " && cp -r animation_workbench " .. plugin_dir, { size = 10 })
      end,
      desc = "Install (copy) to QGIS profile",
    },

    -- ========================================================================
    -- Profiling
    -- ========================================================================
    { "<leader>pr", group = "Profile" },
    {
      "<leader>prp",
      function()
        local file = vim.fn.expand("%")
        run_in_terminal("python -m cProfile -o profile.prof " .. file, { size = 15 })
      end,
      desc = "Profile current file",
    },
    {
      "<leader>prv",
      function()
        run_in_terminal("nix run .#profile", { size = 10 })
      end,
      desc = "View profile (snakeviz)",
    },

    -- ========================================================================
    -- Utilities
    -- ========================================================================
    { "<leader>pu", group = "Utilities" },
    {
      "<leader>puc",
      function()
        run_in_terminal("nix run .#clean", { size = 10 })
      end,
      desc = "Clean workspace",
    },
    {
      "<leader>pui",
      function()
        run_in_terminal("pip install -r requirements-dev.txt", { size = 15 })
      end,
      desc = "Install pip deps",
    },
    {
      "<leader>puh",
      function()
        run_in_terminal("pre-commit install", { size = 10 })
      end,
      desc = "Install pre-commit hooks",
    },
    {
      "<leader>pus",
      function()
        run_in_terminal("./scripts/update-strings.sh", { size = 10 })
      end,
      desc = "Update translation strings",
    },
    {
      "<leader>put",
      function()
        run_in_terminal("./scripts/compile-strings.sh", { size = 10 })
      end,
      desc = "Compile translations",
    },
    {
      "<leader>pun",
      function()
        run_in_terminal("nix flake show", { size = 20 })
      end,
      desc = "Show nix flake",
    },
    {
      "<leader>pue",
      function()
        vim.cmd("edit flake.nix")
      end,
      desc = "Edit flake.nix",
    },

    -- ========================================================================
    -- Git
    -- ========================================================================
    { "<leader>pg", group = "Git" },
    {
      "<leader>pgs",
      "<cmd>Git status<cr>",
      desc = "Git status",
    },
    {
      "<leader>pgd",
      "<cmd>Git diff<cr>",
      desc = "Git diff",
    },
    {
      "<leader>pgb",
      "<cmd>Git blame<cr>",
      desc = "Git blame",
    },
    {
      "<leader>pgl",
      "<cmd>Git log --oneline -20<cr>",
      desc = "Git log (20)",
    },
    {
      "<leader>pgp",
      function()
        run_in_terminal("git push", { size = 10 })
      end,
      desc = "Git push",
    },
  })

  vim.notify("Animation Workbench keymaps loaded (<leader>p)", vim.log.levels.INFO)
end

-- ============================================================================
-- Basic Keymaps (fallback without which-key)
-- ============================================================================

M.setup_basic_keymaps = function()
  local opts = { noremap = true, silent = true }

  -- QGIS
  vim.keymap.set("n", "<leader>pqs", function()
    run_background("nix run .#qgis --impure")
  end, vim.tbl_extend("force", opts, { desc = "QGIS Stable" }))

  vim.keymap.set("n", "<leader>pqd", function()
    run_in_terminal("ANIMATION_WORKBENCH_DEBUG=1 nix run .#qgis --impure", { size = 20 })
  end, vim.tbl_extend("force", opts, { desc = "QGIS Debug" }))

  -- Testing
  vim.keymap.set("n", "<leader>ptt", function()
    run_in_terminal("nix run .#test", { size = 20 })
  end, vim.tbl_extend("force", opts, { desc = "Run tests" }))

  -- Code Quality
  vim.keymap.set("n", "<leader>pcc", function()
    run_in_terminal("nix run .#checks", { size = 25 })
  end, vim.tbl_extend("force", opts, { desc = "Pre-commit checks" }))

  vim.keymap.set("n", "<leader>pcf", function()
    run_in_terminal("nix run .#format", { size = 15 })
  end, vim.tbl_extend("force", opts, { desc = "Format code" }))

  -- Docs
  vim.keymap.set("n", "<leader>pds", function()
    run_in_terminal("nix run .#docs-serve", { size = 10 })
  end, vim.tbl_extend("force", opts, { desc = "Serve docs" }))
end

-- ============================================================================
-- LSP Configuration
-- ============================================================================

M.setup_lsp = function()
  local lspconfig_ok, lspconfig = pcall(require, "lspconfig")
  if not lspconfig_ok then
    return
  end

  -- Configure pyright for QGIS development
  lspconfig.pyright.setup({
    settings = {
      python = {
        analysis = {
          extraPaths = {
            vim.fn.getcwd(),
            vim.fn.getcwd() .. "/animation_workbench",
          },
          typeCheckingMode = "basic",
          autoSearchPaths = true,
          useLibraryCodeForTypes = true,
          diagnosticSeverityOverrides = {
            reportMissingImports = "warning",
            reportMissingModuleSource = "none",
          },
        },
      },
    },
  })
end

-- ============================================================================
-- DAP Configuration for QGIS debugging
-- ============================================================================

M.setup_dap = function()
  local dap_ok, dap = pcall(require, "dap")
  if not dap_ok then
    return
  end

  dap.adapters.python = {
    type = "executable",
    command = "python",
    args = { "-m", "debugpy.adapter" },
  }

  dap.configurations.python = {
    {
      type = "python",
      request = "attach",
      name = "Attach to QGIS (debugpy on 5678)",
      connect = {
        host = "127.0.0.1",
        port = 5678,
      },
      pathMappings = {
        {
          localRoot = vim.fn.getcwd() .. "/animation_workbench",
          remoteRoot = vim.fn.expand("~/.local/share/QGIS/QGIS3/profiles/AnimationWorkbench/python/plugins/animation_workbench"),
        },
      },
    },
    {
      type = "python",
      request = "launch",
      name = "Launch file",
      program = "${file}",
    },
  }
end

-- ============================================================================
-- Project Settings
-- ============================================================================

M.setup_project = function()
  -- Python settings
  vim.opt_local.tabstop = 4
  vim.opt_local.shiftwidth = 4
  vim.opt_local.expandtab = true
  vim.opt_local.textwidth = 120
  vim.opt_local.colorcolumn = "120"

  -- File type associations
  vim.filetype.add({
    extension = {
      qml = "xml",
      ui = "xml",
    },
    pattern = {
      ["metadata.txt"] = "ini",
    },
  })
end

-- ============================================================================
-- Initialize
-- ============================================================================

M.setup = function()
  M.setup_project()
  M.setup_keymaps()
  M.setup_lsp()
  M.setup_dap()
end

-- Auto-setup
M.setup()

return M
