import os
import json
import argparse
import logging
import time
import csv

parser = argparse.ArgumentParser(description="Compares Elasticsearch JSON with Elasticsearch INDEX")
parser.add_argument("-folder", type=str, help="Folder to scaffold")
args = parser.parse_args()

# logging config
timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(
    filename="logs/validate-duplicates" + "-" + timestr + ".csv",
    filemode="a",
    format="%(message)s",
    level=logging.DEBUG,
)


logging.info(f"Analyzing folder {args.folder}...")
print(f"Analyzing folder {args.folder}...")
records = []
for file in os.listdir(args.folder):
    try:
        print(f"Checking file {file}...")
        logging.info(f"Checking file {file}...")
        list_ids = []
        dupe_ids = []
        raw_data = json.load(open(os.path.join(args.folder, file), "rb"))
        for item in raw_data:
            if item["interment_id"] not in list_ids:
                list_ids.append(item["interment_id"])
            else:
                if item["interment_id"] not in dupe_ids:
                    dupe_ids.append(item["interment_id"])

        if len(dupe_ids) > 0:
            print(f"Adding dupes from {file}...")
            logging.info(f"Adding dupes from file {file}...")
            records.append({"file": file, "duplicates": dupe_ids})
    except:
        pass

if len(records) > 0:
    print(f"See the list of duplicates in the files of folder {args.folder}...")
    logging.info(f"See the list of duplicates in the files of folder {args.folder}...")
    with open("logs/duplicate_list.csv", "w", newline="") as fw:
        dw = csv.DictWriter(fw, fieldnames=["file", "interment_id"])
        dw.writeheader()
        for item in records:
            for interment in item["duplicates"]:
                dw.writerow({"file": item["file"], "interment_id": interment})
        print(f"List of duplicates saved on logs/duplicate_list.csv...")
        logging.info(f"List of duplicates saved on logs/duplicate_list.csv...")

else:
    print(f"No dupes where found in the files of folder {args.folder}...")
    logging.info(f"No dupes where found in the files of folder {args.folder}...")
