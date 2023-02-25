import requests
import demjson3
import json
import argparse
import logging
import time

parser = argparse.ArgumentParser(description="Compares Elasticsearch JSON with Elasticsearch INDEX")
parser.add_argument("-file", type=str, help="ES JSON file")
parser.add_argument("-index", type=str, help="ES Index")
parser.add_argument("-vol", type=int, help="ES Volume", default=0)
args = parser.parse_args()

# logging config
timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(
    filename="logs/compare-index-" + str(args.index) + "-" + timestr + ".csv",
    filemode="a",
    format="%(message)s",
    level=logging.DEBUG,
)

authorization = "Basic d2NvcnRlczpHVzQ3OGd3"
appname = args.index
method = "_search"
url = f"https://green-wood-hrrhhxs-arc.searchbase.io/{appname}/{method}"

headers = {"Authorization": authorization, "Content-Type": "application/json"}
payload_obj = {"query": {"match_all": {}}}
if args.vol != 0:
    payload_obj = {"query": {"term": {"registry_volume": args.vol}}}

start = 0
size = 1000
file_data = []
total_records = 0

print("Starting process to compare file and index...")
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
        logging.info(f"Loading ES Index {args.index} data...")
        response = requests.post(url, data=demjson3.encode(payload_obj), headers=headers)
        raw_data = json.loads(response.text)
        total_records = raw_data["hits"]["total"]["value"]
    except:
        logging.error(f"Error retrivieng data for index {args.index}...")
        exit()

    if total_records > 0:
        records = []

        while start < total_records:
            payload_obj["from"] = start
            payload_obj["size"] = size
            payload = demjson3.encode(payload_obj)
            response = requests.post(url, data=payload, headers=headers)
            raw_data = json.loads(response.text)
            for item in raw_data["hits"]["hits"]:
                records.append(item["_source"])
            start += size

        logging.info(f"Loaded {total_records} records from index {args.index}...")

        with open("logs/validate_size.csv", "a", newline="") as fw:
            fw.write(f"'{timestr}',{args.file},{len(file_data)},{args.index},{total_records}\n")

        if len(file_data) == len(records):
            error = False
            errors = []
            print("Comparing file with index data...")
            logging.info("Comparing file with index data...")

            file_data = sorted(file_data, key=lambda x: x["interment_id"])
            records = sorted(records, key=lambda x: x["interment_id"])

            for indx in range(0, len(records)):
                for col_name in records[indx].keys():
                    if file_data[indx][col_name] != records[indx][col_name]:
                        errors.append(
                            f"'{timestr}',{args.file},'{file_data[indx][col_name]}',{args.index},'{records[indx][col_name]}\n'"
                        )
                        error = True
            if error:
                logging.error("File and Index were not identical!!!")
                logging.error("See the validate_values file for detail on issues.")
                print("File and Index were not identical. See validate_values for errors...")
                with open("logs/validate_values.csv", "a", newline="") as fw:
                    fw.writelines(errors)
            else:
                logging.info(f"File and Index were identical!!!")
                print(f"File and Index were identical!!!")
        else:
            logging.error(f"The index {args.index} and the file {args.file} have different number of rows.")
            logging.error("See the validate_size file for detail in the issue.")
            print("File and Index were not identical. See validate_size for error...")
    else:
        logging.info("The process has finished because the index does not have records to be compared.")
        print("File and/or Index were not loaded for comparison. See logs for error...")
