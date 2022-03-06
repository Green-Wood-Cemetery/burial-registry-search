https://www.npmjs.com/package/json2csv
npm install -g json2csv
json2csv --flatten-objects -i json/greenwood-volume-11.json -o greenwood-volume-11-test.csv


pip3 install csvs-to-sqlite
csvs-to-sqlite csv/greenwood-volume-11-test.csv greenwood-volume-11-test.db

brew install datasette
datasette install datasette-cluster-map
datasette serve sqlite/greenwood-volume-11.db