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

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell

    # For PDF production  in mkdocs
    pythonPackages.venvShellHook
    python311Packages.weasyprint
    cairo
    pango
    gdk-pixbuf
    glib
    gtk2
    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    pythonPackages.requests
    pythonPackages.pygobject3
    # Doesnt work properly
    #python311Packages.cffi
    gobject-introspection 
    gtk3
    taglib
    openssl
    git
    libxml2
    libxslt
    libzip
    zlib
    gnused
    rpl
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
