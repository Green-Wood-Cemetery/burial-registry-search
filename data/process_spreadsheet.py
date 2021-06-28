import json
import re
import dateparser
import requests
import logging
from nameparser import HumanName
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.styles import NamedStyle
from openpyxl.styles import Font, Color, Alignment, Border, Side, colors
from openpyxl.comments import Comment
import argparse
import sqlite3
from inflection import parameterize
from os import path
import time
import googlemaps
import sys
sys.path.insert(0, '..')
from lib.interment import Interment

# command line arguments
parser = argparse.ArgumentParser(description='Spreadsheet to JSON')
parser.add_argument('-input', type=str, help='spreadsheet in xslx format')
parser.add_argument('-key', type=str, help='google api key')
parser.add_argument('-sheet', type=str, help='worksheet to transform')
parser.add_argument('-vol', type=str, help='registry volume number')
args = parser.parse_args()
workbook = load_workbook(filename=args.input, data_only=True)

# sheet = workbook.active
sheet = workbook[args.sheet]

# spreadsheet column constants
IMAGE_FILENAME = 0
INTERMENT_ID = 1
INTERMENT_MONTH = 2
INTERMENT_DAY = 3
NAME = 4
LOT_LOCATION = 5
GRAVE_LOCATION = 6
BIRTH_PLACE = 7
AGE_YEARS = 8
AGE_MONTHS = 9
AGE_DAYS = 10
MARITAL_STATUS_MARRIED = 11
MARITAL_STATUS_SINGLE = 12
RESIDENCE_CITY = 13
RESIDENCE_STREET = 14
DEATH_LOCATION = 15
DEATH_MONTH = 16
DEATH_DAY = 17
CAUSE_OF_DEATH = 18
UNDERTAKER = 19
NOTES = 20
HAS_DIAGRAM = 21
NEEDS_REVIEW = 22

# =====================================================================================================================
# MAIN
# =====================================================================================================================
interments = []

count = 2
max = 999999
# Using the values_only because you want to return the cells' values

previous = Interment()

wb = Workbook()
ws = wb.active

# EXCEL HEADERS
# create the style template
header = NamedStyle(name="header")
header.font = Font(bold=True)
header.alignment = Alignment(horizontal="center")
header.border = Border(bottom=Side(border_style="thin"))

content = NamedStyle(name="content")
content.alignment = Alignment(horizontal="left")

ws.append([
    "Interment ID\n[TRANSCRIBED]",
    "Image Number\n[TRANSCRIBED]",
    "Interment Date: Month\n[TRANSCRIBED]",
    "Interment Date: Day\n[TRANSCRIBED]",
    "Interment Date: Year\n[TRANSCRIBED]",
    "Interment Date\n[DISPLAYED VALUE]",
    "Name\n[TRANSCRIBED]",
    "Name\n[DISPLAYED VALUE]",
    "Name - Last\n[SEARCH ONLY]",
    "Name - First\n[SEARCH ONLY]",
    "Name - Middle\n[SEARCH ONLY]",
    "Name - Salutation\n[SEARCH ONLY]",
    "Name - Suffix\n[SEARCH ONLY]",
    "Name: Lot Owner\n[DISPLAYED VALUE]",
    "Name: Gender Guess\n[DISPLAYED VALUE]",
    "Lot\n[TRANSCRIBED]",
    "Lot: Current\n[DISPLAYED VALUE]",
    "Lot: Previous\n[DISPLAYED VALUE]",
    "Grave\n[TRANSCRIBED]",
    "Grave: Current\n[DISPLAYED VALUE]",
    "Grave: Previous\n[DISPLAYED VALUE]",
    "Birth Place\n[TRANSCRIBED]",
    "Birth Place\n[DISPLAYED VALUE]",
    "Birth Place: Geocoded\n[DISPLAYED VALUE]",
    "Age: Years\n[TRANSCRIBED]",
    "Age: Months\n[TRANSCRIBED]",
    "Age: Days\n[TRANSCRIBED]",
    "Age: Hours\n[TRANSCRIBED]",
    "Age: Display\n[DISPLAYED VALUE]",
    "Age: Years\n[SEARCH ONLY]",
    "Age: Months\n[SEARCH ONLY]",
    "Age: Days\n[SEARCH ONLY]",
    "Age: Hours\n[SEARCH ONLY]",
    "Marital Status: Married\n[TRANSCRIBED]",
    "Marital Status: Single\n[TRANSCRIBED]",
    "Marital Status: Merged\n[DISPLAYED VALUE]",
    "Late Residence: City\n[TRANSCRIBED]",
    "Late Residence: City\n[DISPLAYED VALUE]",
    "Late Residence: Street\n[TRANSCRIBED]",
    "Late Residence: Street\n[DISPLAYED VALUE]",
    "Late Residence: Geocoded\n[DISPLAYED VALUE]",
    "Place of Death\n[TRANSCRIBED]",
    "Place of Death\n[DISPLAYED VALUE]",
    "Place of Death: Geocoded\n[DISPLAYED VALUE]",
    "Death Date: Month\n[TRANSCRIBED]",
    "Death Date: Day\n[TRANSCRIBED]",
    "Death Date: Year\n[TRANSCRIBED]",
    "Death Date\n[DISPLAYED VALUE]",
    "Death Date: Ult Month\n[DISPLAYED VALUE]",
    "Cause of Death\n[TRANSCRIBED]",
    "Cause of Death\n[DISPLAYED VALUE]",
    "Undertaker\n[TRANSCRIBED]",
    "Undertaker\n[DISPLAYED VALUE]",
    "Remarks\n[TRANSCRIBED]",
    "Remarks\n[DISPLAYED VALUE]",
    "Has Diagram\n",
    "Needs Review\n"


])
for cell in ws["1:1"]:
    cell.style = header

print('[')
for row in sheet.iter_rows(min_row=4, values_only=True):

    if row[INTERMENT_ID] is not None and count < max:

        i = Interment()
        i.set_previous(previous)
        i.set_id(row[INTERMENT_ID])
        i.set_registry_image_filename_raw(str(row[IMAGE_FILENAME]).strip())
        i.set_interment_date(row[INTERMENT_MONTH], row[INTERMENT_DAY])
        i.set_name_raw(row[NAME])
        i.set_burial_location_lot_raw(row[LOT_LOCATION])
        i.set_burial_location_grave_raw(row[GRAVE_LOCATION])
        i.set_birth_place_raw(row[BIRTH_PLACE])
        i.set_age_years_raw(row[AGE_YEARS])
        i.set_age_months_raw(row[AGE_MONTHS])
        i.set_age_days_raw(row[AGE_DAYS])
        i.set_marital_status_married_raw(row[MARITAL_STATUS_MARRIED])
        i.set_marital_status_single_raw(row[MARITAL_STATUS_SINGLE])

        # merge marital status columns for display
        if i.get_marital_status_married() == 'Not recorded' and i.get_marital_status_single() != 'Not recorded':
            i.set_marital_status(i.get_marital_status_single())
        else:
            i.set_marital_status(i.get_marital_status_married())

        i.set_residence_place_street_raw(row[RESIDENCE_STREET])
        i.set_residence_place_city_raw(row[RESIDENCE_CITY])
        i.set_residence_place_geocode()

        i.set_death_place_raw(row[DEATH_LOCATION])
        i.set_death_date(row[DEATH_MONTH], row[DEATH_DAY])

        i.set_cause_of_death_raw(row[CAUSE_OF_DEATH])
        i.set_undertaker_raw(row[UNDERTAKER])
        i.set_remarks_raw(row[NOTES])
        if row[HAS_DIAGRAM] is not None:
            i.set_has_diagram(True)
        if row[NEEDS_REVIEW] is not None:
            i.set_needs_review(True)

        # print(i.to_json() + ",")

        # if count == 0:
        #     print(i.to_csv(True))
        # else:
        #     print(i.to_csv(False))

        # EXCEL OUTPUT
        ws.append([
            i.get_id(),
            i.get_registry_image_filename(),
            i.get_interment_date_month_raw(),
            i.get_interment_date_day_raw(),
            i.get_interment_date_year(),
            i.get_interment_date_display(),
            i.get_name_raw(),
            i.get_name_full(),
            i.get_name_last(),
            i.get_name_first(),
            i.get_name_middle(),
            i.get_name_salutation(),
            i.get_name_suffix(),
            i.is_plot_owner(),
            i.get_name_gender_guess(),
            i.get_burial_location_lot_raw(),
            i.get_burial_location_lot(),
            i.get_burial_location_lot_strike(),
            i.get_burial_location_grave_raw(),
            i.get_burial_location_grave(),
            i.get_burial_location_grave_strike(),
            i.get_birth_place_raw(),
            i.get_birth_place_display(),
            i.get_birth_place_full(),
            i.get_age_years_raw(),
            i.get_age_months_raw(),
            i.get_age_days_raw(),
            i.get_age_hours_raw(),
            i.get_age_display(),
            i.get_age_years(),
            i.get_age_months(),
            i.get_age_days(),
            i.get_age_hours(),
            i.get_marital_status_married_raw(),
            i.get_marital_status_single_raw(),
            i.get_marital_status(),
            i.get_residence_place_city_raw(),
            i.get_residence_place_city_full(),
            i.get_residence_place_street_raw(),
            i.get_residence_place_street_full(),
            i.get_residence_place_full(),
            i.get_death_place_raw(),
            i.get_death_place_display(),
            i.get_death_place_full(),
            i.get_death_date_month_raw(),
            i.get_death_date_day_raw(),
            i.get_death_date_year(),
            i.get_death_date_display(),
            i.get_ultimate_month(),
            i.get_cause_of_death_raw(),
            i.get_cause_of_death_display(),
            i.get_undertaker_raw(),
            i.get_undertaker_display(),
            i.get_remarks_raw(),
            i.get_remarks_display(),
            i.get_has_diagram(),
            i.get_needs_review()

        ])

        # add image links
        ws.cell(row=count, column=2).hyperlink = i.get_registry_image_link()
        ws.cell(row=count, column=2).value = i.get_registry_image_filename()
        ws.cell(row=count, column=2).style = "Hyperlink"

        # add comments
        # idcell = ws.cell(row=count, column=1)
        # idcell.comment = Comment(u'This is the comment', u'Comment Author', )

        for cell in ws[count:count]:
            cell.style = content

        previous = i
        count += 1
print(']')

# # hide parsed name columns except for last name
# for col in ['J', 'K', 'L', 'M']:
#     ws.column_dimensions[col].hidden = True
# # hide age columns
# for col in ['AD', 'AE', 'AF', 'AG']:
#     ws.column_dimensions[col].hidden = True

wb.save("test.xlsx")
