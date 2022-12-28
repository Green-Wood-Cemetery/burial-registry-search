#!/usr/bin/python

import json
import re
import logging
from nameparser import HumanName
import sqlite3
import copy
import dateparser
import os
import googlemaps
from inflection import parameterize
import pandas as pd
from dotenv import load_dotenv
import humanize

load_dotenv()
connection = sqlite3.connect("gender/gender.db")
cursor = connection.cursor()
logger = logging.getLogger(__name__)

# load dictionaries
with open('dictionaries/cause-of-death.json') as f:
    cause_of_death_dict = json.load(f)
with open('dictionaries/marital-status.json') as g:
    marital_status_dict = json.load(g)
with open('dictionaries/city-to-state.json') as g:
    city_state_dict = json.load(g)
with open('dictionaries/states.json') as g:
    state_dict = json.load(g)
with open('dictionaries/name-abbrev.json') as g:
    name_abbrev_dict = json.load(g)
with open('dictionaries/interment_year_ranges.json') as g:
    interment_year_dict = json.load(g)
with open('dictionaries/death_year_ranges.json') as g:
    death_year_dict = json.load(g)
with open('dictionaries/place-abbrev.json') as g:
    place_abbrev_dict = json.load(g)

do_geocode_birth = False
do_geocode_residence = False
do_geocode_death = False
cemetery = "Green-Wood Cemetery, Brooklyn, NY, USA"

# GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
# gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# static functions
def get_geocode_dict():
    d = {}
    keys = [
        'place_geocode_input',
        'geo_lat',
        'geo_lng',
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


class Interment:

    def __init__(self):

        # elastic search fields
        self.es_fields = []
        self.es_fields.append({'name': 'interment_id', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'cemetery', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'registry_volume', 'type': 'long', 'keywords': True})
        self.es_fields.append({'name': 'registry_page', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'registry_image', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'interment_date_month_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'interment_date_day_transcribed', 'type': 'long', 'keywords': False})
        self.es_fields.append({'name': 'interment_date_year_transcribed', 'type': 'long', 'keywords': False})
        self.es_fields.append({'name': 'interment_date_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'interment_date_iso', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_last', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_first', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_middle', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_salutation', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'name_suffix', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'is_lot_owner', 'type': 'boolean', 'keywords': False})
        self.es_fields.append({'name': 'gender_guess', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_location_lot_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_location_lot_current', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_location_lot_current', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_location_grave_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_location_grave_current', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_location_grave_previous', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_place_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_place_displayed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_formatted_address', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_is_faulty', 'type': 'boolean', 'keywords': False})
        self.es_fields.append({'name': 'birth_geo_street_number', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_street_name_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_street_name_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_neighborhood', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_city', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_county', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_state_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_state_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_country_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_country_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_zip', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_geo_place_id', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'birth_place_geo_location', 'type': 'geo_point', 'keywords': False})
        self.es_fields.append({'name': 'age_years_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'age_months_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'age_days_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'age_hours_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'age_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'age_years', 'type': 'long', 'keywords': False})
        self.es_fields.append({'name': 'age_months', 'type': 'long', 'keywords': False})
        self.es_fields.append({'name': 'age_days', 'type': 'long', 'keywords': False})
        self.es_fields.append({'name': 'age_hours', 'type': 'long', 'keywords': False})
        self.es_fields.append({'name': 'marital_status_married_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'marital_status_single_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'marital_status', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_city_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_city_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_street_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_street_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_formatted_address', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_is_faulty', 'type': 'boolean', 'keywords': False})
        self.es_fields.append({'name': 'residence_place_geo_street_number', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_street_number_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_street_number_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_neighborhood', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_city', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_county', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_state_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_state_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_country_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_country_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_zip', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_place_id', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'residence_place_geo_location', 'type': 'geo_point', 'keywords': False})
        self.es_fields.append({'name': 'death_place_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_formatted_address', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_is_faulty', 'type': 'boolean', 'keywords': False})
        self.es_fields.append({'name': 'death_place_geo_street_number', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_street_number_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_street_number_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_neighborhood', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_city', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_county', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_state_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_state_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_country_long', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_country_short', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_zip', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_place_id', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_place_geo_location', 'type': 'geo_point', 'keywords': False})
        self.es_fields.append({'name': 'death_date_month_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_date_day_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_date_year_transcribed', 'type': 'long', 'keywords': True})
        self.es_fields.append({'name': 'death_date_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_date_iso', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'death_date_ult_month', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'cause_of_death_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'cause_of_death_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'undertaker_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'undertaker_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'remarks_transcribed', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'remarks_display', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'burial_origin', 'type': 'text', 'keywords': True})
        self.es_fields.append({'name': 'has_diagram', 'type': 'boolean', 'keywords': False})

        # INTERMENT ID
        self.__id = 0
        self.__interment_id_comments = ''

        # PREVIOUS INTERMENT
        self.__previous = None

        # REGISTRY
        # filename
        self.__registry_image_filename_raw = None
        self.__registry_image_filename = None
        self.__registry_image_link = ''
        # volume
        self.__registry_volume = None
        # page
        self.__registry_page = None
        self.__registry_volume_page_comments = ''

        # NAME
        self.__name_raw = None
        self.__name_full = None
        self.__name_first = None
        self.__name_last = None
        self.__name_middle = None
        self.__name_salutation = None
        self.__name_suffix = None
        self.__name_infant = None
        self.__name_gender_guess = 'Unknown'
        self.__is_plot_owner = False
        self.__name_comments = ''

        # DATES:
        # INTERMENT
        self.__interment_date_month_raw = None
        self.__interment_date_month_display = None
        self.__interment_date_comments = ''
        self.__interment_date_iso_comments = ''
        self.__interment_date_day_raw = None
        self.__interment_date_day_display = None
        self.__interment_date_year_raw = None
        self.__interment_date_year = None
        self.__interment_date_year_display = None
        self.__interment_date_year_cached = None
        self.__interment_date_display = None
        self.__interment_date_iso = None

        # DEATH
        self.__death_date_month_raw = None
        self.__death_date_month_display = None
        self.__death_date_comments = ''
        self.__death_date_iso_comments = ''
        self.__missing_death_date_comments = ''
        self.__death_date_day_raw = None
        self.__death_date_day_display = None
        self.__death_date_day_full = None
        self.__death_date_year_raw = None
        self.__death_date_year = None
        self.__death_date_display = None
        self.__death_date_year_cached = None
        self.__death_date_iso = None
        self.__death_month_cached = None
        self.__death_date_year_display = None
        self.__death_year_cached = None

        # PLACES:
        # BIRTH
        self.__birth_place_raw = None
        self.__birth_place_raw_expand_abbreviations = None
        self.__birth_place_display = None
        self.__birth_place_full = None
        self.__birth_place_comments = ''
        self.__birth_geo_place_id = None
        self.__birth_geo_location = None
        self.__birth_geo_street_number = None
        self.__birth_geo_street_name_long = None
        self.__birth_geo_street_name_short = None
        self.__birth_geo_neighborhood = None
        self.__birth_geo_country_short = None
        self.__birth_geo_country_long = None
        self.__birth_geo_city = None
        self.__birth_geo_state_long = None
        self.__birth_geo_state_short = None
        self.__birth_geo_county = None
        self.__birth_geo_zip = None
        self.__birth_geo_lat = None
        self.__birth_geo_lng = None
        self.__birth_geo_formatted_address = None

        # DEATH
        self.__death_place_raw = None
        self.__death_place_raw_expand_abbreviations = None
        self.__death_place_display = None
        self.__death_place_full = None
        self.__death_place_comments = ''
        self.__death_geo_place_id = None
        self.__death_geo_location = None
        self.__death_geo_street_number = None
        self.__death_geo_street_name_long = None
        self.__death_geo_street_name_short = None
        self.__death_geo_neighborhood = None
        self.__death_geo_country_short = None
        self.__death_geo_country_long = None
        self.__death_geo_city = None
        self.__death_geo_state_long = None
        self.__death_geo_state_short = None
        self.__death_geo_county = None
        self.__death_geo_zip = None
        self.__death_geo_lat = None
        self.__death_geo_lng = None
        self.__death_geo_formatted_address = None

        # RESIDENCE
        self.__residence_place_city_raw = None
        self.__residence_city_comments = ''
        self.__residence_place_city_full = None
        self.__residence_place_city_raw_expand_abbreviations = None
        self.__residence_place_street_raw = None
        self.__residence_street_comments = ''
        self.__residence_place_street_full = None
        self.__residence_place_street_raw_expand_abbreviations = None
        self.__residence_place_full = None
        self.__residence_place_comments = ''
        self.__residence_geo_place_id = None
        self.__residence_geo_location = None
        self.__residence_geo_street_number = None
        self.__residence_geo_street_name_long = None
        self.__residence_geo_street_name_short = None
        self.__residence_geo_neighborhood = None
        self.__residence_geo_country_short = None
        self.__residence_geo_country_long = None
        self.__residence_geo_city = None
        self.__residence_geo_state_long = None
        self.__residence_geo_state_short = None
        self.__residence_geo_county = None
        self.__residence_geo_zip = None
        self.__residence_geo_lat = None
        self.__residence_geo_lng = None
        self.__residence_geo_formatted_address = None

        # BURIAL LOCATION
        self.__burial_location_lot_raw = None
        self.__burial_location_lot = None
        self.__burial_location_lot_strike = None
        self.__burial_location_lot_comments = ''
        self.__burial_location_lot_strike_comments = ''
        self.__burial_location_grave_raw = None
        self.__burial_location_grave = None
        self.__burial_location_grave_strike = None
        self.__burial_location_grave_comments = ''
        self.__burial_location_grave_strike_comments = ''
        self.__burial_origin = ''
        self.__from_cemetery = ''
        self.__is_removal_from = False
        self.__is_removed_to = False

        # AGE
        self.__age_display = ''
        self.__age_years_raw = None
        self.__age_years = None
        self.__age_years_comments = ''
        self.__age_months_raw = None
        self.__age_months = None
        self.__age_months_comments = ''
        self.__age_days_raw = None
        self.__age_days = None
        self.__age_days_comments = ''
        self.__age_hours_raw = None
        self.__age_hours = None
        self.__age_hours_comments = ''

        # MARITAL STATUS
        self.__marital_status_raw = None
        self.__marital_status = 'Not recorded'
        self.__marital_status_comments = ''
        self.__marital_status_married_raw = None
        self.__marital_status_married = 'Not recorded'
        self.__marital_status_married_comments = ''
        self.__marital_status_single_raw = None
        self.__marital_status_single = 'Not recorded'
        self.__marital_status_single_comments = ''

        # CAUSE OF DEATH
        self.__cause_of_death_raw = None
        self.__cause_of_death_display = None
        self.__cause_of_death_comments = ''
        self.cause_of_death_transcribed_es_name = 'cause_of_death_transcribed'
        self.cause_of_death_transcribed_es_type = 'text'
        self.cause_of_death_transcribed_es_keyword = True

        # UNDERTAKER
        self.__undertaker_raw = None
        self.__undertaker_display = None
        self.__undertaker_comments = ''

        # REMARKS
        self.__remarks_raw = None
        self.__remarks_display = None
        self.__remarks_comments = ''

        # DIAGRAM
        self.__has_diagram = False

        self.__ultimate_month = None

        # ADMINISTRATIVE
        self.__needs_review = False
        # self.__admin_review_notes = None
        self.__needs_review_comments = ''
        self.__geocode_comments = ''
        self.__transcriber_requests_review = False

    # INTERMENT ID
    def set_id(self, value):
        if value is not None and value != '':
            if isinstance(value, int):
                self.__id = int(value)
            if isinstance(value, float):
                self.__id = int(value)
            # a temp value for missing left hand page
            if isinstance(value, str):
                self.__id = value
            # print('ID: ' + str(self.__id))
        else:
            self.__id = None
            self.__needs_review = True
            self.__interment_id_comments = "Missing interment ID"
            # print('ID: missing')

    def get_id(self):
        return self.__id

    # PREVIOUS INTERMENT
    def set_previous(self, value):
        self.__previous = value

    def get_previous(self):
        return self.__previous

    # REGISTRY PROPERTIES
    def set_registry_image_filename_raw(self, value, lookup_years):
        self.__registry_image_filename_raw = value
        self.parse_registry_volume_page(lookup_years)

    def get_registry_image_filename_raw(self):
        return self.__registry_image_filename_raw

    def set_registry_image_filename(self, value):
        self.__registry_image_filename = value

    def get_registry_image_filename(self):
        return self.__registry_image_filename

    def get_registry_image_link(self):
        return self.__registry_image_link

    def set_registry_volume(self, value):
        self.__registry_volume = value

    def get_registry_volume(self):
        return self.__registry_volume

    def set_registry_page(self, value):
        self.__registry_page = value

    def get_registry_page(self):
        return self.__registry_page

    # DATES: INTERMENT
    def set_interment_date(self, month, day, year):
        display_temp = ''
        previous_entry = self.__previous

        if month is not None and month != '' and month != '"' and not str(month).isspace():
            self.__interment_date_month_raw = month
            self.__interment_date_month_display = month
            display_temp += month + " "
        else:
            if previous_entry is not None and self.__id is not None:
                if previous_entry.get_interment_date_month_display() is not None:
                    self.__interment_date_month_display = previous_entry.get_interment_date_month_display()
                    display_temp += self.__interment_date_month_display + " "
            else:
                self.__needs_review = True
                self.__interment_date_comments = "Unable to parse interment month"

        if day is not None and day != '' and day != '"' and not str(day).isspace():
            self.__interment_date_day_raw = int(day)
            self.__interment_date_day_display = int(day)
            display_temp += str(int(day)) + ", "
        else:
            if previous_entry is not None and self.__id is not None:
                if previous_entry.get_interment_date_day_display() is not None:
                    self.__interment_date_day_display = previous_entry.get_interment_date_day_display()
                    display_temp += str(int(self.__interment_date_day_display)) + ", "
            else:
                self.__needs_review = True
                self.__interment_date_comments = "Unable to parse interment day"

        if year is not None and (isinstance(year, float) or str(year).isdigit()):
            self.__interment_date_year_raw = year
            self.__interment_date_year_display = year
            self.__interment_date_year = year
            self.__interment_date_year_cached = year
        else:
            if previous_entry is not None:
                if previous_entry.get_interment_date_year_cached() is not None:
                    self.__interment_date_year_cached = previous_entry.get_interment_date_year_cached()
                if previous_entry.get_interment_date_year_display() is not None:
                    self.__interment_date_year_display = previous_entry.get_interment_date_year_display()
                    self.__interment_date_year = previous_entry.get_interment_date_year_display()
            else:
                self.__needs_review = True
                self.__interment_date_comments = "Unable to parse interment year"

        # generate iso date
        if display_temp != '':
            if self.__interment_date_year is not None:
                display_temp += str(int(self.__interment_date_year))

            self.__interment_date_display = display_temp
            dt = dateparser.parse(display_temp)
            if dt is not None:
                self.__interment_date_iso = dt.strftime("%Y-%m-%d")
            else:
                self.__needs_review = True
                self.__interment_date_iso_comments = "Unable to parse interment date: " + display_temp + '"'

    def set_interment_date_year(self, value):
        self.__interment_date_year = value

    def get_interment_date_year(self):
        return self.__interment_date_year

    def get_interment_date_year_raw(self):
        return self.__interment_date_year_raw

    def get_interment_date_year_display(self):
        return self.__interment_date_year_display

    def get_interment_date_year_cached(self):
        return self.__interment_date_year_cached

    def get_interment_date_display(self):
        return self.__interment_date_display

    def get_interment_date_iso(self):
        return self.__interment_date_iso

    def get_interment_date_month_raw(self):
        return self.__interment_date_month_raw

    def get_interment_date_month_display(self):
        return self.__interment_date_month_display

    def get_interment_date_day_raw(self):
        return self.__interment_date_day_raw

    def get_interment_date_day_display(self):
        return self.__interment_date_day_display

    # DATES: DEATH
    def set_death_date(self, month, day, year):
        display_temp = ''
        previous_entry = self.__previous

        if month is not None and month != '':
            self.__death_date_month_raw = month
            # fix strange month abbreviations
            month = re.sub('Jany', 'Jan', month, re.I)
            month = re.sub('Feby', 'Feb', month, re.I)
            month = re.sub('Febuary', 'February', month, re.I)
            self.__death_date_month_display = month
            self.__death_month_cached = month
            display_temp += month + " "
        else:
            if previous_entry is not None:
                if previous_entry.get_death_month_cached() is not None:
                    self.__death_month_cached = previous_entry.get_death_month_cached()
                if previous_entry.get_death_date_month_display() is not None:
                    self.__death_date_month_display = previous_entry.get_death_date_month_display()
                    display_temp += self.__death_date_month_display + " "
            else:
                self.__needs_review = True
                self.__death_date_comments = "Unable to parse interment month"

        # print('death day = "' + str(day) + '"')
        if day is not None and (isinstance(day, float) or str(day).isdigit()):
            # print('got death day')
            self.__death_date_day_raw = day
            self.__death_date_day_display = int(day)
            display_temp += str(int(day)) + ", "
        else:
            if previous_entry is not None and day == '"':
                self.__death_date_day_raw = day
                if previous_entry.get_death_date_day_display() is not None:
                    self.__death_date_day_display = previous_entry.get_death_date_day_display()
                    display_temp += str(int(self.__death_date_day_display)) + ", "
            else:
                # if day is None, don't assume month or year since it's likely a removal
                self.__death_date_year = None
                display_temp = ''

                # needs review if not a removal
                if not self.__is_removal_from and self.__burial_origin == '':
                    self.__needs_review = True
                    self.__missing_death_date_comments = "No day of death - possibly a removal?"
                    # print('set missing death date comment')

        if year is not None and (isinstance(year, float) or str(year).isdigit()):
            self.__death_date_year_raw = year
            self.__death_date_year_display = year
            self.__death_date_year = year
            self.__death_year_cached = year
        else:
            if previous_entry.get_death_year_cached() is not None:
                self.__death_year_cached = previous_entry.get_death_year_cached()
            if previous_entry.get_death_date_year_display() is not None:
                self.__death_date_year_display = previous_entry.get_death_date_year_display()
                self.__death_date_year = previous_entry.get_death_date_year_display()
            else:
                self.__needs_review = True
                self.__death_date_comments = "Unable to parse death year"
                self.__death_year_cached = None
                self.__death_date_year_display = None

        # generate iso date
        if display_temp != '':
            if self.__death_date_year is not None:
                display_temp += str(int(self.__death_date_year))

            self.__death_date_display = display_temp
            dt = dateparser.parse(display_temp)
            if dt is not None and self.__death_date_year is not None:
                self.__death_date_iso = dt.strftime("%Y-%m-%d")
            else:
                self.__needs_review = True
                self.__death_date_iso_comments = "Unable to parse death date: " + display_temp

    def set_death_date_year(self, value):
        self.__death_date_year = value

    def get_death_date_year(self):
        return self.__death_date_year

    def get_death_date_year_display(self):
        return self.__death_date_year_display

    def get_death_year_cached(self):
        return self.__death_year_cached

    def get_death_date_display(self):
        return self.__death_date_display

    def get_death_date_iso(self):
        return self.__death_date_iso

    def get_death_date_month_raw(self):
        return self.__death_date_month_raw

    def get_death_date_month_display(self):
        return self.__death_date_month_display

    def get_death_month_cached(self):
        return self.__death_month_cached

    def get_death_date_day_raw(self):
        return self.__death_date_day_raw

    def get_death_date_day_display(self):
        return self.__death_date_day_display

    # NAME PROPERTIES
    def get_name_raw(self):
        return self.__name_raw

    def set_name_raw(self, value):
        if value is not None and value != '':
            self.__name_raw = value.strip()
            self.parse_name()

    def get_name_full(self):
        return self.__name_full

    def set_name_full(self, value):
        self.__name_full = value

    def get_name_first(self):
        return self.__name_first

    def set_name_first(self, value):
        self.__name_first = value

    def get_name_last(self):
        return self.__name_last

    def set_name_last(self, value):
        self.__name_last = value

    def get_name_middle(self):
        return self.__name_middle

    def set_name_middle(self, value):
        self.__name_middle = value

    def get_name_salutation(self):
        return self.__name_salutation

    def set_name_salutation(self, value):
        self.__name_salutation = value

    def get_name_suffix(self):
        return self.__name_suffix

    def set_name_suffix(self, value):
        self.__name_suffix = value

    def get_name_gender_guess(self):
        return self.__name_gender_guess

    def set_name_gender_guess(self, value):
        self.__name_gender_guess = value

    # PLACE: BIRTH
    def set_birth_place_raw(self, value):

        if value is not None and value != '':

            self.__birth_place_raw = value
            geocode_string_source = ''
            skip_geocode = False

            # ditto processing
            if re.search(r'"', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
                # simple ditto
                if re.search(r'^["\s]+$', value) or re.search(r"^Do$", value, re.IGNORECASE):
                    # print('place of birth ditto value = ' + value)
                    value = self.get_previous().get_birth_place_display()
                else:
                    # check for ditto New York State: " State
                    if value == '" State':
                        value = "New York State"
                    # check for ditto Brooklyn Eastern District
                    elif value == '" Eastern District' or value == '" Ed' or value == '" ED' or value == '"Ed':
                        value = "Brooklyn Eastern District"
                    else:
                        # complicated ditto, needs human review
                        self.__birth_place_comments = 'Unable to resolve ditto in birth place'
                        self.set_needs_review(True)
                        skip_geocode = True

            if value is not None and value != '':
                # expand any abbreviations
                place_temp = value
                place_parts = place_temp.split()
                place_reassembled = []
                for place_part in place_parts:
                    if len(place_part) < 6:
                        for key in place_abbrev_dict.keys():
                            if key == place_part.lower():
                                place_part = place_abbrev_dict[key]
                    place_reassembled.append(place_part)
                place_temp = " ".join(place_reassembled)
                if place_temp != self.__birth_place_raw:
                    value = place_temp

                # check for removals
                if re.search(r'removal from', value, re.IGNORECASE):
                    self.__burial_origin = value
                    value = ''

                self.__birth_place_display = value

                if do_geocode_birth and value != '' and not skip_geocode:
                    geocode_string_source = value
                    birth_place_geocoded = self.geocode_place('birth', value)
                else:
                    birth_place_geocoded = get_geocode_dict()

                # set the geo attributes
                self.__birth_geo_location = {"lat": birth_place_geocoded['geo_lat'], "lon": birth_place_geocoded['geo_lng']}
                self.__birth_geo_street_number = birth_place_geocoded['geo_street_number']
                self.__birth_geo_street_name_long = birth_place_geocoded['geo_street_name_long']
                self.__birth_geo_street_name_short = birth_place_geocoded['geo_street_name_short']
                self.__birth_geo_neighborhood = birth_place_geocoded['geo_neighborhood']
                self.__birth_geo_city = birth_place_geocoded['geo_city']
                self.__birth_geo_county = birth_place_geocoded['geo_county']
                self.__birth_geo_state_short = birth_place_geocoded['geo_state_short']
                self.__birth_geo_state_long = birth_place_geocoded['geo_state_long']
                self.__birth_geo_country_long = birth_place_geocoded['geo_country_long']
                self.__birth_geo_country_short = birth_place_geocoded['geo_country_short']
                self.__birth_geo_zip = birth_place_geocoded['geo_zip']
                self.__birth_geo_place_id = birth_place_geocoded['google_place_id']
                self.__birth_geo_formatted_address = birth_place_geocoded['geo_formatted_address']

                # set full birth place description to geo-formatted address
                if birth_place_geocoded['geo_formatted_address'] != "":
                    self.__birth_place_full = birth_place_geocoded['geo_formatted_address']
                else:
                    self.__birth_place_full = value

                # warning if raw place doesn't appear in geocoded result at all
                # if self.__birth_place_full.lower().find(geocode_string_source.lower()) == -1:
                #     self.__needs_review = True
                #     self.__birth_place_comments += "Can't find transcribed place in geocoded place."

    def get_birth_geo_location(self):
        return self.__birth_geo_location

    def get_birth_geo_street_number(self):
        return self.__birth_geo_street_number

    def get_birth_geo_street_name_long(self):
        return self.__birth_geo_street_name_long

    def get_birth_geo_street_name_short(self):
        return self.__birth_geo_street_name_short

    def get_birth_geo_neighborhood(self):
        return self.__birth_geo_neighborhood

    def get_birth_geo_city(self):
        return self.__birth_geo_city

    def get_birth_geo_county(self):
        return self.__birth_geo_county

    def get_birth_geo_state_short(self):
        return self.__birth_geo_state_short

    def get_birth_geo_state_long(self):
        return self.__birth_geo_state_long

    def get_birth_geo_country_long(self):
        return self.__birth_geo_country_long

    def get_birth_geo_country_short(self):
        return self.__birth_geo_country_short

    def get_birth_geo_zip(self):
        return self.__birth_geo_street_name_short

    def get_birth_geo_place_id(self):
        return self.__birth_geo_place_id

    def get_birth_geo_formatted_address(self):
        return self.__birth_geo_formatted_address

    def get_birth_place_full(self):
        return self.__birth_place_full

    def get_birth_place_raw(self):
        return self.__birth_place_raw

    def get_birth_place_display(self):
        return self.__birth_place_display

    def get_birth_place_raw_expand_abbreviations(self):
        return self.__birth_place_raw_expand_abbreviations

    def get_birth_place_comments(self):
        return self.__birth_place_comments

    # PLACE: DEATH
    def set_death_place_raw(self, value):
        if value is None:
            value = ''
        self.__death_place_raw = value
        geocode_string_source = ''

        # ditto processing
        if re.search(r'"', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
            # simple ditto
            if re.search(r'^["\s]+$', value) or re.search(r"^Do$", value, re.IGNORECASE):
                value = self.get_previous().get_death_place_display()
            else:
                # check for ditto New York State: " State
                if value == '" State':
                    value = "New York State"
                # check for ditto Brooklyn Eastern District
                elif value == 'ƒ District' or value == '" Ed' or value == '" ED' or value == '"Ed':
                    value = "Brooklyn Eastern District"
                else:

                    if re.search(r'\d+\"\s+(st|ave|place)', value, re.IGNORECASE):
                        # convert street numbers followed by double quotes to ordinals
                        print("found street ord: " + value)
                        value = re.sub(r'(\d+\")\s+',
                                       lambda m: humanize.ordinal(m.group(1)[:-1]) + " ",
                                       value,
                                       re.IGNORECASE)
                        print("street after: " + value)
                    else:
                        # complicated ditto, needs human review
                        self.__death_place_comments = 'Unable to resolve ditto in death place'
                        self.set_needs_review(True)

        # expand any abbreviations
        if value is not None:
            place_temp = value
            place_parts = place_temp.split()
            place_reassembled = []
            for place_part in place_parts:
                if len(place_part) < 6:
                    for key in place_abbrev_dict.keys():
                        if key == place_part.lower():
                            place_part = place_abbrev_dict[key]
                place_reassembled.append(place_part)
            place_temp = " ".join(place_reassembled)
            if place_temp != self.__death_place_raw:
                value = place_temp

            self.__death_place_display = value

            if do_geocode_death and value != '':
                geocode_string_source = value
                death_place_geocoded = self.geocode_place('death', value)
            else:
                death_place_geocoded = get_geocode_dict()

            # set the geo attributes
            self.__death_geo_location = {"lat": death_place_geocoded['geo_lat'], "lon": death_place_geocoded['geo_lng']}
            self.__death_geo_street_number = death_place_geocoded['geo_street_number']
            self.__death_geo_street_name_long = death_place_geocoded['geo_street_name_long']
            self.__death_geo_street_name_short = death_place_geocoded['geo_street_name_short']
            self.__death_geo_neighborhood = death_place_geocoded['geo_neighborhood']
            self.__death_geo_city = death_place_geocoded['geo_city']
            self.__death_geo_county = death_place_geocoded['geo_county']
            self.__death_geo_state_short = death_place_geocoded['geo_state_short']
            self.__death_geo_state_long = death_place_geocoded['geo_state_long']
            self.__death_geo_country_long = death_place_geocoded['geo_country_long']
            self.__death_geo_country_short = death_place_geocoded['geo_country_short']
            self.__death_geo_zip = death_place_geocoded['geo_zip']
            self.__death_geo_place_id = death_place_geocoded['google_place_id']
            self.__death_geo_formatted_address = death_place_geocoded['geo_formatted_address']

            # set full birth place description to geo-formatted address
            if death_place_geocoded['geo_formatted_address'] != "":
                self.__death_place_full = death_place_geocoded['geo_formatted_address']
            else:
                self.__death_place_full = value

            # warning if raw place doesn't appear in geocoded result at all
            # if self.__death_place_full.lower().find(geocode_string_source.lower()) == -1:
            #     self.__needs_review = True
            #     self.__death_place_comments += "Can't find transcribed place in geocoded place."

    def get_death_geo_location(self):
        return self.__death_geo_location

    def get_death_geo_street_number(self):
        return self.__death_geo_street_number

    def get_death_geo_street_name_long(self):
        return self.__death_geo_street_name_long

    def get_death_geo_street_name_short(self):
        return self.__death_geo_street_name_short

    def get_death_geo_neighborhood(self):
        return self.__death_geo_neighborhood

    def get_death_geo_city(self):
        return self.__death_geo_city

    def get_death_geo_county(self):
        return self.__death_geo_county

    def get_death_geo_state_short(self):
        return self.__death_geo_state_short

    def get_death_geo_state_long(self):
        return self.__death_geo_state_long

    def get_death_geo_country_long(self):
        return self.__death_geo_country_long

    def get_death_geo_country_short(self):
        return self.__death_geo_country_short

    def get_death_geo_zip(self):
        return self.__death_geo_zip

    def get_death_geo_place_id(self):
        return self.__death_geo_place_id

    def get_death_geo_formatted_address(self):
        return self.__death_geo_formatted_address

    def get_death_place_full(self):
        return self.__death_place_full

    def get_death_place_display(self):
        return self.__death_place_display

    def get_death_place_raw(self):
        return self.__death_place_raw

    def get_death_place_raw_expand_abbreviations(self):
        return self.__death_place_raw_expand_abbreviations

    def get_death_place_comments(self):
        return self.__death_place_comments

    # PLACE: RESIDENCE CITY
    def set_residence_place_city_raw(self, value):
        if value is None or value.strip() == '-':
            value = ''
        self.__residence_place_city_raw = value

        # ditto processing
        if re.search(r'"', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
            # simple ditto
            if re.search(r'^["\s]+$', value) or re.search(r"^Do$", value, re.IGNORECASE):
                value = self.get_previous().get_residence_place_city_full()
            else:
                # check for ditto New York State: " State
                if value == '" State':
                    value = "New York State"
                # check for ditto Brooklyn Eastern District
                elif value == '" Eastern District' or value == '" Ed' or value == '" ED' or value == '"Ed':
                    value = "Brooklyn Eastern District"
                # complicated ditto, needs human review
                else:
                    self.__residence_city_comments = 'Unable to resolve ditto in late residence city'
                    self.set_needs_review(True)

        self.__residence_place_city_full = value

        # expand any abbreviations
        if value is not None:
            place_temp = value
            place_parts = place_temp.split()
            place_reassembled = []
            for place_part in place_parts:
                if len(place_part) < 6:
                    for key in place_abbrev_dict.keys():
                        if key == place_part.lower():
                            place_part = place_abbrev_dict[key]
                place_reassembled.append(place_part)
            place_temp = " ".join(place_reassembled)
            if place_temp != self.__residence_place_city_raw:
                self.__residence_place_city_raw_expand_abbreviations = place_temp
                self.__residence_place_city_full = place_temp

    def get_residence_place_city_raw(self):
        return self.__residence_place_city_raw

    def get_residence_place_city_full(self):
        return self.__residence_place_city_full

    def get_residence_city_raw_expand_abbreviations(self):
        return self.__residence_place_city_raw_expand_abbreviations

    # PLACE: RESIDENCE STREET
    def set_residence_place_street_raw(self, value):
        if value is None:
            value = ''
        # convert to string if float or int
        if isinstance(value, float):
            value = str(int(value))
        if isinstance(value, int):
            value = str(value)
        if value.strip() == '-':
            value = ''
        self.__residence_place_street_raw = value

        # ditto processing
        if re.search(r'"', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
            # simple ditto
            if re.search(r'^["\s]+$', value) or re.search(r"^Do$", value, re.IGNORECASE):
                value = self.get_previous().get_residence_place_street_full()
            else:

                if re.search(r'\d+\"\s+(st|ave|place)', value, re.IGNORECASE):
                    # convert street numbers followed by double quotes to ordinals
                    print("found street ord: " + value)
                    value = re.sub(r'(\d+\")\s+',
                                   lambda m: humanize.ordinal(m.group(1)[:-1]) + " ",
                                   value,
                                   re.IGNORECASE)
                    print("street after: " + value)
                else:
                    # complicated ditto, needs human review
                    self.__residence_street_comments = 'Unable to resolve ditto in residence street'
                    self.set_needs_review(True)

        self.__residence_place_street_full = value

        # expand any abbreviations
        place_temp = value
        place_parts = place_temp.split()
        place_reassembled = []
        for place_part in place_parts:
            if len(place_part) < 6:
                for key in place_abbrev_dict.keys():
                    if key == place_part.lower():
                        place_part = place_abbrev_dict[key]
            place_reassembled.append(place_part)
        place_temp = " ".join(place_reassembled)
        if place_temp != self.__death_place_raw:
            self.__residence_place_street_raw_expand_abbreviations = place_temp

    def get_residence_place_street_raw(self):
        return self.__residence_place_street_raw

    def get_residence_place_street_full(self):
        return self.__residence_place_street_full

    def get_residence_street_raw_expand_abbreviations(self):
        return self.__residence_place_street_raw_expand_abbreviations

    # PLACE: RESIDENCE (GEO)
    def set_residence_place_geocode(self):
        geocode_place_temp = ''
        residence_place_geocoded = get_geocode_dict()
        if do_geocode_residence:

            # append street and city before geocoding
            if self.__residence_place_street_raw_expand_abbreviations is not None:
                geocode_place_temp += self.__residence_place_street_raw_expand_abbreviations
            elif self.__residence_place_street_raw is not None:
                geocode_place_temp += self.__residence_place_street_raw
            if self.__residence_place_city_raw_expand_abbreviations is not None:
                geocode_place_temp += " " + self.__residence_place_city_raw_expand_abbreviations
            elif self.__residence_place_city_raw is not None:
                geocode_place_temp += " " + self.__residence_place_city_raw

            if geocode_place_temp != '':
                residence_place_geocoded = self.geocode_place('residence', geocode_place_temp.strip())

        # set the geo attributes
        self.__residence_geo_location = {"lat": residence_place_geocoded['geo_lat'],
                                         "lon": residence_place_geocoded['geo_lng']}
        self.__residence_geo_street_number = residence_place_geocoded['geo_street_number']
        self.__residence_geo_street_name_long = residence_place_geocoded['geo_street_name_long']
        self.__residence_geo_street_name_short = residence_place_geocoded['geo_street_name_short']
        self.__residence_geo_neighborhood = residence_place_geocoded['geo_neighborhood']
        self.__residence_geo_city = residence_place_geocoded['geo_city']
        self.__residence_geo_county = residence_place_geocoded['geo_county']
        self.__residence_geo_state_short = residence_place_geocoded['geo_state_short']
        self.__residence_geo_state_long = residence_place_geocoded['geo_state_long']
        self.__residence_geo_country_long = residence_place_geocoded['geo_country_long']
        self.__residence_geo_country_short = residence_place_geocoded['geo_country_short']
        self.__residence_geo_zip = residence_place_geocoded['geo_zip']
        self.__residence_geo_place_id = residence_place_geocoded['google_place_id']
        self.__residence_geo_formatted_address = residence_place_geocoded['geo_formatted_address']

        # set full description to geo-formatted address
        if residence_place_geocoded['geo_formatted_address'] != "":
            self.__residence_place_full = residence_place_geocoded['geo_formatted_address']
        else:
            self.__residence_place_full = geocode_place_temp

        # warning if raw place doesn't appear in geocoded result at all
        # if self.__residence_place_full.lower().find(geocode_place_temp.lower()) == -1:
        #     self.__needs_review = True
        #     self.__residence_place_comments += "Can't find transcribed place in geocoded place."

    def get_residence_place_full(self):
        return self.__residence_place_full

    def get_residence_geo_location(self):
        return self.__residence_geo_location

    def get_residence_geo_street_number(self):
        return self.__residence_geo_street_number

    def get_residence_geo_street_name_long(self):
        return self.__residence_geo_street_name_long

    def get_residence_geo_street_name_short(self):
        return self.__residence_geo_street_name_short

    def get_residence_geo_neighborhood(self):
        return self.__residence_geo_neighborhood

    def get_residence_geo_city(self):
        return self.__residence_geo_city

    def get_residence_geo_county(self):
        return self.__residence_geo_county

    def get_residence_geo_state_short(self):
        return self.__residence_geo_state_short

    def get_residence_geo_state_long(self):
        return self.__residence_geo_state_long

    def get_residence_geo_country_long(self):
        return self.__residence_geo_country_long

    def get_residence_geo_country_short(self):
        return self.__residence_geo_country_short

    def get_residence_geo_zip(self):
        return self.__residence_geo_zip

    def get_residence_geo_place_id(self):
        return self.__residence_geo_place_id

    def get_residence_geo_formatted_address(self):
        return self.__residence_geo_formatted_address

    # IS PLOT OWNER
    def is_plot_owner(self):
        return self.__is_plot_owner

    def set_is_plot_owner(self, value):
        self.__is_plot_owner = value

    # BURIAL LOCATION
    def set_burial_location_lot_raw(self, value):
        if value is not None:
            if isinstance(value, float):
                value = str(int(value))
            self.__burial_location_lot_raw = str(value).strip()
        else:
            self.__burial_location_lot_raw = ''
        self.parse_burial_location_lot_raw()

    def get_burial_location_lot_raw(self):
        return self.__burial_location_lot_raw

    def get_burial_location_lot(self):
        return self.__burial_location_lot

    def get_burial_location_lot_strike(self):
        return self.__burial_location_lot_strike

    def get_burial_location_lot_comments(self):
        return self.__burial_location_lot_comments

    def get_burial_location_lot_strike_comments(self):
        return self.__burial_location_lot_strike_comments

    def set_burial_location_grave_raw(self, value):
        if value is not None:
            if isinstance(value, float):
                value = str(int(value))
            self.__burial_location_grave_raw = str(value).strip()
        else:
            self.__burial_location_grave_raw = ''
        self.parse_burial_location_grave_raw()

    def get_burial_location_grave_raw(self):
        return self.__burial_location_grave_raw

    def get_burial_location_grave(self):
        return self.__burial_location_grave

    def get_burial_location_grave_strike(self):
        return self.__burial_location_grave_strike

    def get_burial_location_grave_comments(self):
        return self.__burial_location_grave_comments

    def get_burial_location_grave_strike_comments(self):
        return self.__burial_location_grave_strike_comments

    def get_burial_origin(self):
        return self.__burial_origin

    # AGE
    def get_age_years_raw(self):
        return self.__age_years_raw

    def get_age_years(self):
        return self.__age_years

    def get_age_years_comments(self):
        return self.__age_years_comments

    def get_age_months_raw(self):
        return self.__age_months_raw

    def get_age_months(self):
        return self.__age_months

    def get_age_months_comments(self):
        return self.__age_months_comments

    def get_age_days_raw(self):
        return self.__age_days_raw

    def get_age_days(self):
        return self.__age_days

    def get_age_days_comments(self):
        return self.__age_days_comments

    def get_age_hours_raw(self):
        return self.__age_hours_raw

    def get_age_hours(self):
        return self.__age_hours

    def get_age_hours_comments(self):
        return self.__age_hours_comments

    def get_age_display(self):
        if self.__age_display == '':
            return 'Unknown'
        else:
            return self.__age_display.strip()

    def set_age_years_raw(self, value):
        # convert to string if float or int
        if isinstance(value, float):
            value = str(int(value))
        if isinstance(value, int):
            value = str(value)
        self.__age_years_raw = value
        if self.__age_years_raw is None:
            self.__age_years = 0
        elif self.__age_years_raw.isnumeric():
            self.__age_years = int(self.__age_years_raw)
            self.__age_display += str(int(self.__age_years_raw))
            if self.__age_years > 1:
                self.__age_display += " years"
            else:
                self.__age_display += " year"

            if self.__age_years > 110:
                self.__age_years_comments = "Age in years is greater than 110"
                self.set_needs_review(True)
        elif self.__age_years_raw == '-':
            self.__age_years = 0
        elif self.__age_years_raw == '':
            self.__age_years = 0
        else:
            self.__age_years_comments = "Age in years isn't a number or dash"
            self.set_needs_review(True)

    def set_age_months_raw(self, value):
        # convert to string if float or int
        if isinstance(value, float):
            value = str(int(value))
        if isinstance(value, int):
            value = str(value)
        self.__age_months_raw = value
        if self.__age_months_raw is None:
            self.__age_months = 0
        elif self.__age_months_raw.isnumeric():
            self.__age_months = int(self.__age_months_raw)
            if self.__age_display != "":
                self.__age_display += ", "
            self.__age_display += str(int(self.__age_months_raw))
            if self.__age_months > 1:
                self.__age_display += " months"
            else:
                self.__age_display += " month"
            if self.__age_months > 12:
                self.__age_months_comments = "Age in months is greater than 12"
                self.set_needs_review(True)
        elif self.__age_months_raw == '-':
            self.__age_months = 0
        elif self.__age_months_raw == '' or self.__age_months_raw is None:
            self.__age_months = 0
        else:
            self.__age_months_comments = "Age in months isn't a number or dash"
            self.set_needs_review(True)

    def set_age_days_raw(self, value):
        # convert to string if float or int
        if isinstance(value, float):
            value = str(int(value))
        if isinstance(value, int):
            value = str(value)

        # check for 'from cemetery' and add it to display remarks later
        elif value is not None and re.search(r'from cemetery', value, re.IGNORECASE):
            value = re.sub(r'\s*from cemetery\s*', '', value, flags=re.IGNORECASE)
            self.__from_cemetery = self.__age_days_raw

        self.__age_days_raw = value
        days_temp = ''
        hours_temp = None
        if self.__age_days_raw is None:
            self.__age_days = 0
        elif self.__age_days_raw.isnumeric():
            self.__age_days = int(self.__age_days_raw)
            if self.__age_display != "":
                self.__age_display += ", "
            self.__age_display += str(int(self.__age_days_raw)) + " days"
            if self.__age_days > 31:
                self.__age_days_comments = "Age in months is greater than 31"
                self.set_needs_review(True)
        elif self.__age_days_raw == '-':
            self.__age_days = 0
        elif self.__age_days_raw == '':
            self.__age_days = 0

        # this is too crazy, let humans review it
        # elif re.match(r'\d+\s+Hrs?', self.__age_days_raw) is not None:
        #     self.__age_days = 0
        #     hours_temp = re.sub(r'\s+Hrs?', '', self.__age_days_raw)
        # elif re.match(r'(\d+)\s+[Hh]ours?', self.__age_days_raw) is not None:
        #     self.__age_days = 0
        #     hours_temp = re.sub(r'\s+[Hh]ours?', '', self.__age_days_raw)
        # elif self.__age_days_raw.find(r'1/2') != -1:
        #     days_temp = re.sub(r'\s*1/2', '', self.__age_days_raw)
        #     hours_temp = '12'
        # elif self.__age_days_raw.find(r'1/4') != -1:
        #     days_temp = re.sub(r'\s*1/4', '', self.__age_days_raw)
        #     hours_temp = '6'
        # elif self.__age_days_raw.find(r'3/4') != -1:
        #     days_temp = re.sub(r'\s*3/4', '', self.__age_days_raw)
        #     hours_temp = '18'
        # elif re.match(r'\d+\s+Hrs?', self.__age_days_raw) is not None:
        #     self.__age_days = 0
        #     hours_temp = re.sub(r'\s+Hrs?', '', self.__age_days_raw)
        # elif re.match(r'(\d+)\s+[Hh]ours?', self.__age_days_raw) is not None:
        #     self.__age_days = 0
        #     hours_temp = re.sub(r'\s+[Hh]ours?', '', self.__age_days_raw)

        else:
            self.__age_days = 0
            self.__age_days_comments = "Age in days isn't a number"
            self.set_needs_review(True)

        if self.contains_numbers(days_temp) and days_temp != '':
            self.__age_days = int(days_temp)
            self.__age_display += " " + days_temp
            if self.__age_days > 1:
                self.__age_display += " days"
            else:
                self.__age_display += " day"

        if hours_temp is not None:
            self.set_age_hours_raw(hours_temp)

    def set_age_hours_raw(self, value):
        self.__age_hours_raw = value
        if self.__age_hours_raw.isnumeric() or isinstance(value, float):
            self.__age_hours = int(self.__age_hours_raw)
            if self.__age_display != "":
                self.__age_display += ", "
            self.__age_display += str(int(self.__age_hours_raw))
            if self.__age_hours > 1:
                self.__age_display += " hours"
            else:
                self.__age_display += " hour"
            if self.__age_hours > 24:
                self.__age_hours_comments = "Age in hours is greater than 24"
                self.set_needs_review(True)
        elif self.__age_hours_raw == '-':
            self.__age_hours = 0
        elif self.__age_hours_raw == '':
            self.__age_hours = 0
        else:
            self.__age_hours_comments = "Age in hours isn't a number or dash"
            self.set_needs_review(True)

    # MARITAL STATUS
    # MARRIED COLUMN
    def get_marital_status_married_raw(self):
        return self.__marital_status_married_raw

    def get_marital_status_married(self):
        return self.__marital_status_married

    def get_marital_status_married_comments(self):
        return self.__marital_status_married_omments

    def set_marital_status_combined_raw(self, value):
        if value is not None and value.strip() == '-':
            value = ''
        # set one of the 2 raw columns so we can see the transcribed value somewhere
        self.__marital_status_married_raw = value
        self.__marital_status_raw = value
        # ditto
        if self.__marital_status_raw == '"':
            if self.get_previous().__marital_status != 'Not recorded':
                self.__marital_status = self.get_previous().__marital_status
            else:
                self.__marital_status_comments = 'Marital status is ditto but no previous value found'
                self.__needs_review = True

        elif self.__marital_status_raw != '' and self.__marital_status_raw is not None:
            # print(self.__marital_status_married_raw)
            marital_status_key_found = False

            # check for 'from cemetery' and add it to display remarks later
            if re.search(r'from cemetery', self.__marital_status_raw, re.IGNORECASE):
                self.__marital_status = "Not recorded"
                self.__from_cemetery = self.__marital_status_raw

            else:
                for key in marital_status_dict.keys():
                    if key == self.__marital_status_raw.lower():
                        self.__marital_status = (marital_status_dict[key])
                        marital_status_key_found = True
                if not marital_status_key_found:
                    # check for age in hours
                    if re.match(r'(\d+)\s+hours?', self.__marital_status_raw, re.IGNORECASE) is not None:
                        self.__age_days = 0
                        hours_temp = re.sub(r'\s+hours?', '', self.__marital_status_raw, flags=re.IGNORECASE)
                        self.set_age_hours_raw(hours_temp)
                    else:
                        self.__marital_status_comments = 'Marital status not found in list'
                        self.__needs_review = True

                    self.__marital_status = "Not recorded"
        else:
            self.__marital_status = "Not recorded"

    def set_marital_status_married_raw(self, value):
        self.__marital_status_married_raw = value
        # ditto
        if self.__marital_status_married_raw == '"':
            # if self.get_previous().__marital_status_married != 'Not recorded':
            #     self.__marital_status_married = self.get_previous().__marital_status_married
            # else:
            #     self.__marital_status_married_comments = 'Marital status is ditto but no previous value found'
            #     self.__needs_review = True
            self.__marital_status_married = "Married"

        elif self.__marital_status_married_raw != '' and self.__marital_status_married_raw is not None:
            # print(self.__marital_status_married_raw)
            marital_status_key_found = False

            # check for 'from cemetery' and add it to display remarks later
            if re.search(r'from cemetery', self.__marital_status_married_raw, re.IGNORECASE):
                self.__marital_status_married = "Not recorded"
                self.__from_cemetery = self.__marital_status_married_raw

            else:
                for key in marital_status_dict.keys():
                    if key == self.__marital_status_married_raw.lower():
                        self.__marital_status_married = (marital_status_dict[key])
                        marital_status_key_found = True
                if not marital_status_key_found:
                    # check for age in hours
                    if re.match(r'(\d+)\s+hours?', self.__marital_status_married_raw, re.IGNORECASE) is not None:
                        self.__age_days = 0
                        hours_temp = re.sub(r'\s+hours?', '', self.__marital_status_married_raw, flags=re.IGNORECASE)
                        self.set_age_hours_raw(hours_temp)
                    else:
                        self.__marital_status_married_comments = 'Marital status not found in list'
                        self.__needs_review = True

                    self.__marital_status_married = "Not recorded"
        else:
            self.__marital_status_married = "Not recorded"


    # SINGLE COLUMN
    def get_marital_status_single_raw(self):
        return self.__marital_status_single_raw

    def get_marital_status_single(self):
        return self.__marital_status_single

    def get_marital_status_single_comments(self):
        return self.__marital_status_single_comments

    def set_marital_status_single_raw(self, value):
        self.__marital_status_single_raw = value
        # ditto
        if self.__marital_status_single_raw == '"':
            # if self.get_previous().__marital_status_single != 'Not recorded':
            #     self.__marital_status_single = self.get_previous().__marital_status_single
            # else:
            #     self.__marital_status_single_comments = 'Marital status is ditto but no previous value found'
            #     self.__needs_review = True
            self.__marital_status_single = "Single"
        elif self.__marital_status_single_raw != '' and self.__marital_status_single_raw is not None:
            marital_status_key_found = False
            for key in marital_status_dict.keys():
                if key == self.__marital_status_single_raw.lower():
                    self.__marital_status_single = (marital_status_dict[key])
                    marital_status_key_found = True
            if not marital_status_key_found:
                self.__marital_status_single_comments = 'Marital status not found in list'
                self.__needs_review = True
        else:
            self.__marital_status_single = "Not recorded"

    # merge marital status columns
    def set_marital_status(self, value):
        self.__marital_status = value

    def get_marital_status(self):
        return self.__marital_status

    # CAUSE OF DEATH
    def set_cause_of_death_raw(self, value):
        if value is None:
            value = ''
        self.__cause_of_death_raw = value

        # ditto processing
        if re.search(r'"', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
            # simple ditto
            if re.search(r'^["\s]+$', value) or re.search(r"^Do$", value, re.IGNORECASE):
                self.__cause_of_death_display = self.get_previous().__cause_of_death_display
            else:
                # complicated ditto, needs human review
                self.__cause_of_death_display = value
                self.__cause_of_death_comments = 'Unable to resolve ditto marks in cause of death'
                self.set_needs_review(True)
        elif value == '-':
            self.__cause_of_death_display = ''
        else:
            self.__cause_of_death_display = value

        # 'Ult' - ultimate month?
        m = re.search(r"ult\s+(.+)", self.__cause_of_death_display, re.IGNORECASE)
        if m is not None:
            self.__cause_of_death_display = m.group(1)
            self.__ultimate_month = 'REQUIRED'
            self.__needs_review = True
            self.__cause_of_death_comments = "Need to adjust death date to ultimate month."

    def get_cause_of_death_raw(self):
        return self.__cause_of_death_raw

    def get_cause_of_death_display(self):
        return self.__cause_of_death_display

    def get_cause_of_death_comments(self):
        return self.__cause_of_death_comments

    # UNDERTAKER
    def set_undertaker_raw(self, value):
        if value is None:
            value = ''
        self.__undertaker_raw = value
        # ditto?
        if re.search(r'^["\s]+$', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
            if self.get_previous().__undertaker_display is not None and self.get_previous().__undertaker_display != '':
                self.__undertaker_display = self.get_previous().__undertaker_display
            else:
                self.__undertaker_comments = 'Unable to determine undertaker'
                self.__needs_review = True
        elif value == '-':
            self.__undertaker_display = ''
        else:
            self.__undertaker_display = value

    def get_undertaker_raw(self):
        return self.__undertaker_raw

    def get_undertaker_display(self):
        return self.__undertaker_display

    def get_undertaker_comments(self):
        return self.__undertaker_comments

    # REMARKS
    def set_remarks_raw(self, value):
        if value is None:
            value = ''
        if type(value) is not str:
            value = str(value)
        self.__remarks_raw = value
        self.__remarks_display = ''

        # ditto processing
        if re.search(r'"', value) or re.search(r"\bDo\b", value, re.IGNORECASE):
            # simple ditto
            if re.search(r'^["\s]+$', value) or re.search(r"^Do$", value, re.IGNORECASE):
                if self.get_previous().__remarks_display is not None and self.get_previous().__remarks_display != '':
                    self.__remarks_display = self.get_previous().__remarks_display
            else:

                if re.search(r'\d+\"\s+', value, re.IGNORECASE):
                    # convert date followed by double quotes to ordinals
                    print("found date ord: " + value)
                    value = re.sub(r'(\d+\")\s+',
                                   lambda m: humanize.ordinal(m.group(1)[:-1]) + " ",
                                   value,
                                   re.IGNORECASE)
                    print("date after: " + value)
                else:
                    # complicated ditto, needs human review
                    self.__remarks_comments = 'Unable to resolve ditto in remarks'
                    self.__needs_review = True

                self.__remarks_display = value

        elif value == '-':
            self.__remarks_display = ''
        else:
            self.__remarks_display = value

        # removal from?
        if re.search('removal from', self.__remarks_display, re.IGNORECASE):
            self.__is_removal_from = True

        # removed to?
        if re.search('removed to', self.__remarks_display, re.IGNORECASE):
            self.__is_removed_to = True

        # append from cemetery if it was found earlier
        if self.__from_cemetery is not None and self.__from_cemetery != '':
            self.__remarks_display += " " + self.__from_cemetery

    def get_remarks_raw(self):
        return self.__remarks_raw

    def get_remarks_display(self):
        return self.__remarks_display

    def get_remarks_comments(self):
        return self.__remarks_comments

    # HAS DIAGRAM
    def get_has_diagram(self):
        return self.__has_diagram

    def set_has_diagram(self, value):
        self.__has_diagram = value
        if value is not None and value != '':
            self.__has_diagram = True
            # print('Diagram: "' + value + '"')

    # ULTIMATE MONTH FOR DEATH DATE
    def get_ultimate_month(self):
        return self.__ultimate_month

    def set_ultimate_month(self, value):
        self.__ultimate_month = value

    # ADMINISTRATIVE
    def get_needs_review(self):
        return self.__needs_review

    def set_needs_review(self, value):
        self.__needs_review = value

    def get_transcriber_requests_review(self):
        return self.__transcriber_requests_review

    def set_transcriber_requests_review(self, value):
        self.__transcriber_requests_review = value
        if value is not None and value != '':
            self.__needs_review = True
            # print('Review: "' + value + '"')

    def get_needs_review_comments(self):
        return self.__needs_review_comments

    def set_needs_review_comments(self):
        sep = ", "
        available_comments = [
            self.__registry_volume_page_comments,
            self.__interment_date_comments,
            self.__death_date_comments,
            self.__death_date_iso_comments,
            self.__missing_death_date_comments,
            self.__interment_date_iso_comments,
            self.__birth_place_comments,
            self.__death_place_comments,
            self.__residence_place_comments,
            self.__burial_location_lot_comments,
            self.__burial_location_lot_strike_comments,
            self.__burial_location_grave_comments,
            self.__burial_location_grave_strike_comments,
            self.__age_years_comments,
            self.__age_months_comments,
            self.__age_days_comments,
            self.__age_hours_comments,
            self.__marital_status_comments,
            self.__marital_status_married_comments,
            self.__marital_status_single_comments,
            self.__cause_of_death_comments,
            self.__undertaker_comments,
            self.__remarks_comments,
            self.__geocode_comments,
            self.__name_comments,
            self.__residence_city_comments,
            self.__residence_street_comments,
            self.__interment_id_comments
        ]
        comments = []
        for comment in available_comments:
            if comment != '':
                comments.append(comment)
        if self.__transcriber_requests_review:
            comments.append("Transcriber requests review")
        all_comments = ''
        all_comments = sep.join(comments)
        # if all_comments != '':
        #     print(all_comments)
        print('ID: ' + str(self.__id) + ' [' + all_comments + ']')

        self.__needs_review_comments = all_comments

    # CLASS FUNCTIONS
    def parse_burial_location_lot_raw(self):
        lot_raw = self.__burial_location_lot_raw

        # simple ditto processing
        if re.search(r'^["\s]+$', lot_raw):
            self.__burial_location_lot = self.get_previous().get_burial_location_lot()
            self.__burial_location_lot_strike = self.get_previous().get_burial_location_lot_strike()
            return

        m = re.search(r"\[(.+)\]", lot_raw)
        if m is not None:
            # there might be multiple strike through values
            lot_strike_temp = m.group(1).replace('[', ' ').replace(']', ' ')
            self.__burial_location_lot_strike = " ".join(lot_strike_temp.split())
            self.__burial_location_lot = re.sub(r'\[.+\]', '', lot_raw).strip()
            if self.__burial_location_lot_strike != '' and self.__burial_location_lot_strike is not None:
                if not self.contains_numbers(self.__burial_location_lot_strike):
                    self.__burial_location_lot_strike_comments = "Burial location contains no numbers"
                    self.__needs_review = True
            if self.__burial_location_lot != '' and self.__burial_location_lot is not None:
                if not self.contains_numbers(self.__burial_location_lot):
                    self.__burial_location_lot_comments = "Burial location contains no numbers"
                    self.__needs_review = True
        else:
            self.__burial_location_lot = lot_raw
            if self.__burial_location_lot != '' and self.__burial_location_lot is not None:
                if not self.contains_numbers(self.__burial_location_lot):
                    self.__burial_location_lot_comments = "Burial location contains no numbers"
                    self.__needs_review = True

    def parse_burial_location_grave_raw(self):
        grave_raw = self.__burial_location_grave_raw

        # simple ditto processing
        if re.search(r'^["\s]+$', grave_raw):
            self.__burial_location_grave = self.get_previous().get_burial_location_grave()
            self.__burial_location_grave_strike = self.get_previous().get_burial_location_grave_strike()
            return

        m = re.search(r"\[(.+)\]", grave_raw)
        if m is not None:
            # there might be multiple strike through values
            grave_strike_temp = m.group(1).replace('[', ' ').replace(']', ' ')
            self.__burial_location_grave_strike = " ".join(grave_strike_temp.split())
            self.__burial_location_grave = re.sub(r'\[.+\]', '', grave_raw).strip()
            if self.__burial_location_grave_strike != '' and self.__burial_location_grave_strike is not None:
                if not self.contains_numbers(self.__burial_location_grave_strike) and \
                        self.__burial_location_grave_strike != '-':
                    self.__burial_location_grave_strike_comments = "Grave location contains no numbers."
                    self.__needs_review = True
            if self.__burial_location_grave != '' and self.__burial_location_grave is not None:
                if not self.contains_numbers(self.__burial_location_grave) and self.__burial_location_grave != '-':
                    self.__burial_location_grave_comments = "Grave location contains no numbers."
                    self.__needs_review = True
        else:
            self.__burial_location_grave = grave_raw
            if self.__burial_location_grave != '' and self.__burial_location_grave is not None:
                if not self.contains_numbers(self.__burial_location_grave) and self.__burial_location_grave != '-':
                    self.__burial_location_grave_comments = "Grave location contains no numbers."
                    self.__needs_review = True

    def parse_name(self):

        name_temp = self.__name_raw
        infant_no_first_name = False
        is_ditto = False

        # ditto processing
        if re.search(r'"', name_temp) or re.search(r"\bDo\b", name_temp, re.IGNORECASE):
            is_ditto = True
            # simple ditto
            if re.search(r'^["\s]+$', name_temp) or re.search(r"^Do$", name_temp, re.IGNORECASE):
                name_temp = self.get_previous().get_name_full()
            else:
                # complicated ditto, needs human review
                self.__name_comments = 'Unable to resolve ditto marks in name'
                self.set_needs_review(True)

        # infant parsing
        if re.search(r"child\s+(of|no)\s+", name_temp, re.IGNORECASE):
            infant_no_first_name = True

            # child, no surname
            if re.search(r"child no name", name_temp, re.IGNORECASE):
                self.__name_full = name_temp
                name_temp = None

            if name_temp is not None:
                # "a male child of" or "a female child of"
                m = re.search(r"a\s+(\w*male)\s+child\s+of\s+(.*)", name_temp, re.IGNORECASE)
                if m is not None:
                    name_temp = m.group(2)
                    if m.group(1).lower() == "male":
                        self.__name_gender_guess = "M"
                    if m.group(1).lower() == "female":
                        self.__name_gender_guess = "F"

        if name_temp is not None:

            # contains a plus sign? strip and designate as plot owner?
            if re.search(r'\+', name_temp):
                name_temp = name_temp.replace('+', '').strip()
                self.set_is_plot_owner(True)

            # replace suffixes that HumanName can't recognize
            if re.search(r"Jur$", name_temp):
                name_temp = name_temp.replace("Jur", "Jr")

            # expand any abbreviated names using name-abbrev dictionary
            name_parts = name_temp.split()
            name_reassembled = []
            for name_part in name_parts:
                if len(name_part) < 6:
                    for key in name_abbrev_dict.keys():
                        if key == name_part.lower():
                            name_part = name_abbrev_dict[key]
                name_reassembled.append(name_part)
            name_temp = " ".join(name_reassembled)

            name = HumanName(name_temp)
            if infant_no_first_name:
                self.__name_last = name.last
                if is_ditto:
                    self.__name_full = self.get_previous().get_name_full()
                else:
                    self.__name_full = self.__name_raw
            else:
                self.__name_first = name.first
                self.__name_last = name.last
                self.__name_middle = name.middle
                self.__name_salutation = name.title
                self.__name_suffix = name.suffix
                self.__name_full = name_temp

                if self.__name_first is not None:
                    self.guess_gender()

    def guess_gender(self):
        # try to guess gender using first namegenderpro database
        # just grab first part of any first name (eg: Mary Jane)
        name_first_gender_temp = self.__name_first.split(' ')[0]
        try:
            gender_row = cursor.execute(
                "SELECT gender from namegenderpro where name = '" + name_first_gender_temp + "' COLLATE NOCASE").fetchone()
            if gender_row:
                self.__name_gender_guess = gender_row[0]
        except sqlite3.OperationalError as e:
            print(e)
            return

    def parse_registry_volume_page(self, lookup_years):
        try:
            m = re.search(r'Volume\s+(\d+)_(\d+)', self.get_registry_image_filename_raw(), re.IGNORECASE)
            if m is None:
                self.__needs_review = True
                self.__registry_volume_page_comments = "Unable to parse transcribed image filename: " + \
                                                       self.__registry_image_filename_raw
            else:
                self.__registry_volume = m.group(1)
                self.__registry_page = m.group(2)
                # normalize filename to match convention used on the image file server
                self.__registry_image_filename = "Volume " + self.__registry_volume + "_" + self.__registry_page

                # no year columns from transcriber, lookup in dictionary
                if lookup_years:
                    self.determine_interment_year()
                    self.determine_death_year()

                # todo: check if image exists on server
                self.__registry_image_link = "https://www.green-wood.com/scans/Volume%20" + m.group(1) + "/Volume%20" + m.group(1) + "_" + m.group(2) + ".jpg"

        except re.error:
            self.__needs_review = True
            self.__registry_volume_page_comments = "Unable to parse transcribed image filename: " + \
                                                   self.__registry_image_filename_raw

    # try to set interment year based on volume and id in dictionaries/interment_year_ranges.json
    def determine_interment_year(self):
        found_volume = False
        if self.__registry_volume is not None \
                and self.__id is not None \
                and self.__id != '' \
                and isinstance(self.__id, int) \
                and self.__id > 0:
            for vols in interment_year_dict:
                if vols['volume'] == self.__registry_volume:
                    found_volume = True
                    for range_item in vols['ranges']:
                        if range_item['begin'] <= self.__id <= range_item['end']:
                            self.__interment_date_year = range_item['year']
                            break
                    if self.__interment_date_year is None:
                        self.__needs_review = True
                        self.__interment_date_comments += "Can't find interment year"
                    break
            if not found_volume:
                self.__needs_review = True
                self.__interment_date_comments += "Can't find volume " + \
                                                  self.__registry_volume + \
                                                  " in dictionaries/interment_year_ranges.json"
        else:
            self.__needs_review = True
            self.__interment_date_comments += "Can't determine interment year since ID is missing or not an integer"

    # try to set death year based on volume and id in dictionaries/death_year_ranges.json
    def determine_death_year(self):
        found_volume = False
        if self.__registry_volume is not None \
                and self.__id is not None \
                and self.__id != '' \
                and isinstance(self.__id, int) \
                and self.__id > 0:
            for vols in death_year_dict:
                if vols['volume'] == self.__registry_volume:
                    found_volume = True
                    for range_item in vols['ranges']:
                        if range_item['begin'] <= self.__id <= range_item['end']:
                            self.__death_date_year = range_item['year']
                            break
                    if self.__death_date_year is None:
                        self.__needs_review = True
                        self.__death_date_comments += "Can't find death year"
                    break
            if not found_volume:
                self.__needs_review = True
                self.__death_date_comments += "Can't find volume " + \
                    self.__registry_volume + " in dictionaries/death_year_ranges.json"
        else:
            self.__death_date_year = None
            self.__needs_review = True
            self.__death_date_comments += "Can't determine death year since ID is missing or not an integer"

    # ==================================================================================================================
    # GEOCODE PLACE
    # ==================================================================================================================
    def geocode_place(self, place_type, place):

        vol = self.__registry_volume
        intern_id = self.__id
        d = get_geocode_dict()
        # return empty dictionary if no place is specified
        if place == '':
            return d
        else:
            if place == 'Brooklyn Eastern District':
                place = 'Brooklyn'
            d['place_geocode_input'] = place

        geocode_filename = 'json/places/' + parameterize(place.lower().strip(), separator="_") + '.json'
        if place != '' and os.path.exists(geocode_filename) is False:

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
                    geo_file = open(geocode_filename, 'w')
                    json.dump(d, geo_file, indent=4, sort_keys=True)
                    geo_file.close()
                    return d
                except Exception as e:
                    logging.fatal(getattr(e, 'message', repr(e)))
            else:
                # logging.warning(
                #     '"' + vol + '","' + str(int(intern_id)) + '","' + "Unable geocode " + place_type + " place: " +
                #     place + '"')
                # serialize empty geo place
                self.__geocode_comments = "Unable to geocode " + place_type + " place: " + place
                self.__needs_review = True
                h = open(geocode_filename, 'w')
                json.dump(d, h, indent=4, sort_keys=True)
                h.close()
                return d
        else:
            # return serialized geocodes
            if os.path.exists(geocode_filename):
                with open(geocode_filename) as json_file:
                    place_json = json.load(json_file)
                    if place_json["google_place_id"] == "":
                        # logging.warning('"' + vol + '","' + str(
                        #     int(intern_id)) + '","' + "Unable geocode " + place_type + " place: " + place + '"')
                        self.__geocode_comments = "Unable to geocode " + place_type + " place: " + place
                        self.__needs_review = True
                    return place_json
            else:
                return d

    def to_json(self):

        # create a deep copy and remove previous property
        temp_obj = copy.deepcopy(self)
        # for att in dir(temp_obj):
        #     print(att, getattr(temp_obj, att))
        if hasattr(temp_obj, '_Interment__previous'):
            del temp_obj.__previous
        json_string = json.dumps(temp_obj, default=lambda o: o.__dict__, indent=4, sort_keys=False)
        json_string = json_string.replace('_Interment__', '')
        return json_string

    def to_csv(self, include_header):
        # create a deep copy and remove previous property
        temp_obj = copy.deepcopy(self)
        # for att in dir(temp_obj):
        #     print(att, getattr(temp_obj, att))
        if hasattr(temp_obj, '_Interment__previous'):
            del temp_obj.__previous

        df = pd.DataFrame.from_records(temp_obj.__dict__)
        # df.to_csv('pandas_test.csv')
        csv_string = df.to_csv(header=include_header)
        csv_string = csv_string.replace('_Interment__', '')
        return csv_string

    def contains_numbers(self, d):
        _digits = re.compile(r'\d')
        return bool(_digits.search(d))

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
