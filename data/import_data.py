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
parsed_vol = (args.file.replace(".json", "")).split("-")[2]
logging.basicConfig(
    filename="logs/import-data-" + str(args.index) + "-" + parsed_vol + "-" + timestr + ".csv",
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
        # This code is setting up a loop to send data in chunks of
        # 100 items to an API. The loop will continue until all of
        # the data in the file_data array has been sent. The payload
        # variable is created by encoding each item in the
        # file_data array and adding it to the payload string.
        # The response from the API is then checked for errors,
        # and if there are any, the loop will be broken.
        # The ind variable is incremented by size each time
        # the loop runs, so that it will move on to the
        # next chunk of 100 items in file_data.
        # nr_records is also incremented by size each time,
        # so that it can keep track of how many records
        # have been sent.
        ind = 0
        size = 100
        max = len(file_data)
        nr_records = 0
        while ind < max:
            payload = ""
            for item in file_data[ind : ind + size]:
                type = {"index": {"_id": item["interment_id"]}}
                payload += demjson3.encode(type) + "\n" + demjson3.encode(item) + "\n"

            response = requests.post(url, data=payload, headers=headers)
            nr_records += size

            parsed = json.loads(response.text)

            if parsed["errors"]:
                print(
                    f"The import process of file {args.file} into index {args.index} was not successful. See logs for errors."
                )
                logging.error(f"The import process of file {args.file} into index {args.index} was not successful.")
                logging.error(f"Dumping errors for import process ...")
                errors = []
                for item in parsed["items"]:
                    if item["index"]["status"] != 201:
                        logging.error(json.dumps(item, indent=4, sort_keys=True))
                        errors.append(item)

                with open("logs/import_errors.json", "a") as fw:
                    json.dump(errors, fw)
            else:
                find_updates = False
                updates = []
                for item in parsed["items"]:
                    if item["index"]["status"] == 200:
                        if not find_updates:
                            logging.error(
                                "The import have generated some updates, which indicates duplicated interment_ids on the file."
                            )
                        logging.error(json.dumps(item, indent=4, sort_keys=True))
                        updates.append(item)
                        find_updates = True

                if find_updates:
                    print(
                        f"The import process of file {args.file} into index {args.index} was successful, but some updates have happened. See the logs for more information."
                    )
                    with open(f"logs/dump_updates_{timestr}.json", "w") as fw:
                        json.dump(updates, fw)
                    print(f"We have saved all the updated records on the file logs/dump_updates_{timestr}.json.")

                else:
                    print(
                        f"Import of {nr_records} records from file {args.file} into index {args.index} was successful."
                    )

            ind += size
    except:
        logging.error(f"Connectivity error when inserting data on index {args.index}...")
else:
    logging.info("The process has finished because the file is empty.")
    print("File is empty or does not exist. See logs for error...")
