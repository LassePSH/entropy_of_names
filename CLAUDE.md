# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

`fetch_names.py` queries the Danmarks Statistik "NavneBarometer" API to retrieve Danish newborn name counts by year (1985–2024) and writes results as CSV.

## Running the script

```bash
# Look up one or more names directly
python fetch_names.py Emma Lars Nora

# Look up names from a file (one name per line)
python fetch_names.py --file danish_female_names.txt --output results.csv
```

## Data format

Output CSV columns: `name`, `gender`, then one column per year (1985–2024).

- `gender` is `K` (kvinde = female) or `M` (male), taken directly from API response keys like `"EMMA (K)"`.
- A name may appear twice (once per gender) if the API returns data for both.
- Year range is inferred dynamically from the length of the first successful API response.

## API

`POST https://www.dst.dk/da/DstDk-Global/Udvikler/HostNavneBarometer?ajax=1` with form body `name=<name>`. Returns JSON mapping `"NAME (K)"` / `"NAME (M)"` to arrays of integer counts ordered from `START_YEAR` (1985) forward.

## Dependencies

Only `requests` is required beyond the stdlib. Install with:

```bash
pip install requests
```
