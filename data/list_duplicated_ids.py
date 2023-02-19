import json
import argparse

parser = argparse.ArgumentParser(description="Compares Elasticsearch JSON with Elasticsearch INDEX")
parser.add_argument("-file", type=str, help="Dump file")
args = parser.parse_args()

try:
    data = json.load(open(args.file, "rb"))

    for item in data:
        try:
            print(item["index"]["_id"])
        except:
            print("The structure  index/_id was not found")
            exit()
except:
    print(f"File {args.file} not found.")
