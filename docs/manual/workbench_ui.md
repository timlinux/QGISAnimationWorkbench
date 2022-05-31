# The Workbench User Interface

## Animation Plan

![Sphere and Planar](img/001_AnimationPlan_SpherePlanar_1.png)

- Render Modes (**`1`**): These determine the behaviour and type of animation
  - **`Sphere`**: The coordinate reference system (CRS) will be manipulated to create a
      spinning globe effect. Like Google Earth might do, but with your own data and
      cartography.
  - **`Planar`**: The coordinate reference system (CRS) will not be altered, but the camera
      will pan and zoom to each point. It lets you move from feature to feature on a
      flat map, pausing at each if you want to.
  - **`Fixed extent`**: The frame of reference stays the same and you can animate the
      symbology within that scene.

- Animation Layer (**`2`**):
  - **`Dropdown menu`**: This allows you to select which map layer you want the animation
      to follow.
  - **`Loop from final feature back to first feature`**: allows for a seamlessly looping
      output GIF or movie(MP4).

- Zoom Range (**`3`**): The scale range that the animation should move through.
  - Minimum (exclusive): The zenith (highest point) of the animation when it zooms out
      while travelling between points, i.e. the most "zoomed out".
  - Maximum (inclusive): The scale (zoom level) used when we arrive at each point,
      i.e. the most "zoomed in".

- Data defined settings (**`4`**)
  - Scale
    - Minimum: User-defined minimum scale
    - Maximum: User-defined maximum scale

- Animation Frames (**`5`**)
  - Frame rate per second (fps): When writing to video or gif, how many frames per
      second to use.
  - Travel Duration: This is the number of seconds that the animation will take during
      animation from one feature to the next.
  - Feature Hover duration: This is the number of seconds that the animation will hover
      over each feature.

![Fixed Extent](img/002_AnimationPlan_FixedExtent_1.png)

- Extent (**`6`**):
  - Can be manually entered using North, East, South, and West coordinates as limits.
  - Can be calculated from a map layer, the layout map, or a bookmark.
  - Can be set to match the Map Canvas Extent
  - Can be set as a rectangular extent using the **`Draw on Canvas`** feature.

- Pan and Zoom Easings (**`7`**)
  - What are Easings: Easings are transitions from one state to another along a smooth
      curve. A user can specify the shape of the curve used.
  - Pan Easings (XY): The pan easing will determine the motion characteristics of the
      camera on the X and Y axis as it flies across the scene (i.e. how it accelerates
      or decelerates between points)
  - Zoom Easing (Z): The pan easing will determine the motion characteristics of the
      camera on the Z axis as it flies across the scene (i.e. how the camera zooms in
      and out of the points)

- Frame previews (**`8`**): A preview of what each frame of the animation will look like. A
    user can decide which **`Frame`** to view.

## Intro Tab

Edit the intro section of the generated movie here.

![Intro Tab](img/003_IntroTab_1.png)

- Media: List of the various images or movies selected for the intro section. You can
  drag and drop items in the list to change the play order.
  - Add Media (Plus sign) (**`1`**): Add images or movies
  - Remove Media (Minus sign) (**`2`**): Remove images or movies

- Duration (**`3`**): For images, you can set a duration for each image (in seconds).
- Preview Frame (**`4`**): This shows what the media will look like.

- Details: Provides details about where the media is stored on your computer.

## Outro Tab

Edit the outro section of the generated movie here.

![Outro Tab](img/004_OutroTab_1.png)

- Media: List of the various images or movies selected for the outro section. You can
  drag and drop items in the list to change the play order.
  - Add Media (Plus sign) (**`1`**): Add images or movies
  - Remove Media (Minus sign) (**`2`**): Remove images or movies

- Duration (**`3`**): For images, you can set a duration for each image (in seconds).
- Preview Frame (**`4`**): This shows what the media will look like.

- Details: Provides details about where the media is stored on your computer.

## Soundtrack Tab

![Soundtrack Tab](img/005_SoundtrackTab_1.png)

- Media: List of the various sound files (.mp3 or .wav) to play during the generated movie.
  You can drag and drop items in the list to change the play order.
  - Add Media (Plus sign) (**`1`**): Add sound files (.mp3 or .wav) to play during the
            generated movie.
  - Remove Media (Minus sign) (**`2`**): Remove sound files (.mp3 or .wav)

- Duration (**`3`**): The cumulative length of your soundtracks should be as long, or longer,
          than your movie, including the intro/outro sections. If the soundtrack is longer
          than the movie it will be truncated (shortened) when the movie ends.

- Details: Provides details about where the media is stored on your computer.

## Output

![Output Tab](img/006_OutputTab_1.png)

- Output Options: Select which output format you would like. Regardless of the format chosen,
  a folder of images will be created, one image per frame.
  - Re-use cached Images (**`1`**): This will not erase cached images on disk and will resume
    processing from the last cached image.
  - Animated GIF (**`2`**): For this export to work, you need to have the ImageMagick 'convert'
    application available on your system.
  - Movie (MP4) (**`3`**): For this option to work, you need to have the 'ffmpeg' application
    on your system.
  - Output Resolution (**`4`**): Allows a user to specify one of three image resolutions for
    the output animation. The numbers in brackets represent the width and height of the
    output in pixels (i.e. width x height).
  - File selection (ellipsis) (**`5`**): This lets a user select the location where the output
    will be stored.

## Progress

![Progress Tab](img/007_ProgressTab_1.png)

- Frame Preview (**`1`**): A preview of what each frame of the animation will look like.
            It changes automatically as the workbench runs.
- Progress (**`2`**): This provides a detailed look at what is happening while the workbench
            runs.
  - Total Tasks: This number represents the total number of frames that will be generated
    by the workbench.
  - Completed Tasks: The number of tasks that have completed being processed.
  - Remaining Features: The number of features from your animation layer that still need
    to be processed.
  - Active Tasks: The number of tasks (threads) currently being run by the workbench
  - Features Complete: The number of tasks that have been processed by the workbench.
- Logs (**`3`**): A detailed list of what steps the workbench is doing (a record of processing)
- Progress Bar (**`4`**): A visual representation of the workbench's progression as a percentage.

## Other Buttons

- **`Run`**: Starts the process of getting an output from the workbench. It is greyed out
            until a user provides a destination for the output file.
- **`Close`**: Closes the workbench.
- **`Cancel`**: Ends the workbench processing at whatever point it has reached when the
            button is pressed.
- **`Help`**: Opens a link to the Animation Workbench documentation.
