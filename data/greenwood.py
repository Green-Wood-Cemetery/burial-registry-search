import json
import dateparser
from openpyxl import load_workbook

workbook = load_workbook(filename="excel/greenwood 08022020.xlsx")
sheet = workbook.active

internments = []

# Using the values_only because you want to return the cells' values
for row in sheet.iter_rows(min_row=3, values_only=True):

    if row[4] is not None:

        # --- INTERNMENT ID
        intern_id = row[4]

        # --- REGISTRY IMAGE FILENAME
        image_filename = row[0]

        # --- INTERNMENT DATE
        intern_date_display = ''
        intern_date_iso = ''
        intern_year = ''
        # internment month
        if row[1] is not None:
            intern_date_display += row[1] + " "
        # internment day
        if row[2] is not None:
            intern_date_display += str(int(row[2])) + ", "
        # internment year
        if row[3] is not None:
            intern_date_display += str(int(row[3]))
            intern_year = int(row[3])
        intern_date = ''
        if intern_date_display is not '':
            dt = dateparser.parse(intern_date_display)
            intern_date_iso = dt.strftime("%Y-%m-%d")


        internment = {
            "intern_id": intern_id,
            "image_filename": image_filename,
            "intern_date_display" : intern_date_display,
            "intern_date_iso": intern_date_iso,
            "intern_year": intern_year

        }
        internments.append(internment)

print(json.dumps(internments))