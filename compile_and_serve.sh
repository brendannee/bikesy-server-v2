docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/bicycle.lua /data/SanFrancisco.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/SanFrancisco.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/SanFrancisco.osrm
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/SanFrancisco.osrm
