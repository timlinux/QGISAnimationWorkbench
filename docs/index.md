# Welcome to the Animation Workbench

## 🤖 Why QGIS Animation Workbench?

QGIS Animation Bench exists because we wanted to use all the awesome cartography features in [QGIS](https://qgis.org) and make cool, animated maps!
QGIS already includes the Temporal manager which allows you to produce animations for time-based data. But what if you want to
make animations where you travel around the map, zooming in and out, and perhaps making features on the map wiggle and jiggle as the
animation progresses? That is what the animation workbench tries to solve.

## 🎨 Features

- [Modes](https://link-to-modes-doc.md) : Supports a 3 modes: Sphere, Planar and Static.
  - Sphere: Creates a spinning globe effect. Like Google Earth might do, but with your own data and cartography.
  - Planar: Lets you move from feature to feature on a flat map, pausing at each if you want to.
  - Static: The frame of reference stays the same and you can animate the symbology within that scene.
- [Internationalization (i18n)](https://github.com/nhn/tui.editor/tree/master/docs/en/i18n.md) : Supports English currently - we may add other languages in the future if there is demand.
- Add music to your exported videos - see the [Creative Commons](https://creativecommons.org/about/program-areas/arts-culture/arts-culture-resources/legalmusicforvideos/) website for a list of places where you can download free music (make sure it does not have a No Derivative Works license).
- Multithreaded, efficient rendering workflow. The plugin is designed to work well even on very modest hardware. If you have a fast PC, you can crank up the size to the thread pool to process more jobs at the same time. Here is an example of running a job with 9000 frames at 60fps and 999 frames per feature

![imagem](https://user-images.githubusercontent.com/178003/159691009-8a8485f0-2bf0-419f-9dd4-a71c207b9117.png)

And the subsequent CPU load during processing:

![cpu](https://user-images.githubusercontent.com/178003/159691200-18dfea74-ac11-4620-9def-803b9c61c98d.png)

After processing:

![imagem](https://user-images.githubusercontent.com/178003/159691416-7cd5c4bf-ad47-4943-9008-bd04b7bf4ef9.png)

And here is the resulting video:

<https://youtu.be/1quc3xPdJsU>
