#!/usr/bin/env python3
"""
Fetch Danish newborn name counts from Danmarks Statistik (1985-2024).

Usage:
    python fetch_names.py Emma Lars Nora
    python fetch_names.py --file names.txt
    python fetch_names.py Emma --output results.csv
"""

import argparse
import csv
import sys
import time
import requests

API_URL = "https://www.dst.dk/da/DstDk-Global/Udvikler/HostNavneBarometer?ajax=1"
START_YEAR = 1985


def fetch_name(session: requests.Session, name: str) -> dict[str, list[int]]:
    """Query the API for a name. Returns {gender: [counts...]} or {} on failure."""
    response = session.post(API_URL, data={"name": name}, timeout=10)
    response.raise_for_status()
    data = response.json()
    # Keys look like "EMMA (K)" or "LARS (M)" — extract gender suffix
    result = {}
    for key, counts in data.items():
        # key format: "NAME (K)" or "NAME (M)"
        gender = key.split("(")[-1].rstrip(")")
        result[gender] = counts
    return result


def main():
    parser = argparse.ArgumentParser(description="Download Danish newborn name counts to CSV.")
    parser.add_argument("names", nargs="*", help="Names to look up")
    parser.add_argument("--file", help="Text file with one name per line")
    parser.add_argument("--output", "-o", help="Output CSV file (default: stdout)")
    args = parser.parse_args()

    names = list(args.names)
    if args.file:
        with open(args.file) as f:
            names += [line.strip() for line in f if line.strip()]
    if not names:
        parser.print_help()
        sys.exit(1)

    # Determine year range from the first successful response
    years = None
    rows = []

    with requests.Session() as session:
        for name in names:
            print(f"Fetching: {name}", file=sys.stderr)
            try:
                data = fetch_name(session, name)
            except Exception as e:
                print(f"  ERROR: {e}", file=sys.stderr)
                continue

            if not data:
                print(f"  No data found for '{name}'", file=sys.stderr)
                continue

            for gender, counts in data.items():
                if years is None:
                    end_year = START_YEAR + len(counts) - 1
                    years = list(range(START_YEAR, end_year + 1))
                rows.append({"name": name.capitalize(), "gender": gender, "counts": counts})

            time.sleep(0.2)  # be polite

    if not rows:
        print("No data retrieved.", file=sys.stderr)
        sys.exit(1)

    out = open(args.output, "w", newline="", encoding="utf-8") if args.output else sys.stdout
    try:
        writer = csv.writer(out)
        writer.writerow(["name", "gender"] + years)
        for row in rows:
            writer.writerow([row["name"], row["gender"]] + row["counts"])
    finally:
        if args.output:
            out.close()
            print(f"Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
