<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.24.3-Tisler">
  <renderer-v2 referencescale="-1" forceraster="0" symbollevels="1" type="singleSymbol" enableorderby="0">
    <symbols>
      <symbol force_rhr="0" name="0" alpha="1" clip_to_extent="1" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" pass="1" locked="0" class="GeometryGenerator">
          <Option type="Map">
            <Option name="SymbolType" value="Line" type="QString"/>
            <Option name="geometryModifier" value="with_variable('full_line',&#xa;wave_randomized( &#xa;&#x9;make_line(  &#xa;&#x9;&#x9;centroid( $geometry ), &#xa;&#x9;&#x9;centroid(geometry(@hover_feature) ) ), &#xa;&#x9;&#x9;10, 20, 1, 5, $id&#xa;&#x9;),&#xa;&#x9;wave_randomized( &#xa;&#x9;&#x9;make_line(&#xa;&#x9;&#x9;&#x9;line_interpolate_point(@full_line, &#xa;&#x9;&#x9;&#x9;&#x9;(@current_hover_frame / @hover_frames) * length(&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;@full_line)),&#xa;&#x9;&#x9;&#x9;&#x9;centroid(geometry(@hover_feature))&#xa;&#x9;&#x9;),10, 20, 1, 5, $id&#xa;&#x9;)&#xa;)" type="QString"/>
            <Option name="units" value="MapUnit" type="QString"/>
          </Option>
          <prop v="Line" k="SymbolType"/>
          <prop v="with_variable('full_line',&#xa;wave_randomized( &#xa;&#x9;make_line(  &#xa;&#x9;&#x9;centroid( $geometry ), &#xa;&#x9;&#x9;centroid(geometry(@hover_feature) ) ), &#xa;&#x9;&#x9;10, 20, 1, 5, $id&#xa;&#x9;),&#xa;&#x9;wave_randomized( &#xa;&#x9;&#x9;make_line(&#xa;&#x9;&#x9;&#x9;line_interpolate_point(@full_line, &#xa;&#x9;&#x9;&#x9;&#x9;(@current_hover_frame / @hover_frames) * length(&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;@full_line)),&#xa;&#x9;&#x9;&#x9;&#x9;centroid(geometry(@hover_feature))&#xa;&#x9;&#x9;),10, 20, 1, 5, $id&#xa;&#x9;)&#xa;)" k="geometryModifier"/>
          <prop v="MapUnit" k="units"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol force_rhr="0" name="@0@0" alpha="1" clip_to_extent="1" type="line">
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" value="" type="QString"/>
                <Option name="properties"/>
                <Option name="type" value="collection" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer enabled="1" pass="0" locked="0" class="MarkerLine">
              <Option type="Map">
                <Option name="average_angle_length" value="4" type="QString"/>
                <Option name="average_angle_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="average_angle_unit" value="MM" type="QString"/>
                <Option name="interval" value="11.8" type="QString"/>
                <Option name="interval_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="interval_unit" value="MM" type="QString"/>
                <Option name="offset" value="0" type="QString"/>
                <Option name="offset_along_line" value="0" type="QString"/>
                <Option name="offset_along_line_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_along_line_unit" value="MM" type="QString"/>
                <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                <Option name="offset_unit" value="MM" type="QString"/>
                <Option name="place_on_every_part" value="true" type="bool"/>
                <Option name="placements" value="Interval" type="QString"/>
                <Option name="ring_filter" value="0" type="QString"/>
                <Option name="rotate" value="1" type="QString"/>
              </Option>
              <prop v="4" k="average_angle_length"/>
              <prop v="3x:0,0,0,0,0,0" k="average_angle_map_unit_scale"/>
              <prop v="MM" k="average_angle_unit"/>
              <prop v="11.8" k="interval"/>
              <prop v="3x:0,0,0,0,0,0" k="interval_map_unit_scale"/>
              <prop v="MM" k="interval_unit"/>
              <prop v="0" k="offset"/>
              <prop v="0" k="offset_along_line"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_along_line_map_unit_scale"/>
              <prop v="MM" k="offset_along_line_unit"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="true" k="place_on_every_part"/>
              <prop v="Interval" k="placements"/>
              <prop v="0" k="ring_filter"/>
              <prop v="1" k="rotate"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" value="" type="QString"/>
                  <Option name="properties"/>
                  <Option name="type" value="collection" type="QString"/>
                </Option>
              </data_defined_properties>
              <symbol force_rhr="0" name="@@0@0@0" alpha="1" clip_to_extent="1" type="marker">
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" value="" type="QString"/>
                    <Option name="properties"/>
                    <Option name="type" value="collection" type="QString"/>
                  </Option>
                </data_defined_properties>
                <layer enabled="1" pass="0" locked="0" class="SimpleMarker">
                  <Option type="Map">
                    <Option name="angle" value="0" type="QString"/>
                    <Option name="cap_style" value="square" type="QString"/>
                    <Option name="color" value="255,0,0,255" type="QString"/>
                    <Option name="horizontal_anchor_point" value="1" type="QString"/>
                    <Option name="joinstyle" value="bevel" type="QString"/>
                    <Option name="name" value="circle" type="QString"/>
                    <Option name="offset" value="0,0" type="QString"/>
                    <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="offset_unit" value="MM" type="QString"/>
                    <Option name="outline_color" value="35,35,35,255" type="QString"/>
                    <Option name="outline_style" value="no" type="QString"/>
                    <Option name="outline_width" value="0" type="QString"/>
                    <Option name="outline_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="outline_width_unit" value="MM" type="QString"/>
                    <Option name="scale_method" value="diameter" type="QString"/>
                    <Option name="size" value="2" type="QString"/>
                    <Option name="size_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
                    <Option name="size_unit" value="MM" type="QString"/>
                    <Option name="vertical_anchor_point" value="1" type="QString"/>
                  </Option>
                  <prop v="0" k="angle"/>
                  <prop v="square" k="cap_style"/>
                  <prop v="255,0,0,255" k="color"/>
                  <prop v="1" k="horizontal_anchor_point"/>
                  <prop v="bevel" k="joinstyle"/>
                  <prop v="circle" k="name"/>
                  <prop v="0,0" k="offset"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="35,35,35,255" k="outline_color"/>
                  <prop v="no" k="outline_style"/>
                  <prop v="0" k="outline_width"/>
                  <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
                  <prop v="MM" k="outline_width_unit"/>
                  <prop v="diameter" k="scale_method"/>
                  <prop v="2" k="size"/>
                  <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
                  <prop v="MM" k="size_unit"/>
                  <prop v="1" k="vertical_anchor_point"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" value="" type="QString"/>
                      <Option name="properties" type="Map">
                        <Option name="fillColor" type="Map">
                          <Option name="active" value="true" type="bool"/>
                          <Option name="expression" value="@current_hover_frame" type="QString"/>
                          <Option name="transformer" type="Map">
                            <Option name="d" type="Map">
                              <Option name="colorramp" type="Map">
                                <Option name="name" value="[source]" type="QString"/>
                                <Option name="properties" type="Map">
                                  <Option name="color1" value="247,251,255,255" type="QString"/>
                                  <Option name="color2" value="8,48,107,255" type="QString"/>
                                  <Option name="direction" value="ccw" type="QString"/>
                                  <Option name="discrete" value="0" type="QString"/>
                                  <Option name="rampType" value="gradient" type="QString"/>
                                  <Option name="spec" value="rgb" type="QString"/>
                                  <Option name="stops" value="0.13;222,235,247,255;rgb;ccw:0.26;198,219,239,255;rgb;ccw:0.39;158,202,225,255;rgb;ccw:0.52;107,174,214,255;rgb;ccw:0.65;66,146,198,255;rgb;ccw:0.78;33,113,181,255;rgb;ccw:0.9;8,81,156,255;rgb;ccw" type="QString"/>
                                </Option>
                                <Option name="type" value="gradient" type="QString"/>
                              </Option>
                              <Option name="curve" type="Map">
                                <Option name="x" value="0,0.07847533632286996,0.35650224215246634,0.67264573991031396,1" type="QString"/>
                                <Option name="y" value="0,0.53846153846153844,0.47252747252747251,0.78021978021978022,1" type="QString"/>
                              </Option>
                              <Option name="maxValue" value="50" type="double"/>
                              <Option name="minValue" value="0" type="double"/>
                              <Option name="nullColor" value="0,0,0,255" type="QString"/>
                              <Option name="rampName" value="" type="QString"/>
                            </Option>
                            <Option name="t" value="2" type="int"/>
                          </Option>
                          <Option name="type" value="3" type="int"/>
                        </Option>
                        <Option name="size" type="Map">
                          <Option name="active" value="true" type="bool"/>
                          <Option name="expression" value="@current_hover_frame" type="QString"/>
                          <Option name="transformer" type="Map">
                            <Option name="d" type="Map">
                              <Option name="curve" type="Map">
                                <Option name="x" value="0,0.07174887892376682,0.25784753363228702,0.56950672645739908,0.81390134529147984,1" type="QString"/>
                                <Option name="y" value="0,0.76923076923076927,0.78021978021978022,0.8351648351648352,0.2857142857142857,0" type="QString"/>
                              </Option>
                              <Option name="exponent" value="1" type="double"/>
                              <Option name="maxSize" value="3" type="double"/>
                              <Option name="maxValue" value="50" type="double"/>
                              <Option name="minSize" value="0.01" type="double"/>
                              <Option name="minValue" value="0" type="double"/>
                              <Option name="nullSize" value="0" type="double"/>
                              <Option name="scaleType" value="0" type="int"/>
                            </Option>
                            <Option name="t" value="1" type="int"/>
                          </Option>
                          <Option name="type" value="3" type="int"/>
                        </Option>
                      </Option>
                      <Option name="type" value="collection" type="QString"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </layer>
          </symbol>
        </layer>
        <layer enabled="1" pass="0" locked="0" class="SimpleFill">
          <Option type="Map">
            <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            <Option name="color" value="0,0,255,255" type="QString"/>
            <Option name="joinstyle" value="bevel" type="QString"/>
            <Option name="offset" value="0,0" type="QString"/>
            <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            <Option name="offset_unit" value="MM" type="QString"/>
            <Option name="outline_color" value="35,35,35,255" type="QString"/>
            <Option name="outline_style" value="solid" type="QString"/>
            <Option name="outline_width" value="0.26" type="QString"/>
            <Option name="outline_width_unit" value="MM" type="QString"/>
            <Option name="style" value="no" type="QString"/>
          </Option>
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="0,0,255,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="no" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="outlineStyle" type="Map">
                  <Option name="active" value="true" type="bool"/>
                  <Option name="expression" value="if(@hover_feature_id = $id, 'solid','no')" type="QString"/>
                  <Option name="type" value="3" type="int"/>
                </Option>
              </Option>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
