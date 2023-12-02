# Developer Notes

### Setup

Fork `main` branch into your personal repository. Clone it to local computer. Install QGIS and the following dependencies.

- debugpy
- convert (imagemagick)
- ffmpeg
- vscode (dont use flatpak, debugging will not work with QGIS)

Before starting development, you should check if there are any errors.

```sh
git clone https://github.com/{your-personal-repo}/QGISAnimationWorkbench.git
ln -s QGISAnimationWorkbench ~.local/share/QGIS/QGIS3/profiles/<profile>/python/plugins
```

Enable the python in the QGIS plugin manager. You should also install the [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin so you can quickly deploy changes to your local session in QGIS as you are working.

#### Debugging

``` sh
TODO
```

#### Packaging

``` sh
TODO
```

#### Run test

``` sh
TODO
```
