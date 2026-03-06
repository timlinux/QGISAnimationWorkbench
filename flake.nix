# SPDX-FileCopyrightText: Tim Sutton
# SPDX-License-Identifier: MIT
{
  description = "NixOS developer environment for QGIS Animation Workbench plugin.";
  inputs.qgis-upstream.url = "github:qgis/qgis";
  inputs.geospatial.url = "github:imincik/geospatial-nix.repo";
  inputs.nixpkgs.follows = "geospatial/nixpkgs";

  outputs =
    {
      self,
      qgis-upstream,
      geospatial,
      nixpkgs,
    }:
    let
      system = "x86_64-linux";
      profileName = "AnimationWorkbench";
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
        };
      };

      extraPythonPackages = ps: [
        ps.pyqtwebengine
        ps.debugpy
        ps.psutil
      ];
      qgisWithExtras = geospatial.packages.${system}.qgis.override {
        inherit extraPythonPackages;
      };
      qgisLtrWithExtras = geospatial.packages.${system}.qgis-ltr.override {
        inherit extraPythonPackages;
      };
      qgisMasterWithExtras = qgis-upstream.packages.${system}.qgis.override {
        inherit extraPythonPackages;
      };
    in
    {
      packages.${system} = {
        default = qgisWithExtras;
        qgis = qgisWithExtras;
        qgis-ltr = qgisLtrWithExtras;
        qgis-master = qgisMasterWithExtras;
      };

      apps.${system} = {
        qgis = {
          type = "app";
          program = "${qgisWithExtras}/bin/qgis";
          args = [
            "--profile"
            "${profileName}"
          ];
        };
        qgis-ltr = {
          type = "app";
          program = "${qgisLtrWithExtras}/bin/qgis";
          args = [
            "--profile"
            "${profileName}"
          ];
        };
        qgis-master = {
          type = "app";
          program = "${qgisMasterWithExtras}/bin/qgis";
          args = [
            "--profile"
            "${profileName}"
          ];
        };
        qgis_process = {
          type = "app";
          program = "${qgisWithExtras}/bin/qgis_process";
          args = [
            "--profile"
            "${profileName}"
          ];
        };

        # Development convenience commands
        test = {
          type = "app";
          program = "${pkgs.writeShellScript "run-tests" ''
            cd ${toString ./.}
            source .venv/bin/activate 2>/dev/null || true
            ${pkgs.python3}/bin/python -m pytest animation_workbench/test/ -v "$@"
          ''}";
        };

        format = {
          type = "app";
          program = "${pkgs.writeShellScript "format-code" ''
            cd ${toString ./.}
            echo "Running black..."
            ${pkgs.python3.withPackages (ps: [ ps.black ])}/bin/black .
            echo "Running isort..."
            ${pkgs.isort}/bin/isort .
            echo "Formatting complete!"
          ''}";
        };

        lint = {
          type = "app";
          program = "${pkgs.writeShellScript "lint-code" ''
            cd ${toString ./.}
            echo "Running flake8..."
            source .venv/bin/activate 2>/dev/null || true
            ${pkgs.python3.withPackages (ps: [ ps.flake8 ])}/bin/flake8 animation_workbench/ --max-line-length=120
            echo "Running pyright..."
            ${pkgs.pyright}/bin/pyright animation_workbench/
          ''}";
        };

        checks = {
          type = "app";
          program = "${pkgs.writeShellScript "run-checks" ''
            cd ${toString ./.}
            ./scripts/checks.sh
          ''}";
        };

        docs-serve = {
          type = "app";
          program = "${pkgs.writeShellScript "serve-docs" ''
            cd ${toString ./.}
            source .venv/bin/activate 2>/dev/null || true
            ${pkgs.python3.withPackages (ps: [ ps.mkdocs ps.mkdocs-material ])}/bin/mkdocs serve
          ''}";
        };

        docs-build = {
          type = "app";
          program = "${pkgs.writeShellScript "build-docs" ''
            cd ${toString ./.}
            source .venv/bin/activate 2>/dev/null || true
            ${pkgs.python3.withPackages (ps: [ ps.mkdocs ps.mkdocs-material ])}/bin/mkdocs build
          ''}";
        };

        clean = {
          type = "app";
          program = "${pkgs.writeShellScript "clean-workspace" ''
            cd ${toString ./.}
            ./scripts/clean.sh
          ''}";
        };

        package = {
          type = "app";
          program = "${pkgs.writeShellScript "package-plugin" ''
            cd ${toString ./.}
            echo "Building plugin package..."
            cd animation_workbench
            ${pkgs.zip}/bin/zip -r ../animation_workbench.zip . \
              -x '*.pyc' \
              -x '__pycache__/*' \
              -x 'test/*' \
              -x '.pytest_cache/*'
            cd ..
            echo "Plugin packaged to animation_workbench.zip"
          ''}";
        };

        profile = {
          type = "app";
          program = "${pkgs.writeShellScript "profile-viewer" ''
            if [ -f profile.prof ]; then
              ${pkgs.python3.withPackages (ps: [ ps.snakeviz ])}/bin/snakeviz profile.prof
            else
              echo "No profile.prof found. Run: python -m cProfile -o profile.prof your_script.py"
            fi
          ''}";
        };

        security = {
          type = "app";
          program = "${pkgs.writeShellScript "security-scan" ''
            cd ${toString ./.}
            echo "Running bandit security scanner..."
            ${pkgs.bandit}/bin/bandit -r animation_workbench -c pyproject.toml
          ''}";
        };

      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [

          qgisWithExtras
          pkgs.actionlint # for checking gh actions
          pkgs.bandit
          pkgs.chafa
          pkgs.nixfmt-rfc-style
          pkgs.ffmpeg
          pkgs.gdb
          pkgs.git
          pkgs.glogg
          pkgs.glow # terminal markdown viewer
          pkgs.gource # Software version control visualization
          pkgs.gum # UX for TUIs
          pkgs.isort
          pkgs.jq
          pkgs.libsForQt5.kcachegrind
          pkgs.libsForQt5.qt5.qtpositioning
          pkgs.markdownlint-cli
          pkgs.nixfmt-rfc-style
          pkgs.pre-commit
          pkgs.pyprof2calltree # needed to covert cprofile call trees into a format kcachegrind can read
          pkgs.python3
          # Python development essentials
          pkgs.pyright
          pkgs.qt5.full # so we get designer
          pkgs.qt5.qtbase
          pkgs.qt5.qtlocation
          pkgs.qt5.qtquickcontrols2
          pkgs.qt5.qtsvg
          pkgs.qt5.qttools
          pkgs.rpl
          pkgs.shellcheck
          pkgs.shfmt
          pkgs.vscode
          pkgs.yamlfmt
          pkgs.yamllint
          pkgs.nodePackages.cspell
          (pkgs.python3.withPackages (ps: [
            ps.black
            ps.click # needed by black
            ps.debugpy
            ps.docformatter
            ps.flake8
            ps.gdal
            ps.httpx
            ps.mypy
            ps.numpy
            ps.paver
            ps.pip
            ps.psutil
            ps.pyqt5-stubs
            ps.pytest
            ps.pytest-qt
            ps.python
            ps.rich
            ps.setuptools
            ps.snakeviz # For visualising cprofiler outputs
            ps.toml
            ps.typer
            ps.wheel
            # For autocompletion in vscode
            ps.pyqt5-stubs

            # This executes some shell code to initialize a venv in $venvDir before
            # dropping into the shell
            ps.venvShellHook
            ps.virtualenv
            # Those are dependencies that we would like to use from nixpkgs, which will
            # add them to PYTHONPATH and thus make them accessible from within the venv.
            ps.pyqtwebengine
          ]))

        ];
        shellHook = ''
            unset SOURCE_DATE_EPOCH

            # Create a virtual environment in .venv if it doesn't exist
             if [ ! -d ".venv" ]; then
              python -m venv .venv
            fi

            # Activate the virtual environment
            source .venv/bin/activate

            # Upgrade pip and install packages from requirements.txt if it exists
            pip install --upgrade pip > /dev/null
            if [ -f requirements.txt ]; then
              echo "Installing Python requirements from requirements.txt..."
              pip install -r requirements.txt > .pip-install.log 2>&1
              if [ $? -ne 0 ]; then
                echo "Pip install failed. See .pip-install.log for details."
              fi
            else
              echo "No requirements.txt found, skipping pip install."
            fi
            if [ -f requirements-dev.txt ]; then
              echo "Installing Python requirements from requirements-dev.txt..."
              pip install -r requirements-dev.txt > .pip-install.log 2>&1
              if [ $? -ne 0 ]; then
                echo "Pip install failed. See .pip-install.log for details."
              fi
            else
              echo "No requirements-dev.txt found, skipping pip install."
            fi

          # Add PyQt and QGIS to python path for neovim
          pythonWithPackages="${
            pkgs.python3.withPackages (ps: [
              ps.pyqt5-stubs
              ps.pyqtwebengine
            ])
          }"
          export PYTHONPATH="$pythonWithPackages/lib/python*/site-packages:${qgisWithExtras}/share/qgis/python:$PYTHONPATH"
            # Colors and styling
            CYAN='\033[38;2;83;161;203m'
            GREEN='\033[92m'
            RED='\033[91m'
            RESET='\033[0m'
            ORANGE='\033[38;2;237;177;72m'
            GRAY='\033[90m'
            # Clear screen and show welcome banner
            clear
            echo -e "$RESET$ORANGE"
            if [ -f animation_workbench/resources/animation-workbench-sketched.png ]; then
              chafa animation_workbench/resources/animation-workbench-sketched.png --size=30x80 --colors=256 | sed 's/^/                  /'
            fi
            # Quick tips with icons
            echo -e "$RESET$ORANGE \n__________________________________________________________________\n"
            echo -e "        Your Dev Environment is prepared."
            echo -e ""
            echo -e "Quick Commands:$RESET"
            echo -e "   $GRAY>$RESET  $CYAN./scripts/vscode.sh$RESET   - VSCode preconfigured for python dev"
            echo -e "   $GRAY>$RESET  $CYAN./scripts/checks.sh$RESET   - Run pre-commit checks"
            echo -e "   $GRAY>$RESET  $CYAN./scripts/clean.sh$RESET    - Cleanup dev folder"
            echo -e "   $GRAY>$RESET  $CYAN nix flake show$RESET      - Show available configurations"
            echo -e ""
            echo -e "Nix Run Commands:$RESET"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#qgis$RESET       - Start QGIS (stable)"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#qgis-ltr$RESET   - Start QGIS LTR"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#qgis-master$RESET - Start QGIS master"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#test$RESET       - Run pytest test suite"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#format$RESET     - Format code (black + isort)"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#lint$RESET       - Run linters (flake8 + pyright)"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#checks$RESET     - Run pre-commit checks"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#docs-serve$RESET - Serve docs locally"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#docs-build$RESET - Build documentation"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#package$RESET    - Build plugin zip"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#security$RESET   - Run security scan (bandit)"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#clean$RESET      - Clean workspace"
            echo -e "   $GRAY>$RESET  $CYAN nix run .#profile$RESET    - View profiling data (snakeviz)"
            echo -e ""
            echo -e "Neovim:$RESET"
            echo -e "   $GRAY>$RESET  $CYAN nvim$RESET                 - Start with LSP (PYTHONPATH auto-configured)"
            echo -e "   $GRAY>$RESET  Project keybindings: $CYAN<leader>p$RESET (run :WhichKey <leader>p)"
        '';
      };
    };
}
