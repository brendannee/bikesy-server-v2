import os
import rasterio
import sys
import esy.osm.pbf

input_file = sys.argv[1] if len(sys.argv) > 1 else 'bay_area'

DATA_DIR = './data/elevation'
ERROR_FILE = 'errors.csv'
OUTPUT_FILE = f'{DATA_DIR}/elevation.csv'
OSM_PATH = f'./data/{input_file}.osm.pbf'


def build_tif_file_name_nw(lat, lng):
    # note only works for northern / western hemispheres
    return f'USGS_13_n{lat}w{lng}.tif'

# load 
print("Loading geotiffs into memory")
geotiffs = {}
for tif in os.listdir(DATA_DIR):
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
                print(f"processed {nodes_processed} nodes", nodes_processed)
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
                    elevations.write(f'{entry.id},{elev},{lng},{lat}\n')

                except Exception as e:
                    print(f"Found error for id {entry.id}")
                    errors.write(f'{entry.id},{e}\n')
