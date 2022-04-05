# ![QGIS Animation Workbench]()

> Welcome to the QGIS Animation Workbench!

![Logo](resources/img/logo/animation-workbench-logo.svg)

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

| Name                                                                                               | Description                          |
| -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [`Alpha Version 2`](https://github.com/timlinux/QGISAnimationWorkbench/archive/refs/tags/apha-2.zip) | Alpha Release (not production ready) |
| [`Alpha Version 1`](https://github.com/timlinux/QGISAnimationWorkbench/archive/refs/tags/apha-1.zip) | Alpha Release (not production ready) |


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
* Add music to your exported videos - see the [Creative Commons](https://creativecommons.org/about/program-areas/arts-culture/arts-culture-resources/legalmusicforvideos/) website for a list of places where you can download free music (make sure it does not have a No Derivative Works license).
* Multithreaded, efficient rendering workflow. The plugin is designed to work well even on very modest hardware. If you have a fast PC, you can crank up the size to the thread pool to process more jobs at the same time. Here is an example of running a job with 9000 frames at 60fps and 999 frames per feature

![imagem](https://user-images.githubusercontent.com/178003/159691009-8a8485f0-2bf0-419f-9dd4-a71c207b9117.png)

And the subsequent CPU load during processing:


![cpu](https://user-images.githubusercontent.com/178003/159691200-18dfea74-ac11-4620-9def-803b9c61c98d.png)

After processing:

![imagem](https://user-images.githubusercontent.com/178003/159691416-7cd5c4bf-ad47-4943-9008-bd04b7bf4ef9.png)

And here is the resulting video:

https://youtu.be/1quc3xPdJsU 

## 🐾 Examples

Let's show you some examples!

A simple spinning globe:



https://user-images.githubusercontent.com/178003/156930974-e6d4e76e-bfb0-4ee2-a2c5-030eba1aad8a.mp4



A street tour of Zaporizhzhia:





https://user-images.githubusercontent.com/178003/156930785-d2cca084-e85d-4a67-8b6c-2dc090f08ac6.mp4


Data above © OpenStreetMap Contributors

QGIS Developers:


https://user-images.githubusercontent.com/178003/156931066-87ce89e4-f8d7-46d9-9d30-aeba097f6d98.mp4


## QGIS Expression Variables

The animation workbench exposes or modifies a number of different QGIS Expression variables that you can use to achieve different dynamic rendering effects.

| Variable                  | Notes                                                                             |
| ------------------------- | --------------------------------------------------------------------------------- |
| current_feature_id        | Feature ID for feature we are moving towards.                                     |
| frames_per_feature        | Total number of frames (including fly and dwell frames) for each feature.         |
| current_frame_for_feature | Frame number within total number of frames for this feature.                      |
| dwell_frames_per_feature  | Total number of frames to dwell (hover) on each feature for.                      |
| current_animation_action  | Either "Hovering", "Panning" or "None".                                           |
| frame_number              | Frame number within the current dwell or pan range.                               |
| frame_rate                | Number of frames per second that the video will be rendered at.                   |
| total_frame_count         | Total number of frames for the whole animation across all features.               |
| current_frame             | Deprecated variable, kept temporarily for compatibility with older projects only. |

## Example expressions

Showing diagnostic information in the QGIS copyright label:

```
[%'Frame ' || to_string(coalesce(@frame_number, 0)) || '/' ||
     to_string(coalesce(@frames_per_feature, 0)) || ' for feature ' ||
     to_string(coalesce(@current_feature_id,0)) || 
     ' with map mode: ' || @current_animation_action %]
```

Variably changing the size on a label as we approach it in the animation:

```
40 * ((@frame_number % @frames_per_feature) /  @frames_per_feature)
```



## 🌏 QGIS Support

Should work with and version of QGIS 3.x. If you have QGIS 3.26 or better you can benefit from the animated icon support (see @nyalldawson's most excellent patch [#48060](https://github.com/qgis/QGIS/pull/48060)).

For QGIS versions below 3.26, you can animate markers by unpacking a GIF image into it's constituent frames and then referencing a specific frame from the symbol data defined property for the image file. Note that to do this extraction below you need to have the [Open Source ImageMagick application](https://imagemagick.org/script/download.php) installed:

First extract a gif to a sequence of images:

```
convert cat.gif -coalesce cat_%05d.png
```

Example of how to create a dynamically changing image marker based on the current frame count:


```
@project_home 
||
'/gifs/cat_000'
|| 
lpad(to_string( @current_frame % 48 ), 2, '0') 
|| 
'.png'
```

Note that for the above, 48 is the number of frames that the GIF was composed of, and it assumes the frames are in the project directory in a subfolder called ``gifs``.




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
$ git clone https://github.com/{your-personal-repo}/QGISAnimationWorkbench.git
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

## Author

This plugin was developed by: 


| Tim Sutton                                                             | Nyall Dawson                                                                 |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| ![Tim](https://avatars.githubusercontent.com/u/178003?v=4&s=174 "Tim") | ![Nyall Dawson](https://avatars.githubusercontent.com/u/1829991?v=4 "Nyall") |
| Coder and Ideas Guy                                                    | Genius Guru of Awesomeness                                                   |
| [timlinux @ github](https://github.com/timlinux/)                      | [nyalldawson @ github](https://github.com/nyalldawson/)                      |


## Contributors:

Thanks to:

*Mathieu Pellerin (@nirvn)


We are looking for contributors, add yourself here!

Also:
* [NHN and Tui Editor](https://raw.githubusercontent.com/nhn/tui.editor) for the great README which I based this one on.

