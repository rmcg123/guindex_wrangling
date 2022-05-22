import pandas as pd
from osm_query import get_all_osm

# Gets all osm data of interest.
get_all_osm(["node", "way"], ["pub", "bar", "nightclub"])

# Imports all retrieved nodes of interest.
pubs_n = pd.read_csv("pub_node.csv")
bars_n = pd.read_csv("bar_node.csv")
clubs_n = pd.read_csv("nightclub_node.csv")

# Combines nodes into single dataframe.
nodes = pubs_n.merge(bars_n, how="outer").merge(clubs_n, how="outer")

# Drop all nodes that do not have name, lat and lon and select
# relevant columns.
nodes = nodes.loc[
    nodes["tags.name"].notnull() &
    nodes["lat"].notnull() &
    nodes["lon"].notnull(),
    ["tags.name", "lat", "lon", "tags.addr:county"]
]

# Import all retrieved ways of interest.
pubs_w = pd.read_csv("pub_way.csv")
bars_w = pd.read_csv("bar_way.csv")
clubs_w = pd.read_csv("nightclub_way.csv")

# Select relevant columns.
pubs_w = pubs_w[["tags.name", "center.lat", "center.lon", "tags.addr:county"]]
bars_w = bars_w[["tags.name", "center.lat", "center.lon", "tags.addr:county"]]
clubs_w = clubs_w[["tags.name", "center.lat", "center.lon"]]

# Combine ways into single Dataframe.
ways = pubs_w.merge(bars_w, how="outer").merge(clubs_w, how="outer")

# Drop all ways that do not have a name, lat and lon.
ways = ways.loc[
    ways["tags.name"].notnull() &
    ways["center.lat"].notnull() &
    ways["center.lon"].notnull(),
    :
]

# Rename ways lat and lon columns to match those of nodes.
ways = ways.rename(
    columns={
        "center.lat": "lat",
        "center.lon": "lon",
    }
)

# Combine ways and nodes.
all_osm = ways.merge(nodes, how="outer")

# Rename names and county columns.
all_osm = all_osm.rename(
    columns={
        "tags.name": "name",
        "tags.addr:county": "county",
    }
)

# Output all osm data.
all_osm.to_csv("all_osm_pubs.csv")
