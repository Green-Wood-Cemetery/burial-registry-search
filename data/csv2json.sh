# greenwod
wget "https://docs.google.com/spreadsheets/d/1PLGDTjWzHjCrs7bNgvSO7zmcsZPZ7sSPVxSGtEWjpx4/export?format=csv&gid=824561781" -O "./csv/greenwood-google-sheet.csv"
csvtojson ./csv/greenwood-google-sheet.csv | jq 'map(. + { "birth_location": {"lat": (.birth_lat)|tonumber, "lon": (.birth_lon)|tonumber} })' | jq 'map(. + { "death_location": {"lat": (.death_lat)|tonumber, "lon": (.death_lon)|tonumber} })' | jq 'map(del(.birth_lat, .birth_lon, .death_lat, .death_lon))' > ./json/greenwood-es.json

# occ
wget "https://docs.google.com/spreadsheets/d/1PLGDTjWzHjCrs7bNgvSO7zmcsZPZ7sSPVxSGtEWjpx4/export?format=csv&gid=678512643" -O "./csv/occ-google-sheet.csv"
# csvtojson ./csv/occ-google-sheet.csv | jq 'map(. + { "birth_location": {"lat": (.birth_lat)|tonumber, "lon": (.birth_lon)|tonumber} })' | jq 'map(. + { "death_location": {"lat": (.death_lat)|tonumber, "lon": (.death_lon)|tonumber} })' | jq 'map(del(.birth_lat, .birth_lon, .death_lat, .death_lon))' > ./json/occ-es.json
csvtojson ./csv/occ-google-sheet.csv > ./json/occ-es.json