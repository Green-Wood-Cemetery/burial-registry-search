#!/usr/bin/python

import pandas as pd
import json
import ast
import argparse
import sys
import datetime
import re
import logging
import time

parser = argparse.ArgumentParser(description="Converts XLSX to Elasticsearch JSON")
parser.add_argument("-url", type=str, help="spreadsheet url")
parser.add_argument("-file", type=str, help="spreadsheet file")
parser.add_argument("-vol", type=int, help="registry volume number")
parser.add_argument("--geocode", action=argparse.BooleanOptionalAction, help="process geocoded locations")
args = parser.parse_args()


# logging config
timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(
    filename="logs/excel_to_es-volume-" + str(args.vol) + "-" + timestr + ".csv", filemode="a", format="%(message)s"
)

volume = args.vol

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
    "has_diagram",
]

if args.url:
    df = pd.read_excel(args.url, names=new_cols, usecols="A:CZ", keep_default_na=False)
elif args.file:
    df = pd.read_excel(args.file, names=new_cols, usecols="A:CZ", keep_default_na=False)
else:
    sys.exit("Please indicate input file or url.")

# replace NaN with empty string
df = df.fillna("")
es_dict = df.to_dict(orient="records")


def clear_field(texto):
    fixed_text = ("".join(c for c in texto if not c.isdigit() and c not in ['"'])).strip()
    fixed_text = fixed_text.replace("-", "").replace("- P", "").strip()
    fixed_text = "" if fixed_text == "?" else fixed_text
    return None if len(fixed_text) == 0 else fixed_text


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime) or isinstance(z, datetime.time):
            return (str(z).replace("00:00:00", "")).strip()
        else:
            return super().default(z)


# add cemetery and volume props
row_count = 0
parsed_data = []
for i in es_dict:
    if i["interment_id"] is not None:
        row_count = row_count + 1
        # add cemetery and volume props
        i["cemetery"] = "Green-Wood Cemetery, Brooklyn, NY, USA"
        i["registry_volume"] = str(volume) if volume > 9 else "0" + str(volume)

        # convert lat/lon strings to json
        if args.geocode:
            i["residence_place_geo_location"] = ast.literal_eval(i["residence_place_geo_location"])
            i["birth_place_geo_location"] = ast.literal_eval(i["birth_place_geo_location"])
            i["death_place_geo_location"] = ast.literal_eval(i["death_place_geo_location"])

        # convert empty values to numbers
        if (
            i["age_years"] in ["", "-", "69/70"]
            or i["age_years"] is None
            or str(i["age_years"]).strip() in ["289", "339", "664", "779", "788", "789", "809", "862"]
        ):
            i["age_years"] = 0

        if i["age_months"] == "" or i["age_months"] is None or i["age_months"] == "-":
            i["age_months"] = 0
        if i["age_days"] == "" or i["age_days"] is None or i["age_days"] == "-":
            i["age_days"] = 0
        if i["age_hours"] == "" or i["age_hours"] is None or i["age_hours"] == "-":
            i["age_hours"] = 0

        # fix bad lot owner values
        if i["is_lot_owner"] == 0:
            i["is_lot_owner"] = False
        if i["is_lot_owner"] == 1:
            i["is_lot_owner"] = True

        # fix bad has diagram values
        if i["has_diagram"] == 0:
            i["has_diagram"] = False
        if i["has_diagram"] == 1:
            i["has_diagram"] = True

        # more boolean conversions...
        if i["birth_geo_is_faulty"] == 0 or i["birth_geo_is_faulty"] == "FALSE":
            i["birth_geo_is_faulty"] = False
        if i["birth_geo_is_faulty"] == 1 or i["birth_geo_is_faulty"] == "TRUE":
            i["birth_geo_is_faulty"] = True

        if i["death_place_geo_is_faulty"] == 0 or i["death_place_geo_is_faulty"] == "FALSE":
            i["death_place_geo_is_faulty"] = False
        if i["death_place_geo_is_faulty"] == 1 or i["death_place_geo_is_faulty"] == "TRUE":
            i["death_place_geo_is_faulty"] = True

        if i["residence_place_geo_is_faulty"] == 0 or i["residence_place_geo_is_faulty"] == "FALSE":
            i["residence_place_geo_is_faulty"] = False
        if i["residence_place_geo_is_faulty"] == 1 or i["residence_place_geo_is_faulty"] == "TRUE":
            i["residence_place_geo_is_faulty"] = True

        if i["birth_geo_is_faulty"] == "UNKNOWN":
            i["birth_geo_is_faulty"] = True

        if i["death_place_geo_is_faulty"] == "UNKNOWN":
            i["death_place_geo_is_faulty"] = True

        if i["residence_place_geo_is_faulty"] == "UNKNOWN":
            i["residence_place_geo_is_faulty"] = True

        # need to catch cases where the reviewer changes number types to float
        # instead of integer when editing the spreadsheet
        # if isinstance(i["interment_id"], float):
        #    i["interment_id"] = int(i["interment_id"])
        if isinstance(i["interment_date_day_transcribed"], float):
            i["interment_date_day_transcribed"] = int(i["interment_date_day_transcribed"])
        if isinstance(i["interment_date_year_transcribed"], float):
            i["interment_date_year_transcribed"] = int(i["interment_date_year_transcribed"])
        if isinstance(i["age_years"], float):
            i["age_years"] = int(i["age_years"])
        if isinstance(i["age_months"], float):
            i["age_months"] = int(i["age_months"])
        if isinstance(i["age_days"], float):
            i["age_days"] = int(i["age_days"])
        if isinstance(i["age_hours"], float):
            i["age_hours"] = int(i["age_hours"])
        if isinstance(i["death_date_year_transcribed"], float):
            i["death_date_year_transcribed"] = int(i["death_date_year_transcribed"])

        if not i["has_diagram"]:
            i["has_diagram"] = False

        if args.geocode:
            if "death_place_geo_formatted_address_extra" in i:
                del i["death_place_geo_formatted_address_extra"]
            if "birth_geo_formatted_address_extra" in i:
                del i["birth_geo_formatted_address_extra"]
            if "residence_place_geo_formatted_address_extra" in i:
                del i["residence_place_geo_formatted_address_extra"]

        if isinstance(i["death_date_iso"], datetime.datetime):
            i["death_date_iso"] = i["death_date_iso"].strftime("%Y-%m-%d")

        # convert empty dates to 2099-12-31
        if len(str(i["death_date_iso"])) == 4:
            i["death_date_month_transcribed"] = "0"
            i["death_date_day_transcribed"] = "0"
            i["death_date_year_transcribed"] = i["death_date_iso"]
            i["death_day"] = "0"
            i["death_month"] = "0"
            i["death_year"] = i["death_date_iso"]
        elif len(str(i["death_date_iso"])) == 7:
            if "-" in i["death_date_iso"]:
                i["death_date_month_transcribed"] = i["death_date_iso"].split("-")[1]
                i["death_date_day_transcribed"] = "0"
                i["death_date_year_transcribed"] = i["death_date_iso"].split("-")[0]
                i["death_day"] = "0"
                i["death_month"] = i["death_date_iso"].split("-")[1]
                i["death_year"] = i["death_date_iso"].split("-")[0]
            else:
                i["death_date_month_transcribed"] = "0"
                i["death_date_day_transcribed"] = "0"
                i["death_date_year_transcribed"] = "0"
                i["death_day"] = "0"
                i["death_month"] = "0"
                i["death_year"] = "0"
        elif len(str(i["death_date_iso"])) == 10:
            if "-" in i["death_date_iso"] and len(i["death_date_iso"].split("-")) == 3:
                i["death_date_month_transcribed"] = i["death_date_iso"].split("-")[1]
                i["death_date_day_transcribed"] = i["death_date_iso"].split("-")[2]
                i["death_date_year_transcribed"] = i["death_date_iso"].split("-")[0]
                i["death_day"] = i["death_date_iso"].split("-")[2]
                i["death_month"] = i["death_date_iso"].split("-")[1]
                i["death_year"] = i["death_date_iso"].split("-")[0]
            else:
                i["death_date_month_transcribed"] = "0"
                i["death_date_day_transcribed"] = "0"
                i["death_date_year_transcribed"] = "0"
                i["death_day"] = "0"
                i["death_month"] = "0"
                i["death_year"] = "0"
        else:
            i["death_date_iso"] = "Not Known"
            i["death_date_month_transcribed"] = "0"
            i["death_date_day_transcribed"] = "0"
            i["death_date_year_transcribed"] = "0"
            i["death_day"] = "0"
            i["death_month"] = "0"
            i["death_year"] = "0"

        i["cause_of_death_display"] = clear_field(i["cause_of_death_display"])

        if i["marital_status"] and i["marital_status"] in [
            "Not recorded",
            "Married",
            "Single",
            "Widow",
            "Divorced",
            "Marriage Annulled",
            "Legally Separated",
            "Infant",
            "Separated",
            "Child",
        ]:
            i["marital_status"] = str(i["marital_status"]).strip()
        else:
            i["marital_status"] = "Unknown"

        # --- PARSE REGISTRY VOL AND PAGE
        try:
            m = re.search("[Vv]olume\s+(\d+)_(\d+)", i["registry_image"])
            if m is None:
                logging.warning("Unable to parse volume page: " + i["registry_image"] + " at row " + str(row_count))
                continue

            registry_volume = int(m.group(1))
            registry_page = int(m.group(2))
            i["registry_page"] = registry_page

            image_filename = f"Volume {registry_volume:02d}_{registry_page:03d}"
            i["registry_image"] = image_filename
        except re.error:
            logging.warning("Unable to parse volume page: " + i["registry_image"] + " at row " + str(row_count))
            continue

        parsed_data.append(i)
    else:
        logging.error("Rejected Record")
        logging.error(i)

# dump and print json
json_string = json.dumps(parsed_data, indent=2, sort_keys=False, cls=DateTimeEncoder)
print(json_string)
