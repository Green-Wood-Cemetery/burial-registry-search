echo "Importing JSON into ElasticSearch..."
for i in {01..60}
do
  echo "python clean_data.py -index ${1} -vol ${i}"
  python3 clean_data.py -index ${1} -vol ${i}

  echo "python import_data.py -file json/greenwood-volume-${i}.json -index ${1}"
  python3 import_data.py -file json/greenwood-volume-${i}.json -index ${1}

  sleep 1m
done
