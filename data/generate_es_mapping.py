#!/usr/bin/python

# python3 generate_es_mapping.py > interments-mappings.json

import json
from lib.interment import Interment

# load field dictionary
# with open('dictionaries/es_fields.json') as f:
#     es_fields = json.load(f)

es_fields = {
    "fields":
        [
            "interment_id",
            "registry_image",
            "registry_volume",
            "registry_page",
            "name_first",
            "name_last",
            "name_middle",
            "name_full",
            "name_salutation",
            "name_infant",
            "interment_date_display",
            "interment_date_iso",
            "interment_date_year",
            "death_date_display",
            "death_date_iso",
            "death_date_year",
            "birth_place_display",
            "birth_geo_place_id",
            "birth_geo_location",
            "birth_geo_street_number",
            "birth_geo_street_name_long",
            "birth_geo_street_name_short",
            "birth_geo_neighborhood",
            "birth_geo_country_short",
            "birth_geo_country_long",
            "birth_geo_city",
            "birth_geo_state_long",
            "birth_geo_state_short",
            "birth_geo_county",
            "birth_geo_zip",
            "birth_geo_lat",
            "birth_geo_lng",
            "birth_geo_formatted_address",
            "death_place_display",
            "death_geo_place_id",
            "death_geo_location",
            "death_geo_street_number",
            "death_geo_street_name_long",
            "death_geo_street_name_short",
            "death_geo_neighborhood",
            "death_geo_country_short",
            "death_geo_country_long",
            "death_geo_city",
            "death_geo_state_long",
            "death_geo_state_short",
            "death_geo_county",
            "death_geo_zip",
            "death_geo_lat",
            "death_geo_lng",
            "death_geo_formatted_address",
            "residence_place_display",
            "residence_geo_place_id",
            "residence_geo_location",
            "residence_geo_street_number",
            "residence_geo_street_name_long",
            "residence_geo_street_name_short",
            "residence_geo_neighborhood",
            "residence_geo_country_short",
            "residence_geo_country_long",
            "residence_geo_city",
            "residence_geo_state_long",
            "residence_geo_state_short",
            "residence_geo_county",
            "residence_geo_zip",
            "residence_geo_lat",
            "residence_geo_lng",
            "residence_geo_formatted_address",
            "burial_location_lot_raw",
            "burial_location_lot",
            "burial_location_lot_strike",
            "burial_location_lot_comments",
            "burial_location_lot_strike_comments",
            "burial_location_grave_raw",
            "burial_location_grave",
            "burial_location_grave_strike",
            "burial_location_grave_comments",
            "burial_location_grave_strike_comments",
            "burial_origin",
            "from_cemetery",
            "is_removal_from",
            "is_removed_to",
            "age_display",
            "age_years_transcribed",
            "age_years",
            "age_months_transcribed",
            "age_months",
            "age_days_transcribed",
            "age_days",
            "age_hours_transcribed",
            "age_hours",
            "marital_status",
            "cause_of_death",
            "undertaker_display",
            "remarks_display",
            "has_diagram"
        ]
}

es_map = {
    'settings':
        {
            'index.mapping.ignore_malformed': True
        },
    'mappings':
        {
            'properties':
                {}
        }
}

es_keyword = {
    "keyword":
        {
            "type": "keyword",
            "ignore_above": 256
        }
}

i = Interment()
for field in i.es_fields:
    field_name = field['name']
    field_type = field['type']
    es_map['mappings']['properties'][field_name] = {"type": field_type}
    if field['keywords']:
        es_map['mappings']['properties'][field_name]['fields'] = es_keyword

# for field in es_fields['fields']:
#     i = Interment()
#     field_name = getattr(i, field + '_es_name')
#     field_type = getattr(i, field + '_es_type')
#
#     es_map['mappings']['properties'][field_name] = {"type": field_type}
#     if getattr(i, field + '_es_keyword'):
#         es_map['mappings']['properties'][field_name]['fields'] = es_keyword


print(json.dumps(es_map, indent=2, sort_keys=False))
