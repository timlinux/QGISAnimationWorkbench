# Using the Animation Workbench

In this section, we describe the general workflow for using the Animation Workbench.

## Process Overview

1. Create a QGIS project!
2. Identify features that will be animated.
3. Use the QGIS Expressions system with the variables introduced by the Animation
   Workbench to define behaviours of your symbols during flight and hover modes of your
   animation.
4. Open the Animation Workbench and configure your animation, choosing between the
   different modes and options.
5. Render your animation!

## More in Depth Process

1. Create a QGIS Project
   &nbsp;<!--Adds blank space for formatting-->
   Open QGIS and click on `Project` ➔ `New`

   ![New Project](img/004_NewProject_1.png)

   &nbsp;<!--Adds blank space for formatting-->

   Add new layers to your project

   ![Add Layers](img/005_AddLayers_1.png)

   > Note: A simple way to add a base layer is to type "world" (**`1`**) into the coordinate
   textbox

   Style the layers you've added to make your project look a bit better. Select the
   layer (**`2`**) you want to style and in the Layer Styling toolbar (**`3`**), style the layer to
   look appealing to you.

   ![Style Layers](img/006_StylingLayers_1.png)

   &nbsp;<!--Adds blank space for formatting-->

2. Identify features that will be animated.
   &nbsp;<!--Adds blank space for formatting-->

   Pick the layer (or layers) that you want to animate. Then either find or create the
   animation for the layer. Make sure you have all the correct attribution for any
   animations you use. Below is an example of an animation split into its frames.

   ![Animation Frames](img/007_AnimatedLayer_1.png)

3. Use the QGIS Expressions system with the variables introduced by the Animation
   Workbench to define behaviours of your symbols during flight and hover modes of your
   animation.
   &nbsp;<!--Adds blank space for formatting-->

   Select the layer you want to animate and open the Layer Styling toolbar.

   > Note: If you are using `QGIS 3.26` you can simply use the new animated point symbol,
   or if you're using an older version of `QGIS 3.x` follow the instructions below.

   The layer should be a `Raster Image Marker`. Once you have selected the image you
   want to use click on the QGIS Expressions dropdown menu (**`4`**) and click on `Edit` (**`5`**).

   ![Edit Expression](img/008_EditExpression_1.png)

   &nbsp;<!--Adds blank space for formatting-->
   Use the [Code Snippets Section](../library/snippets.md) for more in depth help. The
   example below works with the bird animation from earlier

   ![Expression Snippet](img/009_Expression_1.png)

   ```sql
      @project_home
      ||
      '/bird/bird_00'
      || 
      lpad(to_string(@frame_number % 9), 2, '0')
      || 
      '.png'
   ```

4. Open the Animation Workbench and configure your animation, choosing between the
   different modes and options.
   &nbsp;<!--Adds blank space for formatting-->

   Open the Workbench by clicking the `Animation Workbench` (**`6`**) icon in the Plugin Toolbar.

   ![Open Workbench](img/010_OpenAW_1.png)
   &nbsp;<!--Adds blank space for formatting-->

   Configure the settings for your animation. The screenshot below is configured for
   the example presented in this section. The Animation Layer is selected as route (**`7`**)
   because that is the path the animation will fly along, the Zoom Range (**`8`**) was selected
   from the Map Canvas Extent, and the Frame rate per second (**`9`**) was set to 9 to match
   the bird animation.

   ![Output Setup](img/011_OutputSetup_1.png)
   &nbsp;<!--Adds blank space for formatting-->

   Set your desired `Output Options` (**`10`**) Select a location for your output (**`11`**).

   ![Output Location](img/012_Output_1.png)
   &nbsp;<!--Adds blank space for formatting-->

   > Note:  Refer to the [Workbench User Interface](../docs/../manual/workbench_ui.md) Section for more information about
   what various settings and buttons accomplish.

5. Render your animation!
   &nbsp;<!--Adds blank space for formatting-->
   Click `Run` and render your output. The output below is the output from the example.

   ![Output](img/output.gif)
