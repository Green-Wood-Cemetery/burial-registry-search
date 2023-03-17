import pandas as pd
import os
import duckdb

print("Connecting to db...")
conn = duckdb.connect("sqlite/db.duckdb")
conn.sql("SET GLOBAL pandas_analyze_sample=600000")

print("Loading into dataframe...")
records = []
for file in os.listdir("json"):
    records.append(pd.read_json(os.path.join("json", file)))

df = pd.concat(records)

print("Dropping table...")
conn.sql("drop table if exists interments")

print("Creating table...")
conn.sql("create table interments as select * from df")

print("Closing connection...")
conn.close()
