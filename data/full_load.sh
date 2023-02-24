echo "Importing JSON into ElasticSearch..."
for i in {01..60}
do
  echo "python clean_data.py -index test-auto -vol ${i}"
  python clean_data.py -index test-auto -vol ${i}

  echo "python import_data.py -file json/greenwood-volume-${i}.json -index test-auto"
  python import_data.py -file json/greenwood-volume-${i}.json -index test-auto

done



