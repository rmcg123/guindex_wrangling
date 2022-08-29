# guindex_wrangling
A repository for working with data related to the guindex project.

The script `osm_query.py` has functions to query the openstreetmaps
overpass API.

These functions are called in the script `combine_osm_pubs.py`.
Which gets and combines all the OSM data we are interested in.

The script `guindex_query.py` retrieves all the guindex pubs data.

The script `duplicate_check.py` contains functions to check datasets for
duplicates within itself. Some of these functions are also re-used to check
the two data sets against each other.

The script `categorise_pubs_by_county.py` uses county polygons to sort the pubs with missing counties. 

Geographic information of county boundaries can be obtained at: https://www.townlands.ie/page/download/ . 

The final script `cross_check.py` checks the OSM data against the Guindex
data identifying pubs that need to be added to the Guindex.