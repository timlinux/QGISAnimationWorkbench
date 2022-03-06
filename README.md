# ![QGIS Animations Plugin]()

> Welcome to the QGIS Animation Workbench!

[![github release version](https://img.shields.io/github/v/release/timlinux/QGISAnimationWorkbench.svg?include_prereleases)](https://github.com/timlinux/QGISAnimationWorkbenchr/releases/latest) [![QGIS Plugin Repository](https://img.shields.io/badge/Powered%20by-QGIS-blue.svg)](https://plugins.qgis.org/FIXME) [![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://github.com/timlinux/QGISAnimationWorkbench/blob/master/LICENSE) [![PRs welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg)](https://github.com/timlinux/QGISAnimationWorkbench/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) [![code with heart by timlinux](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%99%A5%20by-timlinux-ff1414.svg)](https://github.com/timlinux)

<img src="https://user-images.githubusercontent.com/178003/156927270-4491b001-43a3-4302-a819-41c4fac8c14c.png" width="800" />

## 🚩 Table of Contents

- [!QGIS Animations Plugin](#)
  - [🚩 Table of Contents](#-table-of-contents)
  - [📦 Packages](#-packages)
  - [🤖 Why QGIS Animation Workbench?](#-why-qgis-animation-workbench)
  - [🎨 Features](#-features)
  - [🐾 Examples](#-examples)
  - [🌏 QGIS Support](#-qgis-support)
  - [🔧 Pull Request Steps](#-pull-request-steps)
    - [Setup](#setup)
    - [Develop](#develop)
      - [Debugging](#debugging)
      - [Packaging](#packaging)
      - [Run test](#run-test)
    - [Pull Request](#pull-request)
  - [💬 Contributing](#-contributing)
  - [🚀 Used By](#-used-by)
  - [📜 License](#-license)
  - [Credits](#credits)


## 📦 Packages

| Name | Description |
| --- | --- |
| [`Alpha Version`](https://github.com/timlinux/QGISAnimationWorkbench/archive/refs/tags/apha-1.zip) | Alpha Release (not production ready) |


## 🤖 Why QGIS Animation Workbench?

QGIS Animation Bench exists because we wanted to use all the awesome cartography features in [QGIS](https://qgis.org) and make cool, animated maps!
QGIS already includes the Temporal manager which allows you to produce animations for time-based data. But what if you want to 
make animations where you travel around the map, zooming in and out, and perhaps making features on the map wiggle and jiggle as the 
animation progresses? That is what the animation workbench tries to solve.



## 🎨 Features

* [Modes](https://link-to-modes-doc.md) : Supports a 3 modes: Sphere, Planar and Static.
    * Sphere: Creates a spinning globe effect. Like Google Earth might do, but with your own data and cartography.
    * Planar: Lets you move from feature to feature on a flat map, pausing at each if you want to.
    * Static: The frame of reference stays the same and you can animate the symbology within that scene.
* [Internationalization (i18n)](https://github.com/nhn/tui.editor/tree/master/docs/en/i18n.md) : Supports English currently - we may add other languages in the future if there is demand.

## 🐾 Examples

Let's show you some examples!

A simple spinning globe:



https://user-images.githubusercontent.com/178003/156930974-e6d4e76e-bfb0-4ee2-a2c5-030eba1aad8a.mp4



A street tour of Zaporizhzhia:





https://user-images.githubusercontent.com/178003/156930785-d2cca084-e85d-4a67-8b6c-2dc090f08ac6.mp4


Data above © OpenStreetMap Contributors

QGIS Developers:


https://user-images.githubusercontent.com/178003/156931066-87ce89e4-f8d7-46d9-9d30-aeba097f6d98.mp4


## 🌏 QGIS Support

Should work with QGIS 3.

## 🔧 Pull Request Steps

This project is open source, so you can create a pull request(PR) after you fix issues. Get a local copy of the plugins checked out for development using the following process.

### Setup

Fork `main` branch into your personal repository. Clone it to local computer. Install QGIS and the following dependencies. 

* debugpy
* convert (imagemagick)
* ffmpeg
* vscode (dont use flatpak, debugging will not work with QGIS)


Before starting development, you should check if there are any errors.

```sh
$ git clone https://github.com/{your-personal-repo}/QGISAnimationWorkshop.git
$ ln -s QGISAnimationWorkbench ~.local/share/QGIS/QGIS3/profiles/<profile>/python/plugins
```

Enable the python in the QGIS plugin manager. You should also install the [Plugin Reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin so you can quickly deploy changes to your local session in QGIS as you are working.


### Develop

#### Debugging

``` sh
$ TODO
```

#### Packaging
If testing of legacy browsers is required, the development server can still be run using a [webpack](https://webpack.js.org/).

``` sh
$ TODO
```

#### Run test

``` sh
$ TODO
```

### Pull Request

Before uploading your PR, run test one last time to check if there are any errors. If it has no errors, commit and then push it!

For more information on PR's steps, please see links in the Contributing section.

## 💬 Contributing

* [Code of Conduct](https://github.com/timlinux/QGISAnimationWorkbench/blob/master/CODE_OF_CONDUCT.md)
* [Contributing Guideline](https://github.com/timlinux/QGISAnimationWorkbench/blob/master/CONTRIBUTING.md)
* [Commit Convention](https://github.com/timlinux/QGISAnimationWorkbench/blob/master/docs/COMMIT_MESSAGE_CONVENTION.md)
* [Issue Guidelines](https://github.com/timlinux/QGISAnimationWorkbench/tree/master/.github/ISSUE_TEMPLATE)


## 🚀 Used By

* [Tell Us)](https://example.com)

## 📜 License

This software is licensed under the [GPL v2](https://github.com/timlinux/QGISAnimationWorkbench/blob/master/LICENSE) © [timlinux](https://github.com/timlinux).

##  Credits

This plugin was developed by 


Tim Sutton |
-----------|
![Tim](https://avatars.githubusercontent.com/u/178003?v=4&s=174 "Tim") | 
Tim Sutton |
Coder and Ideas Guy |
[timlinux @ github](https://github.com/timlinux/) |


Thanks to:



Nyall Dawson | 
-----------| 
![Tim](https://avatars.githubusercontent.com/u/178003?v=4&s=174 "Tim") |

Also:
* [NHN and Tui Editor](https://raw.githubusercontent.com/nhn/tui.editor) for the great README which I based this one on.

