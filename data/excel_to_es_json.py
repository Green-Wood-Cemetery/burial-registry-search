#!/usr/bin/python

import pandas as pd
import json
import ast

xslx_url = 'https://github.com/Green-Wood-Cemetery/burial-registry-search/blob/master/data/excel/output/Volume_33_processed.xlsx?raw=true'

volume = 33
# rename excel column headings to elasticsearch json values
new_cols = [
    "interment_id",
    "registry_image",
    "interment_date_month_transcribed",
    "interment_date_day_transcribed",
    "interment_date_year_transcribed",
    "interment_date_display",
    "interment_date_iso",
    "name_transcribed",
    "name_display",
    "name_last",
    "name_first",
    "name_middle",
    "name_salutation",
    "name_suffix",
    "is_lot_owner",
    "gender_guess",
    "burial_location_lot_transcribed",
    "burial_location_lot_current",
    "burial_location_lot_previous",
    "burial_location_grave_transcribed",
    "burial_location_grave_current",
    "burial_location_grave_previous",
    "birth_place_transcribed",
    "birth_place_displayed",
    "birth_geo_formatted_address",
    "birth_geo_is_faulty",
    "birth_geo_street_number",
    "birth_geo_street_name_long",
    "birth_geo_street_name_short",
    "birth_geo_neighborhood",
    "birth_geo_city",
    "birth_geo_county",
    "birth_geo_state_short",
    "birth_geo_state_long",
    "birth_geo_country_long",
    "birth_geo_country_short",
    "birth_geo_zip",
    "birth_geo_place_id",
    "birth_geo_formatted_address_extra",
    "birth_place_geo_location",
    "age_years_transcribed",
    "age_months_transcribed",
    "age_days_transcribed",
    "age_hours_transcribed",
    "age_display",
    "age_years",
    "age_months",
    "age_days",
    "age_hours",
    "marital_status_married_transcribed",
    "marital_status_single_transcribed",
    "marital_status",
    "residence_place_city_transcribed",
    "residence_place_city_display",
    "residence_place_street_transcribed",
    "residence_place_street_display",
    "residence_place_geo_formatted_address",
    "residence_place_geo_is_faulty",
    "residence_place_geo_street_number",
    "residence_place_geo_street_number_long",
    "residence_place_geo_street_number_short",
    "residence_place_geo_neighborhood",
    "residence_place_geo_city",
    "residence_place_geo_county",
    "residence_place_geo_state_short",
    "residence_place_geo_state_long",
    "residence_place_geo_country_long",
    "residence_place_geo_country_short",
    "residence_place_geo_zip",
    "residence_place_geo_place_id",
    "residence_place_geo_formatted_address_extra",
    "residence_place_geo_location",
    "death_place_transcribed",
    "death_place_display",
    "death_place_geo_formatted_address",
    "death_place_geo_is_faulty",
    "death_place_geo_street_number",
    "death_place_geo_street_number_long",
    "death_place_geo_street_number_short",
    "death_place_geo_neighborhood",
    "death_place_geo_city",
    "death_place_geo_county",
    "death_place_geo_state_short",
    "death_place_geo_state_long",
    "death_place_geo_country_long",
    "death_place_geo_country_short",
    "death_place_geo_zip",
    "death_place_geo_place_id",
    "death_place_geo_formatted_address_extra",
    "death_place_geo_location",
    "death_date_month_transcribed",
    "death_date_day_transcribed",
    "death_date_year_transcribed",
    "death_date_display",
    "death_date_iso",
    "death_date_ult_month",
    "cause_of_death_transcribed",
    "cause_of_death_display",
    "undertaker_transcribed",
    "undertaker_display",
    "remarks_transcribed",
    "remarks_display",
    "burial_origin",
    "has_diagram"
]

df = pd.read_excel(xslx_url, names=new_cols, usecols='A:CZ', keep_default_na=False)
es_dict = df.to_dict(orient='records')

# add cemetery and volume props
for i in es_dict:

    # add cemetery and volume props
    i["cemetery"] = "Green-Wood Cemetery, Brooklyn, NY, USA"
    i["registry_volume"] = volume

    # convert lat/lon strings to json
    i["residence_place_geo_location"] = ast.literal_eval(i["residence_place_geo_location"])
    i["birth_place_geo_location"] = ast.literal_eval(i["birth_place_geo_location"])
    i["death_place_geo_location"] = ast.literal_eval(i["death_place_geo_location"])

    # convert empty values to numbers
    if i["age_years"] == "":
        i["age_years"] = 0
    if i["age_months"] == "":
        i["age_months"] = 0
    if i["age_days"] == "":
        i["age_days"] = 0
    if i["age_hours"] == "":
        i["age_hours"] = 0

    if not i["has_diagram"]:
        i["has_diagram"] = False

    if "death_place_geo_formatted_address_extra" in i:
        del i["death_place_geo_formatted_address_extra"]
    if "birth_geo_formatted_address_extra" in i:
        del i["birth_geo_formatted_address_extra"]
    if "residence_place_geo_formatted_address_extra" in i:
        del i["residence_place_geo_formatted_address_extra"]

# dump and print json
json_string = json.dumps(es_dict, indent=2, sort_keys=False)
print(json_string)
