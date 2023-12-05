import folium
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster

import guindex


def create_map():
    """Function to create the map page."""

    pubs = guindex.pubs()

    pubs["price"] = np.where(
        pubs["closed"] | (~pubs["serving_guinness"]), np.nan,
        pubs["last_price"]
    )

    # Map centre.
    av_lat = pubs["latitude"].median()
    av_lon = pubs["longitude"].median()

    # Create map.
    tst = folium.Map(location=[av_lat, av_lon], control_scale=True)

    # Set map zoom level to fit pubs.
    tst.fit_bounds(
        [
            pubs[["latitude", "longitude"]].min().to_list(),
            pubs[["latitude", "longitude"]].max().to_list()
        ]
    )

    # Create cluster to add markers to so as to have zoom based clustering
    # of markers.
    cluster = MarkerCluster(
        locations=[[av_lat, av_lon]],
        name=None,
        icons=None,
        popups=None,
        options={
            "disableClusteringAtZoom": 14
        }
    ).add_to(tst)

    # Go through pubs and create appropriate markers.
    for _, pub in pubs.iterrows():

        if pub["closed"]:
            closed_icon = folium.Icon(
                prefix="fa", icon="window-close", color="black",
                icon_color="white"
            )
            marker = folium.Marker(
                [pub["latitude"], pub["longitude"]],
                popup=pub["name"] + " - closed",
                icon=closed_icon
            )

        elif not pub["serving_guinness"]:
            not_serving_icon = folium.Icon(
                prefix="fa", icon="exclamation", color="red"
            )
            marker = folium.Marker(
                [pub["latitude"], pub["longitude"]],
                popup=pub["name"] + " - not serving Guinness",
                icon=not_serving_icon
            )

        elif pd.notnull(pub["price"]):
            price_icon = folium.Icon(
                prefix="fa",  icon="beer", color="green"
            )
            marker = folium.Marker(
                [pub["latitude"], pub["longitude"]],
                popup=f"{pub['name']} - €{pub['price']}, Submitted: "
                      f"{pub['last_submission_time'].strftime('%Y-%m-%d')}",
                icon=price_icon
            )

        else:
            no_price_icon = folium.Icon(
                prefix="fa", icon="question", color="lightgray"
            )
            marker = folium.Marker(
                [pub["latitude"], pub["longitude"]],
                popup=pub['name'] + " - No data submitted",
                icon=no_price_icon,
            )

        # Add marker to cluster
        marker.add_to(cluster)

    # Save map.
    tst.save("new_guindex_map.html")


if __name__ == "__main__":
    create_map()
