log = require('lib/log')

-- copied from lua-csv submodule
csv = require('lib/csv')

log.info("LOADING ELEVATION")
local f = csv.open("./data/elevation.csv")
ElevationTable = {}
for fields in f:lines() do
    data = {}
    data['elevation'] = fields[2]
    data['lng'] = fields[3]
    data['lat'] = fields[4]
    ElevationTable[fields[1]] = data
end
log.info("FINISHED LOADING ELEVATION")

return ElevationTable

