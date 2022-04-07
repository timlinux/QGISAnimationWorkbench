# Snippets

## Line of travel

In this example we use a geometry generator to create a line between the origin point and the destination point:

```
if (@from_feature_id = $id OR @to_feature_id = $id,
	-- read this from inside to out so 
	-- last tranform the geometry back to the map crs
	transform( 
		-- densify the geometry so that when we transform
		-- back it makes a great circle
		densify_by_count(  
			-- move the geometry into a crs that 
			-- shows a great circle as a straight line
			transform( 
				-- make a line from the previous pont to the next point
				make_line( 
					geometry(@from_feature), 
					geometry(@to_feature)
				),  
				@map_crs, 'EPSG:4326'),
			99), 
		'EPSG:4326',  @map_crs),
	None)
```

![Example output](img/make-line.png)