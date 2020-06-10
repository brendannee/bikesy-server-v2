FROM osrm/osrm-backend:latest

# defaults to standard bike direction/port 5000
# to run multiple servers pass as runtime args to docker build
ARG profile=bicycle.lua

RUN mkdir /data

# create custom bicycle profile
COPY ./profiles/$profile $profile

# add libs not present in OSRM
COPY ./profiles/lib/csv.lua lib/csv.lua
COPY ./profiles/lib/log.lua lib/log.lua
COPY ./profiles/lib/elevation.lua lib/elevation.lua

# copy bay area OSM and elevation data
# these need to be built separately when updating build
# if useful, can instead host on S3 or something
COPY ./data/elevation_sample.csv data/elevation.csv
COPY ./data/bay_area.osm.pbf data/bay_area.osm.pbf

# extract and comppile using bicycle profile
RUN osrm-extract -p $profile data/bay_area.osm.pbf
RUN osrm-partition data/bay_area.osrm
RUN osrm-customize data/bay_area.osrm

# show help for route API
RUN osrm-routed --help

# compile and run (on port 5000)
# docker build -t bike-mapper docker
# docker run -t -i -p 5000:5000 bike-mapper osrm-routed --algorithm mld ./data/bay_area.osrm