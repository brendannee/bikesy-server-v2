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
#### OSM
```
mkdir -p data
curl -o ./data/california-latest.osm.bz2 https://download.geofabrik.de/north-america/us/california-latest.osm.bz2
gunzip ./data/california-latest.osm.bz2
```

#### Extract Bay Area (needed for OSRM)
```
bzcat ./data/california-latest.osm.bz2 | osmosis --read-xml file=- --bounding-box left=-123.404077 bottom=37.171696 top=38.619150 right=-121.674775 --write-pbf ./data/bay_area.osm.pbf
```

#### Load Postgres DB For Investigation
```
psql -c "create database bikemapper;" -d postgres -U postgres
psql -c "create extension postgis; create extension hstore;" -d bikemapper -U postgres
psql -f /usr/local/Cellar/osmosis/0.47/libexec/script/pgsnapshot_schema_0.6.sql -d bikemapper -U postgres
osmosis --read-xml file=./data/bay_area.osm --write-pgsql host=localhost database=bikemapper user=postgres
```

#### USGS Elevation
Highest resolution is 1/3rd arc second.  Adjust lat/lng as needed (values represent top-right corner of 1-degree bounding box.
You can play with tile size (100x100) - this will impact loading vs. access time because index is on each cell.
You can download from [nationalmap.gov](https://viewer.nationalmap.gov/basic/#productSearch) or directly if you know the lat/lon you are looking for.

For N38W122 to N39W123:
```
for lat in 38 39; do
    for lng in 122 123; do
        # download USGS 1/3rd arc second data
        curl -o ./data/USGS_13_n${lat}w${lng}.tif https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/n${lat}w${lng}/USGS_13_n${lat}w${lng}.tif;
    done;
done
```
Assuming all data are in correct folders, run:

```
pip3 install -r requirements.txt
python3 elevation_mapper.py
```

This will write a file, elevation.csv, with a mapping from node_id to elevation in meters.  Any errors are recorded in errors.csv.

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

## Other half-baked ideas / to-dos

You can create postgis map of only bike lanes using the following SQL:
```
create temporary sequence tmp;
create table bikelanes as select nextval('tmp') as id, way_id, cycleway, st_makeline(geom) as geom from (select way_id, ways.tags -> 'cycleway' as cycleway, ways.tags -> 'geom, sequence_id from ways join way_nodes on (ways.id = way_nodes.way_id) join nodes on (nodes.id = way_nodes.node_id) where ways.tags -> 'cycleway' is not null order by way_id, sequence_id) foo group by way_id, cycleway;
```

### [Elevation Plugin](https://github.com/locked-fg/osmosis-srtm-plugin)
Installed as submodule.  Follow above link for any installation issues.
```
mkdir -p /usr/local/Cellar/osmosis/0.47/bin/plugins
jar cf /usr/local/Cellar/osmosis/0.47/bin/plugins/srtm.jar ./osmosis-srtm-plugin/src/main/java/de/locked/osmosis/srtmplugin/*.java
echo "de.locked.osmosis.srtmplugin.SrtmPlugin_loader" > /usr/local/Cellar/osmosis/0.47/libexec/config/osmosis-plugins.conf
```



