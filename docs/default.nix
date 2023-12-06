with import <nixpkgs> { };

let
  # For packages pinned to a specific version
  pinnedHash = "933d7dc155096e7575d207be6fb7792bc9f34f6d"; 
  pinnedPkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/${pinnedHash}.tar.gz") { };
  pythonPackages = pinnedPkgs.python3Packages;
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell

    # For PDF production  in mkdocs
    pythonPackages.venvShellHook
    python311Packages.weasyprint
    pinnedPkgs.cairo
    pinnedPkgs.pango
    pinnedPkgs.gdk-pixbuf
    pinnedPkgs.glib
    pinnedPkgs.gtk2
    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    pythonPackages.requests
    pythonPackages.pygobject3
    # Doesnt work properly
    #python311Packages.cffi
    pinnedPkgs.gobject-introspection 
    pinnedPkgs.gtk3
    pinnedPkgs.taglib
    pinnedPkgs.openssl
    pinnedPkgs.git
    pinnedPkgs.libxml2
    pinnedPkgs.libxslt
    pinnedPkgs.libzip
    pinnedPkgs.zlib
    pinnedPkgs.gnused
    pinnedPkgs.rpl
  ];

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements.txt 
  '';

  shellHook = ''
  '';
  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
  '';

}
