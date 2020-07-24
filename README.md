# bikemapper-v2
Update to graphserver-based bike mapper.  Uses custom lua profiles based on existing bicycle model provided by OSRM.

## Installation and Prequisites

### Homebrew/XCode
Make sure you have XCode installed with command line tools (app store).
Homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew install osmosis boost git cmake libzip libstxxl libxml2 lua tbb ccache postgis
brew cask install docker
```

### Data
#### OSM
```
mkdir -p data
mkdir -p data/elevation
curl -o ./data/california-latest.osm.bz2 https://download.geofabrik.de/north-america/us/california-latest.osm.bz2
gunzip ./data/california-latest.osm.bz2
```

#### Extract Bay Area (needed for OSRM)
```
osmosis --read-xml file=./data/california-latest.osm --bounding-box left=-123.404077 bottom=37.171696 top=38.619150 right=-121.674775 --write-pbf ./data/bay_area.osm.pbf
```

#### Load Postgres DB For Investigation
```
psql -c "create database bikemapper;" -d postgres -U postgres
psql -c "create extension postgis; create extension hstore;" -d bikemapper -U postgres
psql -f /usr/local/Cellar/osmosis/0.48.2/libexec/script/pgsnapshot_schema_0.6.sql -d bikemapper -U postgres
osmosis --read-xml file=./data/bay_area.osm --write-pgsql host=localhost database=bikemapper user=postgres
```

#### USGS Elevation
Highest resolution is 1/3rd arc second.  Adjust lat/lng as needed (values represent top-right corner of 1-degree bounding box.
You can play with tile size (100x100) - this will impact loading vs. access time because index is on each cell.
Place all the files you need to cover the area in a directory ./data/elevation.  Note that the indexing is by top-right corner lat/lng.
You can download from [nationalmap.gov](https://viewer.nationalmap.gov/basic/#productSearch) or directly if you know the lat/lon you are looking for.

For N38W122 to N39W123:
```
for lat in 38 39; do
    for lng in 122 123; do
        # download USGS 1/3rd arc second data
        curl "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/n${lat}w${lng}/USGS_13_n${lat}w${lng}.tif" > "./data/elevation/USGS_13_n${lat}w${lng}.tif"
    done;
done
```
Assuming all data are in correct folders, run:

```
cd scripts
pip3 install -r requirements.txt
python3 elevation_mapper.py
```

This will write a file, elevation.csv, with a mapping from node_id to elevation in meters.  Any errors are recorded in errors.csv.

```
psql -c "drop table if exists node_elevation; create table node_elevation (node_id bigint, elevation float);" -d bikemapper -U postgres
elevationpath=$(find `pwd` -name elevation.csv)
echo "\COPY node_elevation from '${elevationpath}' with csv delimiter as ','" | psql -d bikemapper -U postgres
psql -c "alter table node_elevation add primary key (node_id);" -d bikemapper -U postgres
```

## OSRM
### Use modified version of docker file to host with custom profiles
#### Copy data needed to build
```
cp ./data/bay_area.osm.pbf ./docker/bay_area.osm.pbf
cp ./scripts/elevation.csv ./docker/elevation.csv
```
#### Build docker image
```
docker build -t bike-mapper docker
```
This image can be posted to a repository to deploy on heroku, etc.  To create custom profiles, pass argument to docker build and specify alternative name.
```
docker build -t bike-mapper-safe --build-arg profile=bicycle_extra_safe.lua docker
```
#### Host
```
docker run -t -i -p 5000:5000 bike-mapper osrm-routed --algorithm mld ./data/bay_area.osrm
```
Ideally you would run alternate images on different ports, e.g.
```
docker run -t -i -p 5001:5001 bike-mapper-safe osrm-routed --algorithm mld ./data/bay_area.osrm
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

docker pull osrm/osrm-backend
docker build -t bike-mapper-prepare docker/prepare


