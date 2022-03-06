python3 greenwood.py -key key_goes_here -input 'excel/greenwood 08022020 volume 60.xlsx' -sheet 'Volume60' > test.json | jq > json/greenwood-volume-60.json
python3 python3 greenwood.py -key key_goes_here -input 'excel/greenwood 08022020 volume 60.xlsx' -sheet 'Volume 30' > test.json | jq > json/greenwood-volume-30.json

rm test.json
