# 🧮 QGIS Expression Variables

The animation workbench exposes or modifies a number of different QGIS Expression variables that you can use to achieve different dynamic rendering effects.

## Common variables

These variables will always be available, regardless of the animation mode

| Variable          | Notes                                                               |
| ----------------- | ------------------------------------------------------------------- |
| frame_number      | Frame number within the current dwell or pan range.                 |
| frame_rate        | Number of frames per second that the video will be rendered at.     |
| total_frame_count | Total number of frames for the whole animation across all features. |

## Fixed extent mode variables (with layer)

These variables are available when in the fixed extent animation mode when a vector layer has been set

| Variable                 | Notes                                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------------|
| hover_feature            | The feature we are currently hovering over                                                             |
| hover_feature_id         | Feature ID for the feature we a current hovering over                                                  |
| previous_feature         | The previously visited feature (or NULL if there isn't one)                                            |
| previous_feature_id      | Feature ID for the previously visited feature (or NULL if there isn't one)                             |
| next_feature             | The next feature to visit after the current one (or NULL if there isn't one)                           |
| next_feature_id          | Feature ID for the next feature to visit after the current one (or NULL if there isn't one)            |
| current_hover_frame      | The frame number for the current feature (i.e. how many frames we have hovered at the current feature) |
| hover_frames             | Number of frames we will hover at the current feature for                                              |
| current_animation_action | Always "Hovering"                                                                                      |

## Planar/Sphere modes

These variables are available in the Planar or Sphere mode.

| Variable                 | Notes                             |
|--------------------------|-----------------------------------|
| current_animation_action | Either "Hovering" or "Travelling" |

### When hovering

These variables are available in planar or sphere mode, when the animation is currently hovering over a feature

| Variable            | Notes                                                                                                  |
|---------------------|--------------------------------------------------------------------------------------------------------|
| hover_feature       | The feature we are currently hovering over                                                             |
| hover_feature_id    | The feature ID for the feature we are currently hovering over                                          |
| previous_feature    | The previously visited feature (or NULL if there isn't one)                                            |
| previous_feature_id | Feature ID for the previously visited feature (or NULL if there isn't one)                             |
| next_feature        | The next feature to visit after the current one (or NULL if there isn't one)                           |
| next_feature_id     | Feature ID for the next feature to visit after the current one (or NULL if there isn't one)            |
| current_hover_frame | The frame number for the current feature (i.e. how many frames we have hovered at the current feature) |
| hover_frames        | Number of frames we will hover at the current feature for                                              |

### When travelling

These variables are available in planar or sphere mode, when the animation is currently travelling between two features

| Variable             | Notes                                                        |
|----------------------|--------------------------------------------------------------|
| from_feature         | The feature we are travelling away from                      |
| from_feature_id      | The feature ID for the feature we are travelling away from   |
| to_feature           | The feature we are heading toward                            |
| to_feature_id        | The feature ID for the feature we are heading toward         |
| current_travel_frame | The frame number for the current travel operation            |
| travel_frames        | Number of frames we will travel between the current features |

## Example expressions

Visit the [snippets section](snippets.md) of our documentation for example expressions.
