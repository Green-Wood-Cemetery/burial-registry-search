import requests
import demjson3
import json
import argparse
import logging
import time

parser = argparse.ArgumentParser(description="Compares Elasticsearch JSON with Elasticsearch INDEX")
parser.add_argument("-file", type=str, help="ES JSON file")
parser.add_argument("-index", type=str, help="ES Index")
args = parser.parse_args()

# logging config
timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(
    filename="logs/import-data-" + str(args.index) + "-" + timestr + ".csv",
    filemode="a",
    format="%(message)s",
    level=logging.DEBUG,
)

authorization = "Basic d2NvcnRlczpHVzQ3OGd3"
appname = args.index
method = "_bulk"

url = f"https://green-wood-hrrhhxs-arc.searchbase.io/{appname}/{method}"

headers = {"Authorization": authorization, "Content-Type": "application/json"}

file_data = []
total_records = 0

print("Starting process to Import file into index...")
print(f"File: {args.file}")
print(f"Index: {args.index}")

print("Loading data...")
try:
    logging.info(f"Loading file {args.file} data...")
    with open(args.file, "r", encoding="utf-8") as file_to_compare:
        file_data = json.load(file_to_compare)
    logging.info(f"File {args.file} data loaded...")
except:
    logging.error(f"Erro loading file {args.file}.")

if len(file_data) > 0:
    try:
        payload = ""
        for item in file_data:
            type = {"index": {"_id": item["interment_id"]}}
            payload += demjson3.encode(type) + "\n" + demjson3.encode(item) + "\n"

        logging.info(f"Loading ES Index {args.index} data...")
        response = requests.post(url, data=payload, headers=headers)

        parsed = json.loads(response.text)
        if parsed["errors"]:
            print(
                f"The import process of file {args.file} into index {args.index} was not successful. See logs for errors."
            )
            logging.error(f"The import process of file {args.file} into index {args.index} was not successful.")
            logging.error(f"Dumping errors for import process ...")
            for item in parsed["items"]:
                if item["index"]["status"] == 400:
                    logging.error(json.dumps(item, indent=4, sort_keys=True))
        else:
            print(f"The import process of file {args.file} into index {args.index} was successful.")
    except:
        logging.error(f"Connectivity error when inserting data on index {args.index}...")
else:
    logging.info("The process has finished because the file is empty.")
    print("File is empty or does not exist. See logs for error...")
