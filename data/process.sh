# python3 process_spreadsheet.py -input 'excel/input/Volume 16.xlsx' -vol '16' -sheet 'new'
# python3 process_spreadsheet.py -input 'excel/input/Volume 17.xlsx' -vol '17' -sheet 'Sheet2'
# python3 process_spreadsheet.py -input 'excel/input/Volume 18.xlsx' -vol '18' -sheet 'Volume 18'
# python3 process_spreadsheet.py -input 'excel/input/Volume 19.xlsx' -vol '19' -sheet 'Volume 19'
# python3 process_spreadsheet.py -input 'excel/input/Volume 20.xlsx' -vol '20' -sheet 'Volume 20'
# python3 process_spreadsheet.py -input 'excel/input/Volume 21 - modified.xlsx' -vol '21' -sheet 'VOLUME 21'
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_21 Final Data.xlsx' -vol '21' -sheet 'VOLUME 21' -row_start 3
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_22 Final Data modified.xlsx' -vol '22' -sheet 'VOLUME 22' -row_start 4
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_27 Final Data.xlsx' -vol 27 -sheet 'Volume 27' -row_start 3 -marital_status_cols 2
# python3 process_spreadsheet.py -input 'excel/input/Volume 28 - modified.xlsx' -vol '28' -sheet 'Volume 28' -row_start 3
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_26 Final Data.xlsx' -vol '26' -sheet 'Sheet3' -row_start 3
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_29 Final Data.xlsx' -vol '29' -sheet 'VOLUME 29' -row_start 3 -marital_status_cols 1
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_20 Final Data.xlsx' -vol 20 -sheet 'Volume 20' -row_start 4 -marital_status_cols 2
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_21 Final Data_WithHalfPageEndVol20.xlsx' -vol 21 -sheet 'VOLUME 21' -row_start 3 -marital_status_cols 2
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_30 Final Data.xlsx' -vol 30 -sheet 'VOLUME 30' -row_start 3 -marital_status_cols 1
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_31 Final Data_WithHalfPageEndVol30.xlsx' -vol 31 -sheet 'Volume 31' -row_start 4 -marital_status_cols 1
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_32 Final Data.xlsx' -vol 32 -sheet 'Volume 32' -row_start 6 -marital_status_cols 1
# python3 process_spreadsheet.py -input 'excel/input/VOLUME_33 Final Data.xlsx' -vol 33 -sheet 'Volume 33' -row_start 5 -marital_status_cols 1

#python3 process_spreadsheet.py -input 'excel/input/VOLUME_34 Final Data.xlsx' -vol 34 -sheet 'Volume34' -row_start 9 -marital_status_cols 1 -lookup_years N -year_prefix '18'
#python3 process_spreadsheet.py -input 'excel/input/VOLUME_38 Final Data.xlsx' -vol 38 -sheet 'Volume38' -row_start 12 -marital_status_cols 1 -lookup_years N -year_prefix '18'
#python3 process_spreadsheet.py -input 'excel/input/VOLUME_39 Final Data.xlsx' -vol 39 -sheet 'VOLUME 39' -row_start 5 -marital_status_cols 1 -lookup_years N -year_prefix '18'
#python3 process_spreadsheet.py -input 'excel/input/VOLUME_40 Final Data.xlsx' -vol 40 -sheet 'Volume 40' -row_start 12 -marital_status_cols 1 -lookup_years N -year_prefix '18'
#python3 process_spreadsheet.py -input 'excel/input/VOLUME_41 Final Data.xlsx' -vol 41 -sheet 'VOLUME 41' -row_start 5 -marital_status_cols 1 -lookup_years N -year_prefix '18'


# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_24 Final Data.xlsx' -vol 24 -sheet 'Volume 24' -row_start 3 -marital_status_cols 2 -lookup_years N -year_prefix '18'
# FAILURE python3 process_spreadsheet.py -input 'excel/input/VOLUME_25 Final Data.xlsx' -vol 25 -sheet 'Volume 25' -row_start 59 -marital_status_cols 2 -lookup_years N -year_prefix '18'
# FIXED python3 process_spreadsheet.py -input 'excel/input/VOLUME_25 Final Data_withHalfPageEndVol24.xlsx' -vol 25 -sheet 'Volume 25' -row_start 3 -marital_status_cols 2 -lookup_years N -year_prefix '18'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_35 Final Data.xlsx' -vol 35 -sheet 'Volume35' -row_start 5 -marital_status_cols 1 -lookup_years N -year_prefix '18'
# FIXED python3 process_spreadsheet.py -input 'excel/input/VOLUME_36 Final Data.xlsx' -vol 36 -sheet 'Volume 36' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '18'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_37 Final Data.xlsx' -vol 37 -sheet 'Volume 37' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '18'
# VOL 42 spans 1899 - 1900
# FIXED python3 process_spreadsheet.py -input 'excel/input/VOLUME_42 Final Data.xlsx' -vol 42 -sheet 'Volume 42' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '18'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_43 Final Data.xlsx' -vol 43 -sheet 'Volume 43' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_46 Final Data.xlsx' -vol 46 -sheet 'Volume46' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_47 Final Data.xlsx' -vol 47 -sheet 'VOLUME47' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# FIXED python3 process_spreadsheet.py -input 'excel/input/VOLUME_48 Final Data.xlsx' -vol 48 -sheet 'Volume48' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_49 Final Data.xlsx' -vol 49 -sheet 'Sheet1' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_50 Final Data.xlsx' -vol 50 -sheet 'Volume50' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_51 Final Data.xlsx' -vol 51 -sheet 'Volume 51' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_52 Final Data.xlsx' -vol 52 -sheet 'Volume52' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_53 Final Data.xlsx' -vol 53 -sheet 'Volume53' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_54 Final Data.xlsx' -vol 54 -sheet 'Volume 54' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# FIXED python3 process_spreadsheet.py -input 'excel/input/VOLUME_55 Final Data.xlsx' -vol 55 -sheet 'Volume 55' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_56 Final Data.xlsx' -vol 56 -sheet 'Volume 56' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# FIXED python3 process_spreadsheet.py -input 'excel/input/VOLUME_57 Final Data.xlsx' -vol 57 -sheet 'Volume 57' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_58 Final Data.xlsx' -vol 58 -sheet 'Volume 58' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# SUCCESS python3 process_spreadsheet.py -input 'excel/input/VOLUME_59 Final Data.xlsx' -vol 59 -sheet 'Sheet1' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'
# FAILURE - several columns have wrong values - python3 process_spreadsheet.py -input 'excel/input/VOLUME_60 Final Data.xlsx' -vol 60 -sheet 'Volume60' -row_start 3 -marital_status_cols 1 -lookup_years N -year_prefix '19'

