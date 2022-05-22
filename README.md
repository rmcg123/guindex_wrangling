# guindex_wrangling
A repository for working with data related to the guindex project.

The scripts `osm_query.py` has functions to query the openstreetmaps 
overpass API.

These functions are called in the script `combine_osm_pubs.py`.
Which gets and combines all the OSM data we are interested in.

The script `guindex_query.py` retrieves all the guindex pubs data.

The file `counties.csv` contains shape information of Irish counties.
