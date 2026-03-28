

NOTE: branch-2 needs to be pushed to remote first
* next merge branch-2 into main
* next pull code from main into branch-1
* during this time, merge will be needed on README file as well as data-files and constitution.

## work for branch-1

### Download Census TIGER/Line ZCTA shapefile for Florida and 
  convert to GeoJSON                                               
  pip install geopandas
  python - <<'EOF'                                                 
  import geopandas as gpd
  #### Census TIGER ZCTA5 shapefile URL (2022)                        
  url = "https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_202
  2_us_zcta520.zip"                                                
  gdf = gpd.read_file(url)                                         
  #### Filter to Jacksonville / Duval County ZIPs — adjust list as    
  needed                                                           
  jax_zips = gdf[gdf["ZCTA5CE20"].str.startswith(("320", "322"))]
  jax_zips.to_file("data/raw/jacksonville_zctas.geojson",          
  driver="GeoJSON")
  EOF     