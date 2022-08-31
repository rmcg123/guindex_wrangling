import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from duplicate_check import pubs_counties, distances


def which_pubs(
    dists, data1, data2, county, which_pubs_dict, threshold_1, threshold_2
):
    """Creates a list of tuples containing pubs index and name from each
     dataset that are separated by more than a chosen threshold distance."""

    lst = []
    dists = np.array(dists)
    for i in range(dists.shape[0]):

        if min(dists[i]) > threshold_1:
            lst.append((i, data1["name"][i], min(dists[i]), 1))
        elif min(dists[i]) > threshold_2:
            if (
                fuzz.partial_ratio(
                    data1["name"][i], data2["name"][np.argmin(dists[i])]
                )
                < 75
            ):
                lst.append((i, data1["name"][i], min(dists[i]), 2))
            else:
                continue
        elif min(dists[i]) > 0.02:
            tmp = pd.Series(dists[i])
            tmp = tmp[tmp.gt(0.02) & tmp.le(threshold_2)]
            tmp_2 = []
            for pub in tmp.index:

                print(
                    data1["name"][i],
                    data2["name"][pub],
                    "ratio is ",
                    fuzz.partial_ratio(data1["name"][i], data2["name"][pub]),
                )
                tmp_2.append(
                    fuzz.partial_ratio(data1["name"][i], data2["name"][pub])
                )
            if (pd.Series(tmp_2) < 55).all():
                lst.append((i, data1["name"][i], min(dists[i]), 3))
            else:
                continue
        else:
            continue

    which_pubs_dict[county] = lst

    return which_pubs_dict


def main():

    guindex_pubs = pd.read_csv(
        "guindex_pubs_no_dupes.csv", index_col="Unnamed: 0"
    )
    osm_pubs = pd.read_csv("osm_pubs_no_dupes.csv", index_col="Unnamed: 0")

    osm_pubs["closed"] = np.where(
        (
            osm_pubs["name"].str.endswith("(closed)")
            | osm_pubs["name"].str.endswith("(Closed)")
        ),
        True,
        False,
    )

    osm_pubs = osm_pubs.loc[~osm_pubs["name"].str.contains("Vacant"), :]

    # Clearly incorrect OSM entries and ones that espaced duplicate check
    osm_pubs_to_drop = [
        "I Love Vegetables",
        "I Am In No Way Allergic To Nuts",
        "Me Gaff Hehe x",
        "Open Gate Taproom",
    ]

    osm_pubs = osm_pubs.loc[~osm_pubs["name"].isin(osm_pubs_to_drop), :]

    counties = guindex_pubs["county"].dropna().unique()

    guindex_counties = {}
    osm_counties = {}
    for county in counties:
        _ = pubs_counties(guindex_pubs, county, guindex_counties)
        _ = pubs_counties(osm_pubs, county, osm_counties)

    dists = {}
    for county in counties:
        distances(
            osm_counties[county],
            guindex_counties[county],
            county,
            dists,
            cross=True,
        )

    osm_which = {}
    for county in counties:
        which_pubs(
            dists[county],
            osm_counties[county],
            guindex_counties[county],
            county,
            osm_which,
            0.1,
            0.05,
        )

    osm_lst = []
    for county in counties:
        osm_lst.append(len(osm_which[county]))

    print(
        "------------\n There are ",
        sum(osm_lst),
        " OSM pubs that are not " "in Guindex.\n" "------------",
    )

    transposed_dists = {k: v.T for k, v in dists.items()}

    guindex_which = {}
    for county in counties:
        which_pubs(
            transposed_dists[county],
            guindex_counties[county],
            osm_counties[county],
            county,
            guindex_which,
            0.1,
            0.05,
        )

    guindex_lst = []
    for county in counties:
        guindex_lst.append(len(guindex_which[county]))

    print(
        "------------\n There are ",
        sum(guindex_lst),
        " Guindex pubs not " "in OSM. \n ------------",
    )

    idx_dict = {k: [x[0] for x in osm_which[k]] for k in counties}

    new_county_pubs = {
        k: osm_counties[k].iloc[idx_dict[k], :] for k in counties
    }

    new_pubs = pd.concat(
        [v for v in new_county_pubs.values()], ignore_index=True
    ).reset_index(drop=True)

    new_pubs[["name", "lat", "lon", "county", "closed"]].to_csv(
        "new_pubs.csv", index=False
    )

    return osm_which, guindex_which, dists


if __name__ == "__main__":
    main()
