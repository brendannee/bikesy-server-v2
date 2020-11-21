import os
import redis
import rasterio
import sys
import esy.osm.pbf
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--skip_redis', action='store_true')
parser.add_argument('--skip_file', action='store_true')
parser.add_argument('--input_file', default='bay_area')
args = parser.parse_args()

# heroku-redis
# credentials will be rotated, so you'll have to get from heroku web periodically
if not args.skip_redis:
    REDIS_URI = os.getenv("REDIS_URL")
    r = redis.from_url(REDIS_URI)
    pipe = r.pipeline()

DATA_DIR = './data/elevation'
ERROR_FILE = 'errors.csv'
OUTPUT_FILE = f'{DATA_DIR}/elevation.csv' if not args.skip_file else '/dev/null'
OSM_PATH = f'./data/{args.input_file}.osm.pbf'

def publish_to_redis(key, value):
    pipe.set(key, value)

def build_tif_file_name_nw(lat, lng):
    # note only works for northern / western hemispheres
    return f'USGS_13_n{lat}w{lng}.tif'

# load 
print("Loading geotiffs into memory")
geotiffs = {}
for tif in os.listdir(DATA_DIR):
    if tif.endswith(".tif"):
        print(f"processing {tif}")
        data = rasterio.open(f"{DATA_DIR}/{tif}")
        geotiffs[tif] = {
            'tif': data,
            'band': data.read(1)
        }

print("Loading OSM into memory")
osm = esy.osm.pbf.File(OSM_PATH)
nodes_processed = 0
with open(ERROR_FILE, 'w') as errors:
    with open(OUTPUT_FILE, 'w') as elevations:
        nodes_processed = nodes_processed + 1
        for entry in osm:
            if nodes_processed % 10000 == 0:
                print(f"processed {nodes_processed} nodes")
                if not args.skip_redis:
                    pipe.execute()
            nodes_processed = nodes_processed + 1
            # almost all nodes are part of way_node mapping, no need to further filter
            if entry.__class__ == esy.osm.pbf.file.Node:
                lonlat = entry.lonlat
                # this logic obviously can be improved but works for four tiles
                if lonlat[1] >= 38:
                    # top right/top left
                    tile = geotiffs[build_tif_file_name_nw(39, 122)] if lonlat[0] >= -122 else geotiffs[build_tif_file_name_nw(39, 123)]
                else:
                    # bottom right/bottom left
                    tile = geotiffs[build_tif_file_name_nw(38, 122)] if lonlat[0] >= -122 else geotiffs[build_tif_file_name_nw(38, 123)]
                try:
                    # save space with huge file: use only centimeter precision
                    # extract lat/lng also in this phase because lua doesn't make it easy
                    elev = '{:.2f}'.format(float(tile['band'][tile['tif'].index(lonlat[0], lonlat[1])]))
                    lat = '{:.6f}'.format(lonlat[1])
                    lng = '{:.6f}'.format(lonlat[0])
                    if not args.skip_file:
                        elevations.write(f'{entry.id},{elev},{lng},{lat}\n')
                    if not args.skip_redis:
                        publish_to_redis(entry.id, elev)
                except Exception as e:
                    print(f"Found error for id {entry.id}")
                    errors.write(f'{entry.id},{e}\n')
if not args.skip_redis:
    pipe.execute()
