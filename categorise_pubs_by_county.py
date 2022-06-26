import pandas as pd
from shapely import wkt
from shapely.geometry import Point

no_counties = pd.read_csv("osm_pubs_with_no_counties.csv")
shapes = pd.read_csv("counties.csv")

shapes["geoms"] = shapes["WKT"].apply(wkt.loads)

no_counties["points"] = [Point(no_counties["lon"].iloc[i], no_counties["lat"].iloc[i]) for i in range(len(no_counties))]


def find_county():

    for i in range(len(shapes)):
        for j in range(len(no_counties)):
            if shapes["geoms"].iloc[i].contains(no_counties["points"].iloc[j]):
                no_counties["county"].iloc[j] = shapes["NAME_TAG"].iloc[i]


find_county()
no_counties.drop(columns="points", inplace=True)
no_counties.to_csv("osm_pubs_with_added_counties.csv")
