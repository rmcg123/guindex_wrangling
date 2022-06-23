import pandas as pd
import numpy as np
from math import radians

guindex_pubs = pd.read_csv("guindex_pubs.csv", index_col="Unnamed: 0")
osm_pubs = pd.read_csv("all_osm_pubs.csv", index_col="Unnamed: 0")

counties = osm_pubs["county"].dropna().unique()


def pubs_counties(data, county, pubs_dict):
    """Creates a dictionary entry with key "county" and value pubs from that
    county."""

    pubs_dict[county] = data.loc[data["county"].eq(county), :].reset_index(drop=False)

    return pubs_dict


def distances(data1, data2, county, dist_dict):
    """Creates an array with distances between pubs in a chosen county."""

    dists = np.zeros(len(data1) * len(data2)).reshape(len(data1), len(data2))

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
                            + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
                        )
                    )
                )

    dist_dict[county] = dists

    return dist_dict


def which_pubs(dists, data1, data2, county, which_pubs_dict, threshold=0.01,):
    """Creates a list of tuples containing pubs index and name from each dataset that are separated by less than a chosen threshold distance."""

    lst = []
    dists = np.array(dists)
    for i in range(dists.shape[0]):
        for j in range(dists.shape[1]):
            if i <= j:
                continue
            if dists[i, j] < threshold:
                lst.append((i, data1["name"][i], j, data2["name"][j]))
            else:
                continue

    which_pubs_dict[county] = lst

    return which_pubs_dict


def get_dupes(dupes):
    """Creates a list of duplicates."""
    lst = []
    if len(dupes) == 0:
        pass
    else:
        for i in range(len(dupes)):
            lst.append(dupes[i][0])

    return lst


def remaining_pubs(pubs, drop, county):
    """Drops the duplicated pubs leaving the remaining ones."""
    rem = set(pubs[county].index.to_list()) - set(drop[county])

    pub_rem = pubs[county][pubs[county].index.isin(rem)]

    return pub_rem


def full_check(data):

    county_pubs = {}
    for county in counties:
        _ = pubs_counties(data, county, county_pubs)


    county_dists = {}
    for county in counties:
        _ = distances(county_pubs[county], county_pubs[county], county, county_dists)


    which_dict = {}
    for county in counties:
        _ = which_pubs(county_dists[county], county_pubs[county], county_pubs[county], county, which_dict)


full_check(osm_pubs)