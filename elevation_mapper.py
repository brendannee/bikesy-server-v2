import rasterio
import esy.osm.pbf

# load 
print("Loading geotiffs into memory")
geotiffs = (
    rasterio.open('./data/USGS_13_n39w122.tif'),
    rasterio.open('./data/USGS_13_n39w123.tif'),
    rasterio.open('./data/USGS_13_n38w122.tif'),
    rasterio.open('./data/USGS_13_n38w123.tif'),    
)
bands = [geotiff.read(1) for geotiff in geotiffs]

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
                    tiff = geotiffs[0] if lonlat[0] >= -122 else geotiffs[1]
                    band = bands[0] if lonlat[0] >= -122 else bands[1]
                else:
                    # bottom right/bottom left
                    tiff = geotiffs[2] if lonlat[0] >= -122 else geotiffs[3]
                    band = bands[2] if lonlat[0] >= -122 else bands[3]
                try:
                    elevations.write("{}, {}\n".format(entry.id, band[tiff.index(lonlat[0], lonlat[1])]))
                except Exception as e:
                    print(f"Found error for id {entry.id}")
                    errors.write("{}, {}\n".format(entry.id, e))
