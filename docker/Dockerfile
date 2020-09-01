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
COPY ./profiles/lib/haversine.lua lib/haversine.lua

# copy OSM and elevation data
# these need to be built separately when updating build
# if useful, can instead host on S3 or something
COPY ./data/elevation.csv data/elevation.csv
COPY ./data/extract.osm.pbf data/extract.osm.pbf

# extract and comppile using bicycle profile
# note: the -t option is to single thread the extraction process which is slightly slower
# when developing locally you typically don't have enough memory to load the elevation file for each thread (default 3)
# may want to consider changing when ready for production depending on the constraints of AWS machines

RUN osrm-extract -t 1 -p $profile data/extract.osm.pbf
RUN osrm-partition data/extract.osrm
RUN osrm-customize data/extract.osrm

# show help for route API
# RUN osrm-routed --help
CMD osrm-routed -t 1 -p $PORT --algorithm mld ./data/extract.osrm

# compile and run (on port 5000)
# docker build -t bike-mapper docker
# docker run -t 1 -i -p 5000:5000 bike-mapper osrm-routed --algorithm mld ./data/extract.osrm