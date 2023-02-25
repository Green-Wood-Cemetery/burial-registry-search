# python3 excel_to_es_json.py -file excel/output/Volume_16_processed.xlsx -vol 16 > json/greenwood-volume-16.json
#python3 excel_to_es_json.py -file excel/output/Volume_17_processed.xlsx -vol 17 > json/greenwood-volume-17.json
#python3 excel_to_es_json.py -file excel/output/Volume_18_processed.xlsx -vol 18 > json/greenwood-volume-18.json
#python3 excel_to_es_json.py -file excel/output/Volume_19_processed.xlsx -vol 19 > json/greenwood-volume-19.json

#python3 excel_to_es_json.py -file excel/output/Volume_20_processed.xlsx -vol 20 > json/greenwood-volume-20.json
#python3 excel_to_es_json.py -file excel/output/Volume_21_processed.xlsx -vol 21 > json/greenwood-volume-21.json
#python3 excel_to_es_json.py -file excel/output/Volume_22_processed.xlsx -vol 22 > json/greenwood-volume-22.json
#python3 excel_to_es_json.py -file excel/output/Volume_26_processed.xlsx -vol 26 > json/greenwood-volume-26.json
#python3 excel_to_es_json.py -file excel/output/Volume_27_processed.xlsx -vol 27 > json/greenwood-volume-27.json
#python3 excel_to_es_json.py -file excel/output/Volume_28_processed.xlsx -vol 28 > json/greenwood-volume-28.json
#python3 excel_to_es_json.py -file excel/output/Volume_29_processed.xlsx -vol 29 > json/greenwood-volume-29.json

#python3 excel_to_es_json.py -file excel/output/Volume_30_processed.xlsx -vol 30 > json/greenwood-volume-30.json
#python3 excel_to_es_json.py -file excel/output/Volume_31_processed.xlsx -vol 31 > json/greenwood-volume-31.json
#python3 excel_to_es_json.py -file excel/output/Volume_32_processed.xlsx -vol 32 > json/greenwood-volume-32.json
#python3 excel_to_es_json.py -file excel/output/Volume_33_processed.xlsx -vol 33 > json/greenwood-volume-33.json

#python3 excel_to_es_json.py -file excel/output/Volume_34_processed.xlsx -vol 34 > json/greenwood-volume-34.json
#python3 excel_to_es_json.py -file excel/output/Volume_38_processed.xlsx -vol 38 > json/greenwood-volume-38.json
#python3 excel_to_es_json.py -file excel/output/Volume_39_processed.xlsx -vol 39 > json/greenwood-volume-39.json
#python3 excel_to_es_json.py -file excel/output/Volume_40_processed.xlsx -vol 40 > json/greenwood-volume-40.json
#python3 excel_to_es_json.py -file excel/output/Volume_41_processed.xlsx -vol 41 > json/greenwood-volume-41.json

# process spreadsheets reviewed by Stacy
# FAILED - too many columns, should be A-DC not A-DE
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_22_processed_SL_COMPLETE.xlsx -vol 22 > json/greenwood-volume-22.json
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_22_processed_SL_COMPLETE_fixed.xlsx -vol 22 > json/greenwood-volume-22.json
# SUCCESS
# python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_26_processed_SL_COMPLETE.xlsx -vol 26 > json/greenwood-volume-26.json
# SUCCESS
# python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_27_processed_SL_COMPLETE.xlsx -vol 27 > json/greenwood-volume-27.json
# SUCCESS
# python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_32_processed_SL_COMPLETE.xlsx -vol 32 > json/greenwood-volume-32.json
# SUCCESS
# python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_33_processed_SL_COMPLETE.xlsx -vol 33 > json/greenwood-volume-33.json
# FAILED - too many columns, should be A-DC, not A-DD
# python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_38_processed_SL_COMPLETE.xlsx -vol 38 > json/greenwood-volume-38.json
# python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_38_processed_SL_COMPLETE_fixed.xlsx -vol 38 > json/greenwood-volume-38.json

# Apr 24, 2022
# removed the first two empty rows (no interment ids)
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_29_processed_SL_COMPLETE.xlsx -vol 29 > json/greenwood-volume-29.json
# removed the first empty row (no interment id)
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_30_processed_SL_COMPLETE.xlsx -vol 30 > json/greenwood-volume-30.json
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_34_processed_SL_COMPLETE.xlsx -vol 34 > json/greenwood-volume-34.json
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_39_processed_SL_COMPLETE.xlsx -vol 39 > json/greenwood-volume-39.json
# python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_40_processed_SL_COMPLETE.xlsx -vol 40 > json/greenwood-volume-40.json

# July 22, 2022
# fixes bad year data throughout
#python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_27_processed_SL_COMPLETE.xlsx -vol 27 > json/greenwood-volume-27.json
#python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_33_processed_SL_COMPLETE.xlsx -vol 33 > json/greenwood-volume-33.json
#python3 excel_to_es_json.py --geocode -file excel/reviewed/Volume_38_processed_SL_COMPLETE_fixed.xlsx -vol 38 > json/greenwood-volume-38.json
#python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_40_processed_SL_COMPLETE.xlsx -vol 40 > json/greenwood-volume-40.json
python3 excel_to_es_json.py --no-geocode -file excel/reviewed/Volume_${1}_processed_SL_COMPLETE.xlsx -vol ${1} > json/greenwood-volume-${1}.json

