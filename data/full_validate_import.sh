echo "Validating import..."
for i in {01..60}
do
  python3 validate_index.py  -file json/greenwood-volume-${i}.json -index ${1} -vol ${i}
done
