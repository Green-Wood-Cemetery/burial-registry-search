import json
import re
import dateparser
import requests
import logging
from nameparser import HumanName
from openpyxl import load_workbook
import argparse

# command line arguments
parser = argparse.ArgumentParser(description='Spreadsheet to JSON')
parser.add_argument('-input', type=str, help='spreadsheet in xslx format')
parser.add_argument('-key', type=str, help='google api key')
parser.add_argument('-sheet', type=str, help='worksheet to transform')
args = parser.parse_args()
workbook = load_workbook(filename=args.input, data_only=True)
GOOGLE_API_KEY = args.key
# sheet = workbook.active
sheet = workbook[args.sheet]

do_geocode_birth = False
do_geocode_residence = False
do_geocode_death = False
cemetery = "Green-Wood Cemetery, Brooklyn, NY, USA"


# load synonym dictionaries
with open('dictionaries/cause-of-death.json') as f:
  cause_of_death_dict = json.load(f)
with open('dictionaries/marital-status.json') as g:
    marital_status_dict = json.load(g)

def get_google_geocode_results(address_or_zipcode):
    results = None
    api_key = GOOGLE_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={address_or_zipcode}&key={api_key}"
    # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None, None
    try:
        '''
        This try block in case any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
    except:
        pass
    return results


interments = []

# Using the values_only because you want to return the cells' values
for row in sheet.iter_rows(min_row=3, values_only=True):

    if row[1] is not None:

        # --- TAGS (39)
        tags = []
        if row[39] is not None:
            tags = re.findall(r'"(.*?)"', row[39])

        # --- REGISTRY IMAGE FILENAME (0)
        image_filename = row[0]

        # --- PARSE REGISTRY VOL AND PAGE
        m = re.search('V\w+\s+(\d+)_(\d+)', image_filename)
        registry_volume = m.group(1)
        registry_page = m.group(2)

        # --- INTERMENT ID (1)
        interment_id = row[1]

        # --- INTERMENT DATE (2-4)
        interment_date_display = ''
        interment_date_iso = ''
        interment_year = ''
        # interment month
        if row[2] is not None and row[2] != '':
            interment_date_display += row[2] + " "
        # interment day
        if row[3] is not None and row[3] != '':
            interment_date_display += str(int(row[3])) + ", "
        # interment year
        if row[4] is not None and row[4] != '':
            interment_date_display += str(int(row[4]))
            interment_year = int(row[4])
        interment_date = ''
        if interment_date_display != '':
            dt = dateparser.parse(interment_date_display)
            if dt is not None:
                interment_date_iso = dt.strftime("%Y-%m-%d")

        # --- NAME (5-9)
        name_salutation = ''
        name_first = ''
        name_middle = ''
        name_last = ''
        name_infant = ''
        name_full = ''
        if row[5] is not None:
            name_salutation = row[5]
        if row[6] is not None:
            name_first = row[6]
        if row[7] is not None:
            name_middle = row[7]
        if row[8] is not None:
            name_last = row[8]

        name = HumanName(name_salutation + " " + name_first + " " + name_middle + " " + name_last)
        name_full = name.full_name

        if row[9] is not None:
            name_infant = row[9]
            if name_infant != '':
                name_full += " (" + name_infant + ")"

        #--- expand abbreviated first names in tags
        if name_first.lower() == "geo":
            if "George" not in tags:
                tags.append("George")
        if name_first.lower() == "wm":
            if "William" not in tags:
                tags.append("William")

        #--- BURIAL LOCATION (10-13)
        burial_location_current_lot = ''
        burial_location_current_grave = ''
        burial_location_previous_lot = ''
        burial_location_previous_grave = ''
        if row[10] is not None:
            burial_location_current_lot = row[10]
        if row[11] is not None:
            burial_location_current_grave = row[11]
        if row[12] is not None:
            burial_location_previous_lot = row[12]
        if row[13] is not None:
            burial_location_previous_grave = row[13]

        # --- PLACE OF BIRTH (14-16)
        birth_city = ''
        birth_state = ''
        birth_country = ''
        birth_place_full = ''
        birth_geo_street_number = ''
        birth_geo_street_name_long = ''
        birth_geo_street_name_short = ''
        birth_geo_neighborhood = ''
        birth_geo_country_short = ''
        birth_geo_country_long = ''
        birth_geo_city = ''
        birth_geo_state_long = ''
        birth_geo_state_short = ''
        birth_geo_county = ''
        birth_geo_zip = ''
        birth_geo_lat = None
        birth_geo_lng = None
        birth_geo_formatted_address = ''
        if row[14] is not None:
            birth_city = str(row[14])
        if row[15] is not None:
            birth_state = str(row[15])
        if row[16] is not None:
            birth_country = str(row[16])
        birth_place_full = (birth_city + " " + birth_state + " " + birth_country).strip()
        ' '.join(birth_place_full.split())
        if birth_place_full != '' and do_geocode_birth is True:
            geocode_results = get_google_geocode_results(birth_place_full)
            if geocode_results is not None:
                birth_geo_lat = geocode_results['geometry']['location']['lat']
                birth_geo_lng = geocode_results['geometry']['location']['lng']
                birth_geo_formatted_address = geocode_results['formatted_address']
                for component in geocode_results['address_components']:
                    # logging.warning(component)
                    for type in component['types']:
                        # logging.warning(type)
                        if type == 'street_number':
                            birth_geo_street_number = component['short_name']
                        if type == 'route':
                            birth_geo_street_name_long = component['long_name']
                            birth_geo_street_name_short = component['short_name']
                        if type == 'neighborhood':
                            birth_geo_neighborhood = component['long_name']
                        if type == 'country':
                            birth_geo_country_short = component['short_name']
                            birth_geo_country_long = component['long_name']
                        if type == 'sublocality':
                            birth_geo_city = component['long_name']
                        if type == 'locality':
                            birth_geo_city = component['long_name']
                        if type == 'administrative_area_level_1':
                            birth_geo_state_long = component['long_name']
                            birth_geo_state_short = component['short_name']
                        if type == 'administrative_area_level_2':
                            birth_geo_county = component['long_name']
                        if type == 'postal_code':
                            birth_geo_zip = component['long_name']

        # --- AGE (17-19)
        age_years = None
        age_months = None
        age_days = None
        age_full = ''
        if row[17] is not None and row[17] != '':
            age_years = row[17]
            age_full += str(int(age_years) )+ " years"
        if row[18] is not None and row[18] != '':
            age_months = row[18]
            if age_full != '':
                age_full += ", "
            age_full += str(int(age_months)) + " months"
        if row[19] is not None and row[19] != '':
            age_days = str(row[19])
            age_days = re.sub('\s*1/2', '.5', age_days)
            age_days = re.sub('\s*3/4', '.75', age_days)
            age_days = re.sub('\d+\s+Hrs?', '0', age_days)
            age_days = re.sub('\d+\s+Hours?', '0', age_days)
            age_days = float(age_days)
            if age_full != '':
                age_full += ", "
            age_full += str(age_days) + " days"

        # --- MARITAL STATUS (20)
        marital_status = 'Not recorded'
        if row[20] is not None and row[20] != '':
            marital_status = row[20].capitalize().strip()
        # normalize variants
        for key in marital_status_dict.keys():
            if key == marital_status.lower():
                marital_status = (marital_status_dict[key])

        # --- PLACE OF RESIDENCE (21-24)
        residence_street = ''
        residence_city = ''
        residence_state = ''
        residence_country = ''
        residence_place_full = ''
        residence_geo_street_number = ''
        residence_geo_street_name_long = ''
        residence_geo_street_name_short = ''
        residence_geo_neighborhood = ''
        residence_geo_country_short = ''
        residence_geo_country_long = ''
        residence_geo_city = ''
        residence_geo_state_long = ''
        residence_geo_state_short = ''
        residence_geo_county = ''
        residence_geo_zip = ''
        residence_geo_lat = None
        residence_geo_lng = None
        residence_geo_formatted_address = ''
        if row[21] is not None:
            residence_street = str(row[21])
        if row[22] is not None:
            residence_city = str(row[22])
        if row[23] is not None:
            residence_state = str(row[23])
        if row[24] is not None:
            residence_country = str(row[24])
        residence_place_full = (residence_street + " " + residence_city + " " + residence_state + " " + residence_country).strip()
        ' '.join(residence_place_full.split())
        if residence_place_full != '' and do_geocode_residence is True:
            geocode_results = get_google_geocode_results(residence_place_full)
            if geocode_results is not None:
                residence_geo_lat = geocode_results['geometry']['location']['lat']
                residence_geo_lng = geocode_results['geometry']['location']['lng']
                residence_geo_formatted_address = geocode_results['formatted_address']
                for component in geocode_results['address_components']:
                    # logging.warning(component)
                    for type in component['types']:
                        # logging.warning(type)
                        if type == 'street_number':
                            residence_geo_street_number = component['short_name']
                        if type == 'route':
                            residence_geo_street_name_long = component['long_name']
                            residence_geo_street_name_short = component['short_name']
                        if type == 'neighborhood':
                            residence_geo_neighborhood = component['long_name']
                        if type == 'country':
                            residence_geo_country_short = component['short_name']
                            residence_geo_country_long = component['long_name']
                        if type == 'sublocality':
                            residence_geo_city = component['long_name']
                        if type == 'locality':
                            residence_geo_city = component['long_name']
                        if type == 'administrative_area_level_1':
                            residence_geo_state_long = component['long_name']
                            residence_geo_state_short = component['short_name']
                        if type == 'administrative_area_level_2':
                            residence_geo_county = component['long_name']
                        if type == 'postal_code':
                            residence_geo_zip = component['long_name']

        # --- PLACE OF DEATH (25-29)
        death_location = ''
        death_street = ''
        death_city = ''
        death_state = ''
        death_country = ''
        death_place_full = ''
        death_geo_street_number = ''
        death_geo_street_name_long = ''
        death_geo_street_name_short = ''
        death_geo_neighborhood = ''
        death_geo_country_short = ''
        death_geo_country_long = ''
        death_geo_city = ''
        death_geo_state_long = ''
        death_geo_state_short = ''
        death_geo_county = ''
        death_geo_zip = ''
        death_geo_lat = None
        death_geo_lng = None
        death_geo_formatted_address = ''
        if row[25] is not None:
            death_location = row[25]
        if row[26] is not None:
            death_street = row[26]
        if row[27] is not None:
            death_city = row[27]
        if row[28] is not None:
            death_state = row[28]
        if row[29] is not None:
            death_country = row[29]
        death_place_full = (death_location + " " + death_street + " " + death_city + " " + death_state + " " + death_country).strip()
        ' '.join(death_place_full.split())
        if death_place_full != '' and do_geocode_death is True:
            geocode_results = get_google_geocode_results(death_place_full)
            if geocode_results is not None:
                death_geo_lat = geocode_results['geometry']['location']['lat']
                death_geo_lng = geocode_results['geometry']['location']['lng']
                death_geo_formatted_address = geocode_results['formatted_address']
                for component in geocode_results['address_components']:
                    # logging.warning(component)
                    for type in component['types']:
                        # logging.warning(type)
                        if type == 'street_number':
                            death_geo_street_number = component['short_name']
                        if type == 'route':
                            death_geo_street_name_long = component['long_name']
                            death_geo_street_name_short = component['short_name']
                        if type == 'neighborhood':
                            death_geo_neighborhood = component['long_name']
                        if type == 'country':
                            death_geo_country_short = component['short_name']
                            death_geo_country_long = component['long_name']
                        if type == 'sublocality':
                            death_geo_city = component['long_name']
                        if type == 'locality':
                            death_geo_city = component['long_name']
                        if type == 'administrative_area_level_1':
                            death_geo_state_long = component['long_name']
                            death_geo_state_short = component['short_name']
                        if type == 'administrative_area_level_2':
                            death_geo_county = component['long_name']
                        if type == 'postal_code':
                            death_geo_zip = component['long_name']

        # --- DEATH DATE (30-32)
        death_date_display = ''
        death_date_iso = ''
        death_year = ''
        # death month
        if row[30] is not None and row[30] != '':
            death_date_display += row[30] + " "
        # death day
        if row[31] is not None and row[31] != '':
            death_date_display += str(int(row[31])) + ", "
        # death year
        if row[32] is not None and row[32] != '':
            death_date_display += str(int(row[32]))
            death_year = int(row[32])
        death_date = ''
        if death_date_display != '':
            dt = dateparser.parse(death_date_display)
            if dt is not None:
                death_date_iso = dt.strftime("%Y-%m-%d")

        # --- CAUSE OF DEATH (33)
        cause_of_death = ''
        if row[33] is not None:
            cause_of_death = row[33].strip()

        # add synonyms as tags
        for key in cause_of_death_dict.keys():
            if key == cause_of_death.lower():
                tags.append(cause_of_death_dict[key])

        # --- REMOVAL FROM (34)
        removal_from = ''
        if row[34] is not None:
            removal_from = row[34]

        # --- UNDERTAKER (35)
        undertaker = ''
        if row[35] is not None:
            undertaker = row[35]

        # --- REMOVED (36)
        removed = False
        if row[36] is not None:
            removed = True

        # --- REMOVED DATE (37)
        removed_date = ''
        if row[37] is not None:
            removed_date = row[37]

        # --- NOTES (38)
        notes = ''
        if row[38] is not None:
            notes = row[38]

        interment = {
            "cemetery": cemetery,
            "interment_id": interment_id,
            "image_filename": image_filename,
            "registry_volume": registry_volume,
            "interment_date_display" : interment_date_display,
            "interment_date_iso": interment_date_iso,
            "interment_year": interment_year,
            "name_salutation": name_salutation,
            "name_first": name_first,
            "name_middle": name_middle,
            "name_last": name_last,
            "name_full": name_full,
            "name_infant": name_infant,
            "burial_location_current_lot": burial_location_current_lot,
            "burial_location_current_grave": burial_location_current_grave,
            "burial_location_previous_lot": burial_location_previous_lot,
            "burial_location_previous_grave": burial_location_previous_grave,
            "birth_city": birth_city,
            "birth_state": birth_state,
            "birth_country": birth_country,
            "birth_place_full": birth_place_full,
            "birth_geo_location": {"lat": birth_geo_lat,"lon": birth_geo_lng},
            "birth_geo_street_number": birth_geo_street_number,
            "birth_geo_street_name_long": birth_geo_street_name_long,
            "birth_geo_street_name_short": birth_geo_street_name_short,
            "birth_geo_neighborhood": birth_geo_neighborhood,
            "birth_geo_city": birth_geo_city,
            "birth_geo_county": birth_geo_county,
            "birth_geo_state_short": birth_geo_state_short,
            "birth_geo_state_long": birth_geo_state_long,
            "birth_geo_country_long": birth_geo_country_long,
            "birth_geo_country_short": birth_geo_country_short,
            "birth_geo_zip": birth_geo_zip,
            "birth_geo_formatted_address": birth_geo_formatted_address,
            "age_years": age_years,
            "age_months": age_months,
            "age_days": age_days,
            "age_full": age_full,
            "marital_status": marital_status,
            "residence_street": residence_street,
            "residence_city": residence_city,
            "residence_state": residence_state,
            "residence_country": residence_country,
            "residence_place_full": residence_place_full,
            "residence_geo_location": {"lat": residence_geo_lat, "lon": residence_geo_lng},
            "residence_geo_street_number": residence_geo_street_number,
            "residence_geo_street_name_long": residence_geo_street_name_long,
            "residence_geo_street_name_short": residence_geo_street_name_short,
            "residence_geo_neighborhood": residence_geo_neighborhood,
            "residence_geo_city": residence_geo_city,
            "residence_geo_county": residence_geo_county,
            "residence_geo_state_short": residence_geo_state_short,
            "residence_geo_state_long": residence_geo_state_long,
            "residence_geo_country_long": residence_geo_country_long,
            "residence_geo_country_short": residence_geo_country_short,
            "residence_geo_zip": residence_geo_zip,
            "residence_geo_formatted_address": residence_geo_formatted_address,
            "death_location": death_location,
            "death_street": death_street,
            "death_city": death_city,
            "death_state": death_state,
            "death_country": death_country,
            "death_place_full": death_place_full,
            "death_geo_location": {"lat": death_geo_lat, "lon": death_geo_lng},
            "death_geo_street_number": death_geo_street_number,
            "death_geo_street_name_long": death_geo_street_name_long,
            "death_geo_street_name_short": death_geo_street_name_short,
            "death_geo_neighborhood": death_geo_neighborhood,
            "death_geo_city": death_geo_city,
            "death_geo_county": death_geo_county,
            "death_geo_state_short": death_geo_state_short,
            "death_geo_state_long": death_geo_state_long,
            "death_geo_country_long": death_geo_country_long,
            "death_geo_country_short": death_geo_country_short,
            "death_geo_zip": death_geo_zip,
            "death_geo_formatted_address": death_geo_formatted_address,
            "death_date_display" : death_date_display,
            "death_date_iso": death_date_iso,
            "death_year": death_year,
            "cause_of_death": cause_of_death,
            "removal_from": removal_from,
            "undertaker": undertaker,
            "removed": removed,
            "removed_date": removed_date,
            "note": notes,
            "tags": tags
        }

        # make sure you can json serialize, otherwise dump error and interment
        try:
            json_temp = json.dumps(interment)
            interments.append(interment)
        except Exception as e:
            logging.fatal(getattr(e, 'message', repr(e)))
            logging.fatal(interment)
            # exit()

print(json.dumps(interments))
