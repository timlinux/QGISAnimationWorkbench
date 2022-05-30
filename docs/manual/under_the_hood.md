# What is the Workbench doing?

- **What does the workbench do?**
    The workbench creates animations from QGIS by generating multiple static frames (images)
    and then combining those frames into an animation. The user tells QGIS how the frames
    should change from one to the other. In `QGIS 3.26` and later the animated markers
    allow markers to be animated without the use of the expressions system.
    &nbsp;<!-- blank space -->

- **How do the animated markers work?**

    In the code snippet below, the user tells QGIS that as the frame count increments by
    one the `Raster Image Marker` should change to the next image in the sequence.

    ![Code Snippet](img/014_FishExpression_1.png)

    The user specifies the path of the image (`@project_home/fish/fish_00`). Then the
    `lpad(to_string( @frame_number % 32), 2, '0')` tells QGIS to convert the frame
    number to a string and then modulus the number of frames by the number of animation
    frames (`32`) (i.e. QGIS divides the number of frames by 32 and then repeats the
    sequence when the remainder is zero). The `2` and `'0'` in the snippet tell
    QGIS to pad the `/fish/fish_00` with two zeroes at the end. Finally the `'.png'` tells
    QGIS the type of file to finish off the path.
    &nbsp;<!-- blank space -->

- **Frame Output location on Windows**

    For users on a Windows machine who are interested in seeing the frames before they
    are combined into an animation (GIF or movie) you can find them by going to
    "C:\Users\Username\AppData\Local\Temp\animation_workbench-0000000000.png". Bear in
    mind that AppData is a hidden file, so it's preferable to not make changes unless
    explicitly told otherwise.
    &nbsp;<!-- blank space -->

- **Frame Output on Linux**

    The frames should be in your /tmp directory.
