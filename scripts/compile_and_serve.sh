./osrm-backend/build/osrm-extract -p ./profiles/bicycle.lua bay_area.osm.pbf
./osrm-backend/build/osrm-partition bay_area.osrm
./osrm-backend/build/osrm-customize bay_area.osrm
./osrm-backend/build/osrm-routed --algorithm mld bay_area.osrm

