The bash script grabs the google spreadsheet as a CSV file, converts it to JSON and transforms the geo points to nested JSON objects.

## Prerequisites

### elasticsearch-loader

see: [https://github.com/moshe/elasticsearch_loader](https://github.com/moshe/elasticsearch_loader)

install: `pip3 install elasticsearch-loader`

### node

### npm

### wget

### csvtojson

`npm i -g csvtojson`
see: [https://github.com/Keyang/node-csvtojson](https://github.com/Keyang/node-csvtojson)

### jq

see: [https://stedolan.github.io/jq/](https://stedolan.github.io/jq/)

### env vars

see: [https://vercel.com/green-wood/burial-registry-search/settings/environment-variables](https://vercel.com/green-wood/burial-registry-search/settings/environment-variables)