import os
import rasterio
import esy.osm.pbf

data_dir = './data/elevation/'

def build_tif_file_name_nw(lat, lng):
    # note only works for northern / western hemispheres
    return 'USGS_13_n{}w{}.tif'.format(lat, lng)

# load 
print("Loading geotiffs into memory")
geotiffs = {}
for tif in os.listdir(data_dir):
    print(f"processing {tif}")
    data = rasterio.open(data_dir + tif)
    geotiffs[tif] = {
        'tif': data,
        'band': data.read(1)
    }

print("Loading OSM into memory")
osm = esy.osm.pbf.File('./data/bay_area.osm.pbf')
nodes_processed = 0
with open('errors.csv', 'w') as errors:
    with open('elevation.csv', 'w') as elevations:
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
                    elevations.write("{}, {}\n".format(entry.id, tile['band'][tile['tif'].index(lonlat[0], lonlat[1])]))

                except Exception as e:
                    print(f"Found error for id {entry.id}")
                    errors.write("{}, {}\n".format(entry.id, e))
