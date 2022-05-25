# The Workbench User Interface

## Animation Plan

- 1\. Render Modes: These determine the behaviour and type of animation
  - `Sphere`: the coordinate reference system (CRS) will be manipulated to create a spinning globe effect.
        Like Google Earth might do, but with your own data and cartography.
  - `Planar`: the coordinate reference system (CRS) will not be altered, but the camera will pan and zoom
        to each point. It lets you move from feature to feature on a flat map, pausing at each if you want to.
  - `Fixed extent`: The frame of reference stays the same and you can animate the symbology within that scene.

- 2\. Animation Layer:
  - `Dropdown menu`: Allows you to select which map layer you want the animation to follow.
  - `Loop from final feature back to first feature`: allows for a seamlessly looping output GIF or movie(MP4).

- 3\. Zoom Range: The scale range that the animation should move through.
  - Minimum (exclusive): the zenith (highest point) of the animation when it zooms out while travelling between
        points, i.e. the most "zoomed out".
  - Maximum (inclusive): the scale (zoom level) used when we arrive at each point, i.e. the most "zoomed in".

- 4\. Data defined settings
  - Scale
    - Minimum: User defined minimum scale
    - Maximum: User defined maximum scale

- 5\. Animation Frames
  - Frame rate per second (fps): When writing to video or gif, how many frames per second to use.
  - Travel Duration: This is the number of seconds that the animation will take during animation from one feature
         to the next.
  - Feature Hover duration: This is the number of seconds that the animation will hover over each feature.

![Sphere and Planar](img/001_AnimationPlan_SpherePlanar_1.png)

- 6\. Extent:
  - Can be manually entered using North, East, South, and West coordinates as limits.
  - Can be calculated from a map layer, the layout map, or a bookmark.
  - Can be set to match the Map Canvas Extent
  - Can be set as a rectangular extent using the `Draw on Canvas` feature.

- 7\. Pan and Zoom Easings
  - What are Easings: Easings are transitions from one state to another along a smooth curve. A user can specify the
        shape of the curve used.
  - Pan Easings (XY): The pan easing will determine the motion characteristics of the camera on the X and Y axis as it
         flies across the scene (i.e. how it accelerates or decelerates between points)
  - Zoom Easing (Z): The pan easing will determine the motion characteristics of the camera on the Z axis as it flies
        across the scene (i.e. how the camera zooms in and out of the points)

- 8\. Frame previews: a preview of what each frame of the animation will look like. A user can decide which `Frame` to view.

![Fixed Extent](img/002_AnimationPlan_FixedExtent_2.png)

## Intro Tab

## Outro Tab

## Soundtrack Tab

## Output

## Progress

## Other Buttons
