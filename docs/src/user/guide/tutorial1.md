## Tutorial 1: Point Along A Line

This tutorial introduces the concept of moving a point along a line within your animated
map.

1\. Download and extract the **[Required Tutorial Zip Folder](https://github.com/timlinux/QGISAnimationWorkbench/blob/main/examples/tutorial_1.zip)**
&nbsp;<!--Blank Space-->

2\. Open the **tutorial_1.qgz** project file that is in the folder. When you first open it you
you see something like this:

![Initial Open](img/tut_1/001_InitialOpen_1.png)
&nbsp;<!--Blank Space-->

3\. Select the premade `line` layer (**`1`**), and click on the `Add Symbol Layer`
(*green plus symbol*) button (**`2`**) to it.

![Add Symbol Layer](img/tut_1/002_AddSymbolLayer_1.png)

Change the new `Symbol Layer` (**`3`**) type to marker line and then style it (**`4`**) so that it is more visible.

![Style Symbol Layer](img/tut_1/003_StyleSymbolLayer_1.png)

4\. Change the `Symbol Layer's` settings so that the point is only on the `first vertex` (**`5`**) and
and not at equidistant intervals.

Change the offset along the line to be `Percentage` (**`6`**).

![Symbol Layer Settings](img/tut_1/005_EditExpression_1.png)

Click the `Dropdown Menu` (**`7`**) ➔`Edit...` (**`8`**) and then add the following code snippet

![Edit Expression](img/tut_1/005_EditExpression_1.png)

```sql
    -- Point Along Line Code Snippet
    (@current_hover_frame/@hover_frames) * 100
```

![Offset along line Snippet](img/tut_1/006_OffsetSnippet_1.png)

The snippet tells QGIS how far along the line (as a percentage of the line length) to
render the point in each frame.

5\. Open the Workbench and select `Fixed Extent` (**`9`**).

Click on `Map Canvas Extent` (**`10`**) and set the the `Frames` to 300 (**`11`**) (for a 10 second
output at 30 frames per second).

![Animation Plan](img/tut_1/007_AnimationPlan_1.png)

6\. Skip over the `Intro`, `Outro`, and `Soundtrack` tabs. In the `Output` tab, set the output
format (**`12`**) and resolution (**`13`**), and set the output location's path (**`14`**).

![Output Tab](img/tut_1/008_OutputTab_1.png)

7\. Click `Run` and render your output.

![Point Along Line Output GIF](img/tut_1/output.gif)

After this tutorial you should have a better idea of how to make a point move along a line.
An expansion to this example would be to make the moving point a dynamically changing
marker (like the markers in tutorial 1). Go have fun!

