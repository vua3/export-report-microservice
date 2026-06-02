"""
export_connector.py
helper program to connect to export microservice (export_service.py)
"""

import requests
import data 

BASE_URL = "http://localhost:5002"


def request_export() -> bool:
    """
    Load museums from local data, POST them to the export microservice,
    and save the returned .txt file to disk.
    Returns True on success, False on any failure.
    """

    # load data 
    museums = data.load_museums()

    visited  = [m.to_dict() for m in museums if m.status == "visited"]
    wishlist = [m.to_dict() for m in museums if m.status == "wishlist"]

    # build the request body 
    payload = {
        "title":          "My Museum Log",
        "visited_label":  "Places I've Been",
        "wishlist_label": "On My List",
        "visited":        visited,
        "wishlist":       wishlist,
    }

    # POST to microservice 
    try:
        response = requests.post(
            f"{BASE_URL}/export",
            json=payload,
            timeout=10,
        )
    except requests.ConnectionError:
        print("  [Export] Error: Export microservice is not running.")
        return False

    # handle responses
    if response.status_code == 200:
        # returned the .txt file - save it locally
        with open("museum_report.txt", "wb") as f:
            f.write(response.content)
        print("  [Export] Report saved to museum_report.txt")
        return True

    elif response.status_code == 404:
        error = response.json().get("error", "")
        if error == "no_data":
            print("  [Export] Nothing to export — your log is empty.")
        return False

    else:
        error_body = response.json()
        print(f"  [Export] Server error: {error_body.get('message', 'unknown')}")
        return False

