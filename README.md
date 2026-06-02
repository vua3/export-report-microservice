# Export Report Microservice

This microservice generates a formatted `.txt` report from any two-section log (visited + wishlist). 
Built with [Python 3](https://www.python.org/) and [Flask](https://flask.palletsprojects.com/).

---

## Description

This microservice exposes a single endpoint `POST /export` that accepts a JSON body containing your log data and returns a `.txt` report as a downloadable file.

---

## Setup & Prerequisites

**Requirements:**
- [Python 3.8+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)

**Install dependencies:**

```bash
pip install flask flask-cors requests
```

**Run the microservice** (keep this running in a separate terminal):

```bash
python export_service.py
```

The service starts on `http://localhost:5002`. You should see:

```
 * Running on http://127.0.0.1:5002
```

> Main program and the microservice must run in separate terminals at the same time.

---

## How to Request Data

**Endpoint:** `POST http://localhost:5002/export`

**Headers required:**
```
Content-Type: application/json
```

### Request Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `visited` | array of objects | Yes | — | Items the user has visited/completed |
| `wishlist` | array of objects | Yes | — | Items the user wants to visit/do |
| `title` | string | No | `"My Log"` | Title printed at the top of the report |
| `visited_label` | string | No | `"Visited"` | Section heading for the visited list |
| `wishlist_label` | string | No | `"Wishlist"` | Section heading for the wishlist |

> `visited` and `wishlist` can be empty arrays `[]` but both must be present. If both are empty, the service returns a `no_data` error.

---

### Example Calls

**Python (`requests` library):**

```python
import requests

payload = {
    "title":          "My Museum Log",
    "visited_label":  "Places I've Been",
    "wishlist_label": "On My List",
    "visited": [
        {
            "name":         "The Getty Center",
            "location":     "Los Angeles, California",
            "museum_type":  "Art",
            "ticket_cost":  "Free (parking $20)",
            "notes":        "Beautiful at sunset!"
        }
    ],
    "wishlist": [
        {
            "name":        "The Louvre",
            "location":    "Paris, France",
            "ticket_cost": "€22"
        }
    ]
}

response = requests.post(
    "http://localhost:5002/export",
    json=payload,
    timeout=10
)

if response.status_code == 200:
    with open("my_report.txt", "wb") as f:
        f.write(response.content)
    print("Report saved!")
else:
    print(response.json())
```

---

## How to Receive Data

### Success — `200 OK`

The response body is a plain `.txt` file delivered as a download attachment. Save `response.content` (bytes) directly to a file.

**Example report output:**

```
============================================================
  MY MUSEUM LOG
  Generated: June 01, 2026 at 02:45 PM
============================================================

PLACES I'VE BEEN
------------------------------------------------------------
  [1] The Getty Center
      Location        : Los Angeles, California
      Museum Type     : Art
      Ticket Cost     : Free (parking $20)
      Notes           : Beautiful at sunset!

ON MY LIST
------------------------------------------------------------
  [1] The Louvre
      Location        : Paris, France
      Ticket Cost     : €22

SUMMARY
------------------------------------------------------------
  Total logged      : 2
  Places I've Been  : 1
  On My List        : 1

============================================================
  End of Report
============================================================
```

The download filename is automatically set to `{title}_report.txt` (e.g. `my_museum_log_report.txt`).

---

### Example Responses

**No data — `404`**

Returned when both `visited` and `wishlist` are empty arrays.

```json
{
  "error": "no_data"
}
```

**Bad request — `400`**

Returned when the request body is missing, not valid JSON, or `visited`/`wishlist` are not arrays.

```json
{
  "error": "bad_request",
  "message": "Request body must be valid JSON with Content-Type: application/json"
}
```

```json
{
  "error": "bad_request",
  "message": "'visited' and 'wishlist' must be arrays"
}
```

**Server error — `500`**

Returned if the report fails to build or the temp file cannot be written. 

```json
{
  "error": "server_error",
  "message": "Could not write report file."
}
```

---

## Writing a Connector File

This is a small helper file that lives in you main program's folder. It is responsible for:

1. Loading your app's data
2. Shaping it into the agreed request body
3. POSTing it to the microservice
4. Saving the returned `.txt` file and reporting success or failure to your app

You write the connector. This is the only file that needs to know anything about a program's data structure.

