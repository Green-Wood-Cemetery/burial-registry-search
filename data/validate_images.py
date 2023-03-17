import pandas as pd
import duckdb as duckdb
import requests as req
import csv
import logging
import traceback
import time

# logging config
timestr = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(filename="logs/validate-images-" + timestr + ".csv", filemode="a", format="%(message)s")


print("Querying the database...")
conn = duckdb.connect("sqlite/db.duckdb")
images = conn.execute(
    """select registry_image, 
              registry_page, 
              registry_volume, 
              interment_id 
        from interments
        where interment_id is not null
        order by registry_volume, registry_image"""
).df()

print("Starting the validation...")
records = []
visited = []
for index, row in images.iterrows():
    try:
        volume = int(row["registry_volume"])
        image = row["registry_image"]
        url = f"https://www.green-wood.com/scans/Volume {volume:02d}/{image}.jpg"

        if url not in visited:
            print(f"{index} - Verifying {url}:", end=" ")

            resp = req.get(url)

            if resp.status_code != 200:
                print("NOT OK")
                records.append(
                    {
                        "interment_id": row["interment_id"],
                        "registry_volume": row["registry_volume"],
                        "registry_page": row["registry_page"],
                        "registry_image": row["registry_image"],
                        "url": url,
                    }
                )
            else:
                print("OK")

            visited.append(url)
    except:
        print(f"Error validating {row['registry_image']}")
        logging.error(traceback.format_exc())

with open("logs/wrong_images.csv", "w") as fw:
    dw = csv.DictWriter(fw, fieldnames=["interment_id", "registry_volume", "registry_page", "registry_image", "url"])
    dw.writeheader()
    dw.writerows(records)

conn.close()
print("Validation ended.")
