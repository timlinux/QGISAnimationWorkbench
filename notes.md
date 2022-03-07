How to extract a gif to a sequence of images:

```
convert cat.gif -coalesce cat_%05d.png
```

Example of how to create a dynamically changing image based on the current frame count:


```
@project_home 
||
'/gifs/swing_000'
|| 
lpad(to_string( @current_frame % 48 ), 2, '0') 
|| 
'.png'
```

Generate a movie from the scenes:

```
ffmpeg -y -framerate 30 -pattern_type glob -i "/tmp/globe-*.png" -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white" -c:v libx264 -pix_fmt yuv420p movie.mp4
```

Project variables:

        task_scope.setVariable('current_point_id', current_point_id)
        task_scope.setVariable('frames_per_point', self.frames_per_point)
        task_scope.setVariable('current_frame_for_point', current_frame)        
        task_scope.setVariable('current_animation_action', action)     
        task_scope.setVariable('current_frame', self.image_counter)        
        task_scope.setVariable('total_frame_count', self.total_frame_count)     
