echo "Converting from Excel to JSON..."
for i in {01..60}
do
  echo "python excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_${i}_processed_SL_COMPLETE.xlsx -vol ${i} > json/greenwood-volume-${i}.json"
  python excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_${i}_processed_SL_COMPLETE.xlsx -vol ${i} > json/greenwood-volume-${i}.json
done

echo "Validate Duplicates Globally..."
python validate_duplicates_global.py -folder json



