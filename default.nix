with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python
    pylint
    black
    python311Packages.future
    qgis
    vscode
    xorg.libxcb
    qgis
    qt5.full
    qtcreator
    python3
    python3Packages.pyqt5
    python3Packages.gdal
    python3Packages.pytest

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell

  ];

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements.txt
  '';

  shellHook = ''
    export PYTHONPATH=$PYTHONPATH:`which qgis`/../../share/qgis/python
    export QT_QPA_PLATFORM=offscreen
  '';

  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
  '';

}
