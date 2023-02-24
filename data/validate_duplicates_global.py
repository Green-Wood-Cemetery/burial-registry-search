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

interments = {}
records = []

for file in os.listdir(args.folder):
    try:
        print(f"Checking file {file}...")
        logging.info(f"Checking file {file}...")
        raw_data = json.load(open(os.path.join(args.folder, file), "rb"))
        for item in raw_data:
            if item["interment_id"] not in interments:
                interments[item["interment_id"]] = [file]
            else:
                interments[item["interment_id"]].append(file)
    except:
        pass

keys = []
for key in interments.keys():
    if len(interments[key]) > 1:
        for file in interments[key]:
            if str(key) + "#" + file not in keys:
                records.append({"file": file, "interment_id": key})
                keys.append(str(key) + "#" + file)

if len(records) > 0:
    print(f"See the list of duplicates in the files of folder {args.folder}...")
    logging.info(f"See the list of duplicates in the files of folder {args.folder}...")
    with open(f"logs/duplicate_list_{args.folder}.csv", "w", newline="") as fw:
        dw = csv.DictWriter(fw, fieldnames=["file", "interment_id"])
        dw.writeheader()
        dw.writerows(records)
        print(f"List of duplicates saved on logs/duplicate_list_{args.folder}.csv...")
        logging.info(f"List of duplicates saved on logs/duplicate_list_{args.folder}.csv...")

else:
    print(f"No dupes where found in the files of folder {args.folder}...")
    logging.info(f"No dupes where found in the files of folder {args.folder}...")
