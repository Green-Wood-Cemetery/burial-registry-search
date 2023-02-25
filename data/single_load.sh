  echo "python clean_data.py -index ${2} -vol ${1}"
  python clean_data.py -index ${2} -vol ${1}

  echo "python import_data.py -file json/greenwood-volume-${1}.json -index ${2}"
  python import_data.py -file json/greenwood-volume-${1}.json -index ${2}