tmp = open('elevation_ids.txt')
ids = []
for id in tmp.readlines():
  ids.append(id.strip())
all_data = open('elevation.csv')
for line in all_data.readlines():
  id, elev, lng, lat = line.strip().split(',')
  if id in ids:
    print(f'{id},{elev},{lng},{lat}')
# print(ids)