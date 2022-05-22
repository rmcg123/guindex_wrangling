import json
import requests
import pandas as pd


def osm_query(element, amenity):

    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query_pub = f"""
    [out:json];
    area["ISO3166-1"="IE"]
    [admin_level=2]
    [boundary=administrative];
    ({element}["amenity"={amenity}](area);
    );
    out center;
    """

    response_pub = requests.get(overpass_url, params={"data": overpass_query_pub})

    data_pub = response_pub.json()

    pubs = pd.json_normalize(data_pub["elements"])

    pubs.to_csv(f"{amenity}_{element}.csv")

