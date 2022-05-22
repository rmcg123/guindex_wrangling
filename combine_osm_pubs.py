import pandas as pd
from osm_query import get_all_osm


get_all_osm(["node", "way"], ["pub", "bar", "nightclub"])


pubs_n = pd.read_csv("pub_node.csv")
bars_n = pd.read_csv("bar_node.csv")
clubs_n = pd.read_csv("nightclub_node.csv")


nodes = pubs_n.merge(bars_n, how="outer").merge(clubs_n, how="outer")

nodes = nodes.loc[
    nodes["tags.name"].notnull() &
    nodes["lat"].notnull() &
    nodes["lon"].notnull(),
    ["tags.name", "lat", "lon", "tags.addr:county"]
]

pubs_w = pd.read_csv("pub_way.csv")
bars_w = pd.read_csv("bar_way.csv")
clubs_w = pd.read_csv("nightclub_way.csv")

pubs_w = pubs_w[["tags.name", "center.lat", "center.lon", "tags.addr:county"]]
bars_w = bars_w[["tags.name", "center.lat", "center.lon", "tags.addr:county"]]
clubs_w = clubs_w[["tags.name", "center.lat", "center.lon"]]

ways = pubs_w.merge(bars_w, how="outer").merge(clubs_w, how="outer")

ways = ways.loc[
    ways["tags.name"].notnull() &
    ways["center.lat"].notnull() &
    ways["center.lon"].notnull(),
    :
]

ways = ways.rename(
    columns={
        "center.lat": "lat",
        "center.lon": "lon",
    }
)

all_osm = ways.merge(nodes, how="outer")

all_osm = all_osm.rename(
    columns={
        "tags.name": "name",
        "tags.addr:county": "county",
    }
)

all_osm.to_csv("all_osm_pubs.csv")
