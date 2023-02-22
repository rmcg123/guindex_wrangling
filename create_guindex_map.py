import folium
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster


def create_map():
    """Function to create the map page."""

    pubs = pd.read_csv("guindex_pubs.csv")

    # Fictitious information for closed, serving and price. To be replaced
    # with real columns.
    pubs["closed"] = np.random.choice([True, False], size=len(pubs))
    pubs["serving_guinness"] = np.random.choice([True, False], size=len(pubs))
    pubs["price"] = np.random.choice([5.0, 6.0, np.nan], size=len(pubs))

    pubs["price"] = np.where(
        pubs["closed"] | (~pubs["serving_guinness"]), np.nan, pubs["price"]
    )

    # Map centre.
    av_lat = pubs["lat"].median()
    av_lon = pubs["lon"].median()

    # Create map.
    tst = folium.Map(location=[av_lat, av_lon], control_scale=True)

    # Set map zoom level to fit pubs.
    tst.fit_bounds(
        [
            pubs[["lat", "lon"]].min().to_list(),
            pubs[["lat", "lon"]].max().to_list()
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
                [pub["lat"], pub["lon"]],
                popup=pub["name"] + " - closed",
                icon=closed_icon
            )

        elif not pub["serving_guinness"]:
            not_serving_icon = folium.Icon(
                prefix="fa", icon="exclamation", color="red"
            )
            marker = folium.Marker(
                [pub["lat"], pub["lon"]],
                popup=pub["name"] + " - not serving Guinness",
                icon=not_serving_icon
            )

        elif pd.notnull(pub["price"]):
            price_icon = folium.Icon(
                prefix="fa",  icon="beer", color="green"
            )
            marker = folium.Marker(
                [pub["lat"], pub["lon"]],
                popup=f"{pub['name']} - €{pub['price']}",
                icon=price_icon
            )

        else:
            no_price_icon = folium.Icon(
                prefix="fa", icon="question", color="lightgray"
            )
            marker = folium.Marker(
                [pub["lat"], pub["lon"]],
                popup=pub['name'] + " - No data submitted",
                icon=no_price_icon,
            )

        # Add marker to cluster
        marker.add_to(cluster)

    # Save map.
    tst.save("new_guindex_map.html")


if __name__ == "__main__":
    create_map()
