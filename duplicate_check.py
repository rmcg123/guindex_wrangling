import pandas as pd
import numpy as np
from math import radians

guindex_pubs = pd.read_csv("guindex_pubs.csv", index_col="Unnamed: 0")
osm_pubs = pd.read_csv("all_osm_pubs.csv", index_col="Unnamed: 0")

counties = osm_pubs["county"].unique()


def pubs_counties(data, county, pubs_dict):
    """Creates a dictionary entry with key "county" and value pubs from that
    county."""

    pubs_dict[county] = data.loc[data["county"].eq(county), :]

    return pubs_dict


def distances(data1, data2):
    """Creates an array with distances between pubs in a chosen county."""

    dists = np.zeroes(len(data1) * len(data2)).reshape(len(data1), len(data2))

    for i in range(len(data1)):
        for j in range(len(data2)):
            if i <= j:
                dists[i, j] = np.nan
            else:
                lat1, lon1, lat2, lon2 = map(
                    radians,
                    [
                        data1["lat"][i],
                        data1["lon"][i],
                        data2["lat"][j],
                        data2["lon"][j],
                    ],
                )
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                dists[i, j] = (
                    2
                    * 6371
                    * np.arcsin(
                        np.sqrt(
                            np.sin(dlat / 2) ** 2
                            + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)
                        )
                    )
                )

    return dists
