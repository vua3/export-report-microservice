"""
export_service.py - Export Report Microservice
"""

import os
import tempfile
from datetime import datetime

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

PORT = 5002


# Build layout of report as a plain-text string
def build_report(title: str, visited: list, wishlist: list,
                 visited_label: str = "Visited",
                 wishlist_label: str = "Wishlist") -> str:
    """
    Parameters:
    title          : report title string  ("My Museum Log")
    visited        : list of dicts, each representing a visited item
    wishlist       : list of dicts, each representing a wishlist item
    visited_label  : section heading for visited items  ("Places I've Been")
    wishlist_label : section heading for wishlist items ("Bucket List")
    """
    
    # format the current date/time for report header
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    lines = []

    # set report header & timestamp
    lines += [
        "=" * 60,
        f"  {title.upper()}",
        f"  Generated: {now}",
        "=" * 60,
        "",
    ]

    # visited section (or other label if you're not tracking museums)
    lines += [
        visited_label.upper(),
        "-" * 60,
    ]

    if visited:
        for i, item in enumerate(visited, start=1):
            # print "name" of object (eg The Getty Museum) if present, then every other field 
            name = item.get("name", f"Item {i}")
            lines.append(f"  [{i}] {name}")
            for key, value in item.items():
                if key == "name":
                    continue                     # already printed above
                if str(value).strip():           # skip blank values
                    label = key.replace("_", " ").title()
                    lines.append(f"      {label:<16}: {value}")
            lines.append("")
    else:
        lines += ["  (none)", ""]

    # wishlist section (or other label if you're not tracking museums)
    lines += [
        wishlist_label.upper(),
        "-" * 60,
    ]

    if wishlist:
        for i, item in enumerate(wishlist, start=1):
            name = item.get("name", f"Item {i}")
            lines.append(f"  [{i}] {name}")
            for key, value in item.items():
                if key == "name":
                    continue
                if str(value).strip():
                    label = key.replace("_", " ").title()
                    lines.append(f"      {label:<16}: {value}")
            lines.append("")
    else:
        lines += ["  (none)", ""]

    # Summary section with counts
    total = len(visited) + len(wishlist)
    lines += [
        "SUMMARY",
        "-" * 60,
        f"  Total logged      : {total}",
        f"  {visited_label:<18}: {len(visited)}",
        f"  {wishlist_label:<18}: {len(wishlist)}",
        "",
        "=" * 60,
        "  End of Report",
        "=" * 60,
    ]

    return "\n".join(lines)


# export endpoint

@app.route("/export", methods=["POST"])
def export_report():
    """
    Accepts a JSON body, builds a report, and returns it as a .txt download.
    """

    # Step 1: parse the request body ──────────────────────────────────────────
    body = request.get_json(silent=True)   # silent=True → returns None on bad JSON
    if body is None:
        return jsonify({
            "error": "bad_request",
            "message": "Request body must be valid JSON"
        }), 400

    title          = body.get("title", "My Log")
    visited_label  = body.get("visited_label", "Visited")
    wishlist_label = body.get("wishlist_label", "Wishlist")
    visited        = body.get("visited", [])
    wishlist       = body.get("wishlist", [])

    # Validate that visited and wishlist are actually lists
    if not isinstance(visited, list) or not isinstance(wishlist, list):
        return jsonify({
            "error": "bad_request",
            "message": "sections must be lists"
        }), 400

    # Step 2: check for empty data ────────────────────────────────────────────
    if not visited and not wishlist:
        return jsonify({"error": "no_data"}), 404

    # Step 3: build the report ────────────────────────────────────────────────
    try:
        report_text = build_report(title, visited, wishlist, visited_label, wishlist_label)
    except Exception as e:
        return jsonify({
            "error": "server_error",
            "message": f"Failed to build report: {e}"
        }), 500

    # Step 4: write to a temp file and send ───────────────────────────────────
    try:
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8"
        )
        tmp.write(report_text)
        tmp.close()
    except OSError as e:
        return jsonify({
            "error": "server_error",
            "message": f"Could not write report file: {e}"
        }), 500

    # Step 5: send the file as an attachment ──────────────────────────────────
    safe_title = title.lower().replace(" ", "_")
    download_name = f"{safe_title}_report.txt"

    return send_file(
        tmp.name,
        mimetype="text/plain",
        as_attachment=True,
        download_name=download_name,
    )


# Default route
@app.route("/")
def home():
    return (
        "Export Microservice running on port 5002"
    )


if __name__ == "__main__":
    app.run(port=5002, debug=True)
