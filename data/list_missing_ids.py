import json
import os


try:
    print("[")
    for file in os.listdir("json"):
        data = json.load(open(os.path.join("json", file), "rb"))
        for item in data:
            if item["interment_id"] == "":
                item["file"] = file
                print(json.dumps(item), ",")
    print("]")
except:
    print(f"File {file} not found.")
