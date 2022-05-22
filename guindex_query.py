import requests
import json
import pandas as pd
import numpy as np

pub_fetch = requests.get("https://www.guindex.ie/api/pubs/")

lst = []

for i in range(39):
    pub_fetch = requests.get("https://www.guindex.ie/api/pubs/", params={"page": {i+1}})
    pubs = pub_fetch.json()
    lst.append(pubs["results"])

pubs_df = pd.json_normalize(np.array(lst).flatten())

last_ones = requests.get("https://www.guindex.ie/api/pubs/", params={"page": 40})

last_pubs = last_ones.json()["results"]

last_pubs = pd.json_normalize(last_pubs)

all_pubs = pubs_df.append(last_pubs).reset_index(drop=True)

all_pubs = all_pubs.rename({"latitude": "lat", "longitude": "lon"}, axis=1)

all_pubs[["name", "lat",  "lon", "county"]].to_csv("guindex_pubs.csv")
