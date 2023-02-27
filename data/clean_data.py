import requests
import demjson3
import json
import argparse
import logging
import time

# Creates an argument parser object with two arguments:
# -index and -vol.
# Then configures the logging module to create a log file with
# the index name and volume number.

parser = argparse.ArgumentParser(description="Compares Elasticsearch JSON with Elasticsearch INDEX")
parser.add_argument("-index", type=str, help="ES Index")
parser.add_argument("-vol", type=int, help="Volume to be cleaned")
args = parser.parse_args()

timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(
    filename="logs/clean-data-" + str(args.index) + "-" + str(args.vol) + "-" + timestr + ".csv",
    filemode="a",
    format="%(message)s",
    level=logging.DEBUG,
)

# Sets authorization and appname variables as well as
# a method variable. It also creates a url variable using
# the f-string method.
# It then sets headers for the request and creates an
# empty list for file_data and sets total_records to 0.

authorization = "Basic d2NvcnRlczpHVzQ3OGd3"
appname = args.index
method = "_delete_by_query"

url = f"https://green-wood-hrrhhxs-arc.searchbase.io/{appname}/{method}?wait_for_completion=true&scroll_size=5000"

headers = {"Authorization": authorization, "Content-Type": "application/json"}

file_data = []
total_records = 0

# The code prints out starting information about the
# index and volume before trying to make a request
# using the payload variable.
# If there are records found in the response,
# it logs information about them as well as printing it out.
# If no records are found, it prints out an error message
# and logs it.

print("Starting process to Clean the index...")
print(f"Index: {args.index}")
print(f"Volume: {args.vol}")

try:
    payload = demjson3.encode({"query": {"term": {"registry_volume": args.vol}}})
    response = requests.post(url, data=payload, headers=headers)
    parsed = json.loads(response.text)

    if parsed["total"] > 0:
        logging.info(f"Total records for volume: {parsed['total']}")
        logging.info(f"Total records deleted: {parsed['deleted']}")
        if parsed["deleted"] <= 0:
            print("Problems with record deletion.")
            logging.error(f"From the total {parsed['total']} records found, only {parsed['deleted']} were deleted.")

        print(f"Total records for volume: {parsed['total']}")
        print(f"Total records deleted: {parsed['deleted']}")

    else:
        print("The volume was not found inside the index.")
        logging.error("The volume was not found inside the index.")
except:
    pass
