# Building documentation

## Preparing your Environment

The general workflow we recommend is:

1. Install the nix package manager
2. Checkout this project
3. Open this docs folder in a shell / terminal application
4. Open a nix-shell to install the build environment

### Install Nix package manager

If you are on ubuntu, windows (under WSL2) or macOS you can install the nix
package manager which will fetch all the dependencies needed to build this
project.

To do this, please go to the [Nix Download Page]() and follow the instructions
under `Nix: the package manager` as appropriate to your operating system.

A special note for NixOS users:

If you are a NixOS user, you already have the nix package manager. You can
additionally install [direnv](https://github.com/nix-community/nix-direnv)
which will create a seamless entry into the development environment.

### Checkout this project

You need to have a local copy of this project in order to build the documentation. To do that you can do:

```
git clone https://github.com/timlinux/QGISAnimationWorkbench.git
```

or

```
git clone git@github.com:timlinux/QGISAnimationWorkbench.git
```

### Open the project in your terminal

Open your favourite terminal and enter into this documentation folder:

```
cd QGISAnimationWorkbench/docs/
```

### Install the build environment

Now we can set up the build environment. Note that it will fetch a bunch of
packages from the internet, so having a good internet connection will help a
lot here.

```
nix shell
```

Note: As mentioned above, if you have direnv set up on NixOS, you can skip this
step, it is automatic.

When the setup process completes, you will see something like this in your shell:


```
direnv: loading ~/dev/python/QGISAnimationWorkbench/docs/.envrc
direnv: using nix
Using venvShellHook
Executing venvHook
Skipping venv creation, './.venv' already exists
Finished executing venvShellHook
direnv: export +AR +AS +CC +CONFIG_SHELL +CXX +DETERMINISTIC_BUILD +GETTEXTDATADIRS +GETTEXTDATADIRS_FOR_TARGET +GSETTINGS_SCHEMAS_PATH +HOST_PATH +IN_NIX_SHELL +LD +NIX_BINTOOLS +NIX_BINTOOLS_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu +NIX_BUILD_CORES +NIX_BUILD_TOP +NIX_CC +NIX_CC_WRAPPER_TARGET_HOST_x86_64_unknown_linux_gnu +NIX_CFLAGS_COMPILE +NIX_ENFORCE_NO_NATIVE +NIX_HARDENING_ENABLE +NIX_LDFLAGS +NIX_SSL_CERT_FILE +NIX_STORE +NM +OBJCOPY +OBJDUMP +PYTHONHASHSEED +PYTHONNOUSERSITE +PYTHONPATH +RANLIB +READELF +SIZE +SSL_CERT_FILE +STRINGS +STRIP +SYSTEM_CERTIFICATE_PATH +TEMP +TEMPDIR +TMP +TMPDIR +VIRTUAL_ENV +VIRTUAL_ENV_PROMPT +XML_CATALOG_FILES +_PYTHON_HOST_PLATFORM +_PYTHON_SYSCONFIGDATA_NAME +__structuredAttrs +buildInputs +buildPhase +builder +cmakeFlags +configureFlags +depsBuildBuild +depsBuildBuildPropagated +depsBuildTarget +depsBuildTargetPropagated +depsHostHost +depsHostHostPropagated +depsTargetTarget +depsTargetTargetPropagated +doCheck +doInstallCheck +mesonFlags +name +nativeBuildInputs +out +outputs +patches +phases +postShellHook +postVenvCreation +preferLocalBuild +propagatedBuildInputs +propagatedNativeBuildInputs +shell +shellHook +stdenv +strictDeps +system +venvDir ~GI_TYPELIB_PATH ~PATH ~XDG_DATA_DIRS
```

You can further validate that everything is set up correctly by running 


```
pip freeze
```

You should see a list of packages similar to those listed below:

```
Babel==2.13.1
beautifulsoup4==4.12.2
black==23.11.0
Brotli==1.1.0
brotlicffi==1.1.0.0
certifi==2023.7.22
cffi==1.16.0
chardet==5.2.0
charset-normalizer==3.2.0
click==8.1.7
colorama==0.4.6
cssselect2==0.7.0
defusedxml==0.7.1
fonttools==4.42.1
ghp-import==2.1.0
gitdb==4.0.11
GitPython==3.1.40
griffe==0.38.0
html5lib==1.1
idna==3.4
Jinja2==3.1.2
libsass==0.22.0
lxml==4.9.3
Markdown==3.5.1
MarkupSafe==2.1.3
mdx-gh-links==0.3.1
mergedeep==1.3.4
mkdocs==1.5.3
mkdocs-autorefs==0.5.0
mkdocs-enumerate-headings-plugin==0.6.1
mkdocs-git-revision-date-localized-plugin==1.2.1
mkdocs-material==9.4.14
mkdocs-material-extensions==1.3.1
mkdocs-pdf-export-plugin==0.5.10
mkdocs-redirects==1.2.1
mkdocs-video==1.5.0
mkdocs-with-pdf==0.9.3
mkdocstrings==0.24.0
mkdocstrings-python==1.7.5
mypy-extensions==1.0.0
olefile==0.46
packaging==23.2
paginate==0.5.6
pathspec==0.11.2
Pillow==10.1.0
platformdirs==4.1.0
pycairo==1.24.0
pycparser==2.21
pydyf==0.8.0
Pygments==2.17.2
PyGObject==3.46.0
pymdown-extensions==10.5
pyphen==0.14.0
python-dateutil==2.8.2
pytz==2023.3.post1
PyYAML==6.0.1
pyyaml_env_tag==0.1
regex==2023.10.3
requests==2.31.0
shortuuid==1.0.11
six==1.16.0
smmap==5.0.1
soupsieve==2.5
tinycss2==1.2.1
urllib3==2.0.7
watchdog==3.0.0
weasyprint==60.1
webencodings==0.5.1
zopfli==0.2.3
```


## Workflow 1: HTML Static Web Site

In this workflow, we will build the static website created by our
documentation, and then use the development server provided by mkdocs to view
the site. We assume as a starting point that you have not yet run nix-shell:

```
nix-shell
./create-mkdocs-html-config.sh
./build-docs-html.sh
mkdocs serve
```

By default the mkdocs server will publish the site on your localhost, port 8000
at http://127.0.0.1:8000/

In your web browser you can then peruse the generated site. To stop the server,
return to your shell and press ``Crtl-c``.

If you want to rebuild your docs after making some edits / corrections, you can
then just run the last two steps again:

```
./build-docs-html.sh
mkdocs serve
```

Alternatively, just leave the server running, make your edits as needed and
mkdocs will rebuild the site whenever you make a change.

## Workflow 2: PDF Generated Documentation

This workflow is almost identical to workflow 1, except in this case, we will
build the PDF documentation, and then use the development server to rebuild the
PDF as needed. We assume as a starting point that you have not yet run
nix-shell:

```
nix-shell
./create-mkdocs-pdf-config.sh
./build-docs-pdf.sh
mkdocs serve
```

By default the mkdocs serve will generate the PDF into the ``pdfs`` folder as
file [QGISAnimationWorkbench.pdf](pdfs/QGISAnimationWorkbench.pdf).

In your PDF viewer you can then peruse the generated document. To stop the server,
return to your shell and press ``Crtl-c``.

If you want to rebuild your docs after making some edits / corrections, you can
then just run the last two steps again:

```
./build-docs-pdf.sh
mkdocs serve
```

Alternatively, just leave the server running, make your edits as needed and
mkdocs will rebuild the PDF whenever you save a change.

