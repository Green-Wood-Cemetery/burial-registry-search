  echo "python3 clean_data.py -index ${2} -vol ${1}"
  python3 clean_data.py -index ${2} -vol ${1}

  echo "python3 import_data.py -file json/greenwood-volume-${1}.json -index ${2}"
  python3 import_data.py -file json/greenwood-volume-${1}.json -index ${2}