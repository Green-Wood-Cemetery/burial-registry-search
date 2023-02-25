echo "Validating import..."
echo "python3 validate_index.py  -file json/greenwood-volume-${1}.json -index ${2} -vol ${1}"
python3 validate_index.py  -file json/greenwood-volume-${1}.json -index ${2} -vol ${1}
