import json

import requests
import pandas as pd
from secrets import myemail, mypassword


def post_pub(details):
    """Sends a post request to the Guindex. Takes a dictionary of pub
    details."""

    # Obtain authentication.
    auth_url = "https://www.guindex.ie/api/rest-auth/login/"

    auth_rqst = requests.post(
        auth_url, data={"email": myemail, "password": mypassword}
    )
    if auth_rqst.status_code != 200:

        print("Authentication failed. Check your details.")

    else:
        # Extract token.
        token = auth_rqst.json()["key"]

        # Pub posting url
        url = "https://www.guindex.ie/api/pubs/"

        # Headers for post request.
        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Token " + token,
        }

        # Extract details of pub from dictionary.
        pub_details = {
            "name": details["name"],
            "latitude": str(details["lat"]),
            "longitude": str(details["lon"]),
            "county": details["county"],
            "closed": details["closed"],
        }

        pub_details = json.dumps(pub_details)

        pub_post = requests.post(
            url, data=pub_details, headers=headers
        )

        if pub_post.status_code == 201:
            print(
                "Posted ",
                details["name"],
                "from county",
                details["county"],
                "to Guindex.",
            )


def main():
    """Main function."""

    # Reads in new OSM pubs.
    pubs = pd.read_csv("new_pubs.csv")

    # Loops through rows of pubs posting each new OSM pub to Guindex.
    for pub in pubs.index:
        details = pubs.iloc[pub, :].to_dict()
        post_pub(details=details)


if __name__ == "__main__":
    main()
