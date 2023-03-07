echo "Converting from Excel to JSON..."
for i in {01..60}
do
  if [[ $i -lt 10 ]]
  then
    echo "python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_0${i}_processed_SL_COMPLETE.xlsx -vol ${i} > json/greenwood-volume-${i}.json"
    python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_0${i}_processed_SL_COMPLETE.xlsx -vol ${i} > json/greenwood-volume-${i}.json
  else
    echo "python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_${i}_processed_SL_COMPLETE.xlsx -vol ${i} > json/greenwood-volume-${i}.json"
    python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_${i}_processed_SL_COMPLETE.xlsx -vol ${i} > json/greenwood-volume-${i}.json
  fi

done

echo "Validate Duplicates Globally..."
python3 validate_duplicates_global.py -folder json



