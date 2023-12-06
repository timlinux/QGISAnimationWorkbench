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

    # For PDF production  in mkdocs - see https://comwes.github.io/mkpdfs-mkdocs-plugin/index.html
    pythonPackages.venvShellHook
    python311Packages.weasyprint
    cairo
    pango
    gdk-pixbuf
    glib
    gtk2
    
    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    pythonPackages.numpy
    pythonPackages.requests
    pythonPackages.pygobject3
    # Doesnt work properly
    #python311Packages.cffi

    # In this particular example, in order to compile any binary extensions they may
    # require, the Python modules listed in the hypothetical requirements.txt need
    # the following packages to be installed locally:
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
    # Need to manually install this because of https://github.com/comwes/mkpdfs-mkdocs-plugin/pull/15
    pip install -e git+https://github.com/jwaschkau/mkpdfs-mkdocs-plugin.git#egg=mkpdfs-mkdocs
    rpl -R "from weasyprint.fonts import FontConfiguration" "from weasyprint.text.fonts import FontConfiguration" .venv/src/mkpdfs-mkdocs/mkpdfs_mkdocs/mkpdfs.py
    rpl -R "from weasyprint.fonts import FontConfiguration" "from weasyprint.text.fonts import FontConfiguration" .venv/lib/python3.11/site-packages/mkpdfs_mkdocs/generator.py
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
