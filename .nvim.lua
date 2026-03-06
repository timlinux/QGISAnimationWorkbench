-- SPDX-FileCopyrightText: Tim Sutton
-- SPDX-License-Identifier: MIT
--
-- QGIS Animation Workbench - Neovim Project Configuration
-- This file contains project-specific settings for LSP, formatting, etc.

local M = {}

-- ============================================================================
-- PYTHONPATH Configuration for QGIS
-- ============================================================================

-- Detect QGIS installation path from nix environment
local function get_qgis_python_path()
  local handle = io.popen("which qgis 2>/dev/null")
  if handle then
    local qgis_bin = handle:read("*a"):gsub("%s+$", "")
    handle:close()
    if qgis_bin ~= "" then
      -- Extract nix store path: /nix/store/xxx-qgis-xxx/bin/qgis -> /nix/store/xxx-qgis-xxx
      local qgis_prefix = qgis_bin:match("(.+)/bin/qgis")
      if qgis_prefix then
        return qgis_prefix .. "/share/qgis/python"
      end
    end
  end
  return nil
end

-- Get virtualenv site-packages path
local function get_venv_path()
  local cwd = vim.fn.getcwd()
  local venv_path = cwd .. "/.venv/lib"
  -- Find python version directory
  local handle = io.popen("ls " .. venv_path .. " 2>/dev/null | head -1")
  if handle then
    local python_ver = handle:read("*a"):gsub("%s+$", "")
    handle:close()
    if python_ver ~= "" then
      return venv_path .. "/" .. python_ver .. "/site-packages"
    end
  end
  return nil
end

-- ============================================================================
-- LSP Configuration
-- ============================================================================

M.setup_lsp = function()
  local lspconfig_ok, lspconfig = pcall(require, "lspconfig")
  if not lspconfig_ok then
    return
  end

  -- Build extra paths for pyright
  local extra_paths = {}

  local qgis_path = get_qgis_python_path()
  if qgis_path then
    table.insert(extra_paths, qgis_path)
    table.insert(extra_paths, qgis_path .. "/plugins")
  end

  local venv_path = get_venv_path()
  if venv_path then
    table.insert(extra_paths, venv_path)
  end

  -- Add project root for imports
  table.insert(extra_paths, vim.fn.getcwd())

  -- Configure pyright with QGIS paths
  lspconfig.pyright.setup({
    settings = {
      python = {
        analysis = {
          extraPaths = extra_paths,
          typeCheckingMode = "basic",
          autoSearchPaths = true,
          useLibraryCodeForTypes = true,
          diagnosticMode = "workspace",
          -- Ignore some errors common in QGIS plugins
          diagnosticSeverityOverrides = {
            reportMissingImports = "warning",
            reportMissingModuleSource = "none",
            reportOptionalMemberAccess = "information",
          },
        },
        pythonPath = vim.fn.getcwd() .. "/.venv/bin/python",
      },
    },
    on_attach = function(client, bufnr)
      -- Enable completion triggered by <c-x><c-o>
      vim.bo[bufnr].omnifunc = "v:lua.vim.lsp.omnifunc"

      -- Buffer local mappings
      local opts = { buffer = bufnr }
      vim.keymap.set("n", "gD", vim.lsp.buf.declaration, opts)
      vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
      vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
      vim.keymap.set("n", "gi", vim.lsp.buf.implementation, opts)
      vim.keymap.set("n", "<C-k>", vim.lsp.buf.signature_help, opts)
      vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
      vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
      vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
    end,
  })
end

-- ============================================================================
-- Formatting Configuration (conform.nvim)
-- ============================================================================

M.setup_formatting = function()
  local conform_ok, conform = pcall(require, "conform")
  if not conform_ok then
    return
  end

  conform.setup({
    formatters_by_ft = {
      python = { "isort", "black" },
      lua = { "stylua" },
      nix = { "nixfmt" },
      yaml = { "yamlfmt" },
      json = { "jq" },
      markdown = { "markdownlint" },
      sh = { "shfmt" },
      bash = { "shfmt" },
    },
    formatters = {
      black = {
        prepend_args = { "--line-length", "120" },
      },
      isort = {
        prepend_args = { "--profile", "black", "--line-length", "120" },
      },
      shfmt = {
        prepend_args = { "-i", "2", "-ci" },
      },
    },
    format_on_save = {
      timeout_ms = 3000,
      lsp_fallback = true,
    },
  })

  -- Format command
  vim.api.nvim_create_user_command("Format", function()
    conform.format({ async = true, lsp_fallback = true })
  end, { desc = "Format current buffer" })
end

-- ============================================================================
-- Linting Configuration (nvim-lint)
-- ============================================================================

M.setup_linting = function()
  local lint_ok, lint = pcall(require, "lint")
  if not lint_ok then
    return
  end

  lint.linters_by_ft = {
    python = { "flake8", "mypy" },
    yaml = { "yamllint" },
    markdown = { "markdownlint" },
    sh = { "shellcheck" },
    bash = { "shellcheck" },
    dockerfile = { "hadolint" },
  }

  -- Configure flake8 to match pyproject.toml
  lint.linters.flake8.args = {
    "--max-line-length=120",
    "--extend-ignore=E501,W503,E203",
    "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
  }

  -- Auto-lint on save and insert leave
  vim.api.nvim_create_autocmd({ "BufWritePost", "InsertLeave" }, {
    callback = function()
      lint.try_lint()
    end,
  })
end

-- ============================================================================
-- DAP (Debug Adapter Protocol) Configuration
-- ============================================================================

M.setup_dap = function()
  local dap_ok, dap = pcall(require, "dap")
  if not dap_ok then
    return
  end

  -- Python debugpy configuration
  dap.adapters.python = {
    type = "executable",
    command = vim.fn.getcwd() .. "/.venv/bin/python",
    args = { "-m", "debugpy.adapter" },
  }

  dap.configurations.python = {
    {
      type = "python",
      request = "launch",
      name = "Launch file",
      program = "${file}",
      pythonPath = function()
        return vim.fn.getcwd() .. "/.venv/bin/python"
      end,
    },
    {
      type = "python",
      request = "attach",
      name = "Attach to QGIS (debugpy)",
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
  }
end

-- ============================================================================
-- Project-specific settings
-- ============================================================================

M.setup_project = function()
  -- Set Python 3 as the provider
  vim.g.python3_host_prog = vim.fn.getcwd() .. "/.venv/bin/python"

  -- File type associations
  vim.filetype.add({
    extension = {
      qml = "xml", -- QGIS QML style files
      ui = "xml",  -- Qt UI files
    },
    pattern = {
      ["metadata.txt"] = "ini",
    },
  })

  -- Project-specific settings
  vim.opt_local.tabstop = 4
  vim.opt_local.shiftwidth = 4
  vim.opt_local.expandtab = true
  vim.opt_local.textwidth = 120
  vim.opt_local.colorcolumn = "120"

  -- Spell checking for documentation
  vim.api.nvim_create_autocmd("FileType", {
    pattern = { "markdown", "rst", "text" },
    callback = function()
      vim.opt_local.spell = true
      vim.opt_local.spelllang = "en_us"
    end,
  })
end

-- ============================================================================
-- Telescope project-specific pickers
-- ============================================================================

M.setup_telescope = function()
  local telescope_ok, telescope = pcall(require, "telescope.builtin")
  if not telescope_ok then
    return
  end

  -- Custom picker for plugin files only
  vim.api.nvim_create_user_command("PluginFiles", function()
    telescope.find_files({
      cwd = vim.fn.getcwd() .. "/animation_workbench",
      prompt_title = "Plugin Files",
    })
  end, { desc = "Find files in plugin directory" })

  -- Custom picker for test files
  vim.api.nvim_create_user_command("TestFiles", function()
    telescope.find_files({
      cwd = vim.fn.getcwd() .. "/animation_workbench/test",
      prompt_title = "Test Files",
    })
  end, { desc = "Find test files" })

  -- Search in plugin code only
  vim.api.nvim_create_user_command("PluginGrep", function()
    telescope.live_grep({
      cwd = vim.fn.getcwd() .. "/animation_workbench",
      prompt_title = "Search Plugin Code",
    })
  end, { desc = "Search in plugin code" })
end

-- ============================================================================
-- Initialize all configurations
-- ============================================================================

M.setup = function()
  M.setup_project()
  M.setup_lsp()
  M.setup_formatting()
  M.setup_linting()
  M.setup_dap()
  M.setup_telescope()

  -- Notify user
  vim.notify("Animation Workbench project config loaded", vim.log.levels.INFO)
end

-- Auto-setup when this file is sourced
M.setup()

return M
