# The Workbench User Interface

## Animation Plan
- Render Modes: These determine the behaviour and type of animation
    - 1\. `Sphere`: the coordinate reference system (CRS) will be manipulated to create a spinning globe effect. 
        Like Google Earth might do, but with your own data and cartography.
    - 2\. `Planar`: the coordinate reference system (CRS) will not be altered, but the camera will pan and zoom 
        to each point. It lets you move from feature to feature on a flat map, pausing at each if you want to.
    - 3\. `Fixed extent`: The frame of reference stays the same and you can animate the symbology within that scene. 

- Animation Layer: 
    - 4\. `Dropdown menu`: Allows you to select which map layer you want the animation to follow.
    - 5\. `Loop from final feature back to first feature`: allows for a seamlessly looping output GIF or movie(MP4).

- Zoom Range: The scale range that the animation should move through.
    - 6\. Minimum (exclusive): the zenith (highest point) of the animation when it zooms out while travelling between 
        points, i.e. the most "zoomed out".
    - 7\. Maximum (inclusive): the scale (zoom level) used when we arrive at each point, i.e. the most "zoomed in".

- Data defined settings
    - 8\. Scale
        - Minimum: User defined minimum scale
        - Maximum: User defined maximum scale

- Animation Frames
    - 9\. Frame rate per second (fps): When writing to video or gif, how many frames per second to use.
    - 10\. Travel Duration: This is the number of seconds that the animation will take during animation from one feature
         to the next.
    - 11\. Feature Hover duration: This is the number of seconds that the animation will hover over each feature.

- Extent:
    - 12\. Can be manually entered using North, East, South, and West coordinates as limits.
    - 13\. Can be calculated from a map layer, the layout map, or a bookmark. 
    - 14\. Can be set to match the Map Canvas Extent
    - 15\. Can be set as a rectangular extent using the `Draw on Canvas` feature.

- Pan and Zoom Easings
    - What are Easings: Easings are transitions from one state to another along a smooth curve. A user can specify the 
        shape of the curve used.
    - 16\. Pan Easings (XY): The pan easing will determine the motion characteristics of the camera on the X and Y axis as it
         flies across the scene (i.e. how it accelerates or decelerates between points)
    - 17\. Zoom Easing (Z): The pan easing will determine the motion characteristics of the camera on the Z axis as it flies 
        across the scene (i.e. how the camera zooms in and out of the points)

- Frame previews: a preview of what each frame of the animation will look like. A user can decide which 18\. `Frame` to view.

## Intro Tab

## Outro Tab

## Soundtrack Tab

## Output

## Progress

## Other Buttons