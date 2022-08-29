import pandas as pd
import numpy as np
from math import radians
from fuzzywuzzy import fuzz
from categorise_pubs_by_county import categorise_pubs


def pubs_counties(data, county, pubs_dict):
    """Creates a dictionary entry with key "county" and value pubs from that
    county."""

    pubs_dict[county] = data.loc[data["county"].eq(county), :].reset_index(
        drop=False
    )

    return pubs_dict


def distances(data1, data2, county, dist_dict, cross=False):
    """Creates an array with distances between pubs in a chosen county."""

    dists = np.zeros(len(data1) * len(data2)).reshape(len(data1), len(data2))

    for i in range(len(data1)):
        for j in range(len(data2)):
            if i <= j and not cross:
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
                            + np.cos(lat1)
                            * np.cos(lat2)
                            * np.sin(dlon / 2) ** 2
                        )
                    )
                )

    dist_dict[county] = dists

    return dist_dict


def which_pubs(dists, data1, data2, county, which_pubs_dict, threshold=0.05):
    """Creates a list of tuples containing pubs index and name from each
     dataset that are separated by less than a chosen threshold distance."""

    lst = []
    dists = np.array(dists)
    for i in range(dists.shape[0]):
        for j in range(dists.shape[1]):
            if i <= j:
                continue
            if dists[i, j] < threshold:
                if fuzz.ratio(data1["name"][i], data2["name"][j]) > 85:
                    lst.append((i, data1["name"][i], j, data2["name"][j]))
                else:
                    continue
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


def full_check(data, counties):

    # Create a dictionary with counties as keys and DataFrames of pubs as
    # values.
    county_pubs = {}
    for county in counties:
        _ = pubs_counties(data, county, county_pubs)

    # Create another dictionary with counties as keys and np.arrays of
    # distances between pubs as entries.
    county_dists = {}
    for county in counties:
        _ = distances(
            county_pubs[county], county_pubs[county], county, county_dists
        )

    # Create a dictionary with counties as keys and lists of
    # (index_1, name_1, index_2, name_2) tuples of pubs within a certain
    # distance.
    which_dict = {}
    for county in counties:
        _ = which_pubs(
            county_dists[county],
            county_pubs[county],
            county_pubs[county],
            county,
            which_dict,
        )

    # Creates a dictionary with counties as keys and lists of duplicates as
    # values.
    drop_dupes = {}
    for county in counties:
        drop_dupes[county] = get_dupes(which_dict[county])

    # Creates a dictionary with counties as keys and pd.DataFrame of remaining
    # pubs as values.
    rem_pubs = {}
    for county in counties:
        rem_pubs[county] = remaining_pubs(county_pubs, drop_dupes, county)

    return rem_pubs, which_dict


def main():
    """Main function."""

    # Import guindex and osm pubs.
    guindex_pubs = pd.read_csv("guindex_pubs.csv", index_col="Unnamed: 0")
    osm_pubs = pd.read_csv("all_osm_pubs.csv", index_col="Unnamed: 0")

    # Find osm pubs that do not have a county.
    no_counties = osm_pubs.loc[osm_pubs["county"].isna(), :]

    # Save pubs missing counties in a csv.
    no_counties.to_csv("osm_pubs_with_no_counties.csv")

    # Take slice of osm DataFrame where there are counties.
    osm_pubs = osm_pubs.loc[~osm_pubs["county"].isna(), :].reset_index(
        drop=True
    )

    # Add counties for those missing them.
    counties_added = categorise_pubs()

    print(counties_added)

    # Re-combine osm pubs.
    all_osm_pubs = pd.concat([osm_pubs, counties_added], ignore_index=True)

    all_osm_pubs.to_csv("all_osm_pubs_with_counties.csv")

    # Unique counties in osm pubs.
    counties = all_osm_pubs["county"].dropna().unique()

    # For each of the two pubs dataset perform the full duplicate check.
    for data in ["osm", "guindex"]:
        if data == "osm":
            dat = all_osm_pubs
        else:
            dat = guindex_pubs

        rem_pubs, which_dict = full_check(dat, counties)

        # Re-combine all counties DataFrames into a single DataFrame.
        rem_pubs = pd.concat(
            [v for v in rem_pubs.values()], ignore_index=True
        ).reset_index(drop=True)

        # Save non-duplicate pubs to csv.
        rem_pubs.to_csv(f"{data}_pubs_no_dupes.csv")

        # Combine duplicates from all counties into a single DataFrame.
        which_dict = pd.concat(
            [pd.DataFrame(v) for v in which_dict.values()], ignore_index=True
        ).reset_index(drop=True)

        # Output duplicates to a csv for inspection.
        which_dict.to_csv(f"{data}_pubs_dropped_dupes.csv")


if __name__ == "__main__":
    main()
