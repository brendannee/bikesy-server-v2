# extract sample from full elevation.csv for testing
# new file needs to be updated in docker/profiles/lib/elevation.lua
# as well as Dockerfile

tmp = open('elevation_ids.txt')
ids = []
for id in tmp.readlines():
  ids.append(id.strip())
all_data = open('elevation.csv')
for line in all_data.readlines():
  id, elev, lng, lat = line.strip().split(',')
  if id in ids:
    print(f'{id},{elev},{lng},{lat}')