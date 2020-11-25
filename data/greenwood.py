import json
import re
import dateparser
import requests
import logging
from nameparser import HumanName
from openpyxl import load_workbook
import argparse
import sqlite3
from inflection import parameterize
from os import path
import time
import googlemaps

connection = sqlite3.connect("gender/gender.db")
cursor = connection.cursor()

# command line arguments
parser = argparse.ArgumentParser(description='Spreadsheet to JSON')
parser.add_argument('-input', type=str, help='spreadsheet in xslx format')
parser.add_argument('-key', type=str, help='google api key')
parser.add_argument('-sheet', type=str, help='worksheet to transform')
parser.add_argument('-vol', type=str, help='registry volume number')
args = parser.parse_args()
workbook = load_workbook(filename=args.input, data_only=True)

GOOGLE_API_KEY = args.key
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# sheet = workbook.active
sheet = workbook[args.sheet]

# logging config
timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(filename='logs/import-volume-' + args.vol + '-' + timestr + '.log', filemode='a', format='%(levelname)s - %(message)s')

do_geocode_birth = True
do_geocode_residence = True
do_geocode_death = True
cemetery = "Green-Wood Cemetery, Brooklyn, NY, USA"


# load synonym dictionaries
with open('dictionaries/cause-of-death.json') as f:
    cause_of_death_dict = json.load(f)
with open('dictionaries/marital-status.json') as g:
    marital_status_dict = json.load(g)
with open('dictionaries/city-to-state.json') as g:
    city_state_dict = json.load(g)
with open('dictionaries/states.json') as g:
    state_dict = json.load(g)

# =====================================================================================================================
# GOOGLE GEOCODE API LOOKUP
# =====================================================================================================================
def get_google_geocode_results(address_or_zipcode):
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


def get_geocode_dict():
    d = {}
    keys = [
        'place_geocode_input',
        'geo_lat', 'geo_lng',
        'geo_formatted_address',
        'geo_street_number',
        'geo_street_name_long',
        'geo_street_name_short',
        'geo_neighborhood',
        'geo_country_long',
        'geo_country_short',
        'geo_city',
        'geo_state_long',
        'geo_state_short',
        'geo_county',
        'geo_zip',
        'geo_other',
        'google_place_id'
    ]
    # initialize empty dictionary
    for i in keys:
        d[i] = ''
    return d

# =====================================================================================================================
# GEOCODE PLACE
# =====================================================================================================================
def geocode_place(vol, id, type, place):

    d = get_geocode_dict()
    # return empty dictionary if no place is specified
    if place == '':
        return d
    else:
        d['place_geocode_input'] = place

    geocode_filename = 'json/places/' + parameterize(place.lower().strip(), separator="_") + '.json'
    if place != '' and path.exists(geocode_filename) is False:

        # geocode_results = get_google_geocode_results(place)
        gmaps_result = gmaps.geocode(place)
        if len(gmaps_result) != 0:
            geocode_results = gmaps_result[0]
        else:
            geocode_results = None

        if geocode_results is not None:
            d['google_place_id'] = geocode_results['place_id']
            d['place_geocode_input'] = place
            d['geo_lat'] = geocode_results['geometry']['location']['lat']
            d['geo_lng'] = geocode_results['geometry']['location']['lng']
            d['geo_formatted_address'] = geocode_results['formatted_address']
            for component in geocode_results['address_components']:
                for geo_type in component['types']:
                    if geo_type == 'street_number':
                        d['geo_street_number'] = component['short_name']
                    if geo_type == 'route':
                        d['geo_street_name_long'] = component['long_name']
                        d['geo_street_name_short'] = component['short_name']
                    if geo_type == 'neighborhood':
                        d['geo_neighborhood'] = component['long_name']
                    if geo_type == 'country':
                        d['geo_country_short'] = component['short_name']
                        d['geo_country_long'] = component['long_name']
                    if geo_type == 'sublocality':
                        d['geo_city'] = component['long_name']
                    if geo_type == 'locality':
                        d['geo_city'] = component['long_name']
                    if geo_type == 'administrative_area_level_1':
                        d['geo_state_long'] = component['long_name']
                        d['geo_state_short'] = component['short_name']
                    if geo_type == 'administrative_area_level_2':
                        d['geo_county'] = component['long_name']
                    if geo_type == 'postal_code':
                        d['geo_zip'] = component['long_name']
                    if geo_type == 'establishment':
                        d['geo_other'] = component['long_name']
                    if geo_type == 'natural_feature':
                        d['geo_other'] = component['long_name']
            try:
                f = open(geocode_filename, 'w')
                json.dump(d, f, indent=4, sort_keys=True)
                f.close()
                return d
            except Exception as e:
                logging.fatal(getattr(e, 'message', repr(e)))
        else:
            logging.warning("VOLUME " + vol + " INTERMENT ID " + str(int(id)) + " unable geocode " + type + " place: " + place)
            # serialize empty geo place
            f = open(geocode_filename, 'w')
            json.dump(d, f, indent=4, sort_keys=True)
            f.close()
            return d
    else:
        # return serialized geocodes
        if path.exists(geocode_filename):
            with open(geocode_filename) as json_file:
                place_json = json.load(json_file)
                if place_json["google_place_id"] == "":
                    logging.warning("VOLUME " + vol + " INTERMENT ID " + str(int(id)) + " unable to geocode " + type + " place: " + place)
                return place_json
        else:
            return d

# =====================================================================================================================
# IS FLOAT?
# =====================================================================================================================
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

# =====================================================================================================================
# MAIN
# =====================================================================================================================
interments = []

# Using the values_only because you want to return the cells' values
for row in sheet.iter_rows(min_row=3, values_only=True):

    if row[1] is not None:

        # --- TAGS (39)
        tags = []
        if len(row) > 39:
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
            if interment_year > 2020:
                logging.warning("VOLUME " + str(registry_volume) + " INTERMENT ID " + str(int(interment_id)) + " has an interment_year greater than 2020: " + str(interment_year) )
        interment_date = ''
        if interment_date_display != '':
            dt = dateparser.parse(interment_date_display)
            if dt is not None:
                interment_date_iso = dt.strftime("%Y-%m-%d")
            else:
                logging.warning("VOLUME " + str(registry_volume) + " INTERMENT ID " + str(int(interment_id)) + " unable to parse interment date: " + interment_date_display )

        # --- NAME (5-9)
        name_salutation = ''
        name_first = ''
        name_first_gender = 'Unknown'
        name_middle = ''
        name_last = ''
        name_infant = ''
        name_full = ''
        if row[5] is not None:
            name_salutation = row[5].strip()
        if row[6] is not None:
            name_first = str(row[6]).strip()
            # just get first part of any first name (eg: Mary Jane)
            name_first_gender_temp = name_first.split(' ')[0]
            gender_row = cursor.execute("SELECT gender from namegenderpro where name = '" + name_first_gender_temp + "' COLLATE NOCASE").fetchone()
            if gender_row:
                name_first_gender = gender_row[0]
        if row[7] is not None:
            name_middle = row[7].strip()
        if row[8] is not None:
            name_last = row[8].strip()

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

        # BIRTH CITY
        if row[14] is not None:
            birth_city = str(row[14]).strip()
            # city is really a state, and state is empty, move it over
            for key in state_dict.keys():
                if key == birth_city.lower() and row[15] is None:
                    birth_city = ''
                    birth_state = key
            # long s variant of massachusetts
            if 'mafs' == birth_city.lower() and row[15] is None:
                birth_city = ''
                birth_state = 'Massachusetts'
                if row[16] is None:
                    birth_country = 'United States'

        # BIRTH STATE
        if row[15] is not None:
            birth_state = str(row[15]).strip()

        # BIRTH COUNTRY
        if row[16] is not None:
            birth_country = str(row[16])

        # BIRTH PLACE FULL - concatenate all of the available fields
        birth_place_full = (birth_city + " " + birth_state + " " + birth_country).strip()
        ' '.join(birth_place_full.split())

        # GEOCODE: BIRTH PLACE
        if do_geocode_birth:
            birth_place_geocoded = geocode_place(registry_volume, interment_id, 'birth', birth_place_full)
        else:
            birth_place_geocoded = get_geocode_dict()

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
            age_days = re.sub('\w+\s+[Hh]ours?', '0', age_days)
            if isfloat(age_days):
                age_days = float(age_days)
                if age_full != '':
                    age_full += ", "
                age_full += str(age_days) + " days"

        # --- MARITAL STATUS (20)
        valid_status = ['Not recorded', 'Married', 'Single', 'Widow', 'Unknown']
        marital_status = 'Not recorded'
        if row[20] is not None and row[20] != '':
            marital_status = str(row[20]).strip().capitalize()
        # normalize variants
        for key in marital_status_dict.keys():
            if key == marital_status.lower():
                marital_status = (marital_status_dict[key])
        if marital_status not in valid_status:
            logging.warning("VOLUME " + str(registry_volume) + " INTERMENT ID " + str(int(interment_id)) + " has a marital status of: " + marital_status)


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
            residence_street = str(row[21]).strip()
        if row[22] is not None:
            residence_city = str(row[22]).strip()

            # long s variant of massachusetts
            if 'mafs' == residence_city.lower() and row[23] is None:
                residence_city = ''
                residence_state = 'Massachusetts'
                if row[24] is None:
                    residence_country = 'United States'

            # infer state in some cases using a mapping dictionary
            if row[23] is None:
                for key in city_state_dict.keys():
                    if key == residence_city.lower():
                        residence_state = (city_state_dict[key])
        if row[23] is not None:
            residence_state = str(row[23]).strip()
        if row[24] is not None:
            residence_country = str(row[24]).strip()

        residence_place_full = (residence_street + " " + residence_city + " " + residence_state + " " + residence_country).strip()
        ' '.join(residence_place_full.split())

        # GEOCODE: RESIDENCE PLACE
        if do_geocode_residence:
            residence_place_geocoded = geocode_place(registry_volume, interment_id, 'residence', residence_place_full)
        else:
            residence_place_geocoded = get_geocode_dict()

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
            death_location = str(row[25]).strip()
        if row[26] is not None:
            death_street = str(row[26]).strip()
        if row[27] is not None:
            death_city = str(row[27]).strip()

            # long s variant of massachusetts
            if 'mafs' == death_city.lower() and row[28] is None:
                death_city = ''
                death_state = 'Massachusetts'
                if row[29] is None:
                    death_country = 'United States'

            # infer state in some cases using a mapping dictionary
            if row[28] is None:
                for key in city_state_dict.keys():
                    if key == death_city.lower():
                        death_state = (city_state_dict[key])
        if row[28] is not None:
            death_state = str(row[28]).strip()
        if row[29] is not None:
            death_country = str(row[29]).strip()
        death_place_full = (death_location + " " + death_street + " " + death_city + " " + death_state + " " + death_country).strip()
        ' '.join(death_place_full.split())

        # GEOCODE: DEATH PLACE
        if do_geocode_death:
            death_place_geocoded = geocode_place(registry_volume, interment_id, 'death', death_place_full)
        else:
            death_place_geocoded = get_geocode_dict()

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
            if death_year > 2020:
                logging.warning("VOLUME " + str(registry_volume) + " INTERMENT ID " + str(int(interment_id)) + " has a death year greater than 2020: " + str(death_year) )

        death_date = ''
        if death_date_display != '':
            dt = dateparser.parse(death_date_display)
            if dt is not None:
                death_date_iso = dt.strftime("%Y-%m-%d")
            else:
                logging.warning("VOLUME " + str(registry_volume) + " INTERMENT ID " + str(int(interment_id)) + " unable to parse death date: " + death_date_display )

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
            notes = str(row[38]).strip()

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
            "gender_guess": name_first_gender,
            "burial_location_current_lot": burial_location_current_lot,
            "burial_location_current_grave": burial_location_current_grave,
            "burial_location_previous_lot": burial_location_previous_lot,
            "burial_location_previous_grave": burial_location_previous_grave,
            "birth_city": birth_city,
            "birth_state": birth_state,
            "birth_country": birth_country,
            "birth_place_full": birth_place_full,
            "birth_geo_location": {"lat": birth_place_geocoded['geo_lat'],"lon": birth_place_geocoded['geo_lng']},
            "birth_geo_street_number": birth_place_geocoded['geo_street_number'],
            "birth_geo_street_name_long": birth_place_geocoded['geo_street_name_long'],
            "birth_geo_street_name_short": birth_place_geocoded['geo_street_name_short'],
            "birth_geo_neighborhood": birth_place_geocoded['geo_neighborhood'],
            "birth_geo_city": birth_place_geocoded['geo_city'],
            "birth_geo_county": birth_place_geocoded['geo_county'],
            "birth_geo_state_short": birth_place_geocoded['geo_state_short'],
            "birth_geo_state_long": birth_place_geocoded['geo_state_long'],
            "birth_geo_country_long": birth_place_geocoded['geo_country_long'],
            "birth_geo_country_short": birth_place_geocoded['geo_country_short'],
            "birth_geo_zip": birth_place_geocoded['geo_zip'],
            "birth_geo_place_id": birth_place_geocoded['google_place_id'],
            "birth_geo_formatted_address": birth_place_geocoded['geo_formatted_address'],
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
            "residence_geo_location": {"lat": residence_place_geocoded['geo_lat'],"lon": residence_place_geocoded['geo_lng']},
            "residence_geo_street_number": residence_place_geocoded['geo_street_number'],
            "residence_geo_street_name_long": residence_place_geocoded['geo_street_name_long'],
            "residence_geo_street_name_short": residence_place_geocoded['geo_street_name_short'],
            "residence_geo_neighborhood": residence_place_geocoded['geo_neighborhood'],
            "residence_geo_city": residence_place_geocoded['geo_city'],
            "residence_geo_county": residence_place_geocoded['geo_county'],
            "residence_geo_state_short": residence_place_geocoded['geo_state_short'],
            "residence_geo_state_long": residence_place_geocoded['geo_state_long'],
            "residence_geo_country_long": residence_place_geocoded['geo_country_long'],
            "residence_geo_country_short": residence_place_geocoded['geo_country_short'],
            "residence_geo_zip": residence_place_geocoded['geo_zip'],
            "residence_geo_place_id": residence_place_geocoded['google_place_id'],
            "residence_geo_formatted_address": residence_place_geocoded['geo_formatted_address'],
            "death_location": death_location,
            "death_street": death_street,
            "death_city": death_city,
            "death_state": death_state,
            "death_country": death_country,
            "death_place_full": death_place_full,
            "death_geo_location": {"lat": death_place_geocoded['geo_lat'],"lon": death_place_geocoded['geo_lng']},
            "death_geo_street_number": death_place_geocoded['geo_street_number'],
            "death_geo_street_name_long": death_place_geocoded['geo_street_name_long'],
            "death_geo_street_name_short": death_place_geocoded['geo_street_name_short'],
            "death_geo_neighborhood": death_place_geocoded['geo_neighborhood'],
            "death_geo_city": death_place_geocoded['geo_city'],
            "death_geo_county": death_place_geocoded['geo_county'],
            "death_geo_state_short": death_place_geocoded['geo_state_short'],
            "death_geo_state_long": death_place_geocoded['geo_state_long'],
            "death_geo_country_long": death_place_geocoded['geo_country_long'],
            "death_geo_country_short": death_place_geocoded['geo_country_short'],
            "death_geo_zip": death_place_geocoded['geo_zip'],
            "death_geo_place_id": death_place_geocoded['google_place_id'],
            "death_geo_formatted_address": death_place_geocoded['geo_formatted_address'],
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
connection.close()