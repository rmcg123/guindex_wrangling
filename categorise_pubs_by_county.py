import pandas as pd
from shapely import wkt
from shapely.geometry import Point


def find_county(geometry_df, pubs_df):
    """Sort pubs into their respective counties."""

    # Loop over county shapes and pubs to check if pub is in each county.
    for i in range(len(geometry_df)):
        for j in range(len(pubs_df)):
            if (
                geometry_df["geoms"]
                .iloc[i]
                .contains(pubs_df["points"].iloc[j])
            ):
                pubs_df["county"].iloc[j] = geometry_df["NAME_TAG"].iloc[i]

    pubs_df.drop(columns="points", inplace=True)

    return pubs_df


def categorise_pubs():
    """Main function."""

    # Read in pubs that are missing counties.
    no_counties = pd.read_csv(
        "osm_pubs_with_no_counties.csv", index_col="Unnamed: 0"
    )

    # Read in counties shapefile.
    shapes = pd.read_csv("counties.csv")

    # Convert well-known-text version of geometry into shapely geometries.
    shapes["geoms"] = shapes["WKT"].apply(wkt.loads)

    # Create shapely points from the longitude and latitude of the pubs.
    no_counties["points"] = [
        Point(no_counties["lon"].iloc[i], no_counties["lat"].iloc[i])
        for i in range(len(no_counties))
    ]

    # Check which shape each of the points is in to get their county.
    no_counties = find_county(shapes, no_counties)

    # Save pubs with added counties for inspection.
    no_counties.to_csv("osm_pubs_with_added_counties.csv")

    return no_counties


if __name__ == "__main__":
    categorise_pubs()
