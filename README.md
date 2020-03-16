# bikemapper-v2
Update to graphserver-based bike mapper.  Uses custom lua profiles based on existing bicycle model provided by OSRM.

## Installation and Prequisites

### Homebrew/XCode
Make sure you have XCode installed with command line tools (app store).
Homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew install osmosis boost git cmake libzip libstxxl libxml2 lua tbb ccache postgis
```

### Data
```
mkdir -p data
curl -o ./data/california-latest.osm.bz2 https://download.geofabrik.de/north-america/us/california-latest.osm.bz2
gunzip ./data/california-latest.osm.bz2
```

## Osmosis

### Extract Bay Area (needed for OSRM)
```
osmosis --read-xml file=./data/california-latest.osm --bounding-box left=-123.404077 bottom=37.171696 top=38.619150 right=-121.674775 --write-pbf ./data/bay_area.osm.pbf
```
Or alternately, work directly with [bzcat](https://wiki.openstreetmap.org/wiki/Osmosis#Extracting_bounding_boxes)

### Optional: Load Postgres DB For Investigation
```
psql -c "create database bikemapper;" -d postgres -U postgres
psql -c "create extension postgis; create extension hstore;" -d bikemapper -U postgres
psql -f /usr/local/Cellar/osmosis/0.47/libexec/script/pgsnapshot_schema_0.6.sql -d bikemapper -U postgres
osmosis --read-xml file=./data/bay_area.osm --write-pgsql host=localhost database=bikemapper user=postgres
```
You can create postgis map of only bike lanes using the following SQL:
```
create table bikelanes as select nextval('tmp') as id, way_id, cycleway, st_makeline(geom) as geom from (select way_id, ways.tags -> 'cycleway' as cycleway, geom, sequence_id from ways join way_nodes on (ways.id = way_nodes.way_id) join nodes on (nodes.id = way_nodes.node_id) where ways.tags -> 'cycleway' is not null order by way_id, sequence_id) foo group by way_id, cycleway;
```

## OSRM
### Install Submodule
```
git submodule init
git submodule update
```
### Build
See [OSRM documentation](https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM).
TO DO: contribute new bicycle lua files to repo and build using docker (recommended).
```
cd osrm-backend
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
sudo cmake --build . --target install
```
### Prepare Data (see compile_and_serve.sh)
```
./osrm-backend/build/osrm-extract -p ./profiles/bicycle.lua ./data/bay_area.osm.pbf
./osrm-backend/build/osrm-partition ./data/bay_area.osrm
./osrm-backend/build/osrm-customize ./data/bay_area.osrm
```

### Serve (Port 5000)
```
./osrm-backend/build/osrm-routed --algorithm mld ./data/bay_area.osrm
```

### Confirm the Wiggle
```
curl -s "http://127.0.0.1:5000/route/v1/driving/-122.424474,37.766237;-122.430911,37.779670?steps=false" | jq -r .routes[0].geometry
```
Should return
```
afoeFz~ejV]@lAdi@uS~@?h@iI`Ah@fI{Dd@h@hIiVtC~Bb^{Dd@|@bN
```

### [Easier Frontend](https://hub.docker.com/r/osrm/osrm-frontend/)
```
docker pull osrm/osrm-frontend
docker run -p 9966:9966 osrm/osrm-frontend
```
