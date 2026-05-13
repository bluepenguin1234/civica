"""
Fetch Census ACS 5-year data for all MA county subdivisions (towns).
Pulls 2023 and 2013 ACS to compute 10-year changes.
Output: data/bulk/census_acs_ma_towns.csv
"""

import urllib.request, json, csv
from pathlib import Path

OUT = Path(__file__).parent.parent / "data" / "bulk" / "census_acs_ma_towns.csv"

BASE = "https://api.census.gov/data/{year}/acs/acs5"
KEY  = "f464d89b2c5f394540fff2627add67036b80287e"
GEO  = f"&for=county+subdivision:*&in=state:25&key={KEY}"

VARS_2023 = [
    "NAME",
    "B15003_001E",  # pop 25+ (education denominator)
    "B15003_022E",  # bachelor's
    "B15003_023E",  # master's
    "B15003_024E",  # professional
    "B15003_025E",  # doctorate
    "B19013_001E",  # median HH income
    "B17001_001E",  # poverty universe
    "B17001_002E",  # below poverty
    "B23025_003E",  # civilian labor force
    "B23025_005E",  # unemployed
    "B01003_001E",  # total population
]

VARS_2013 = ["NAME", "B19013_001E", "B01003_001E"]

def fetch(year, variables):
    url = f"{BASE.format(year=year)}?get={','.join(variables)}{GEO}"
    print(f"  Fetching {year} ACS... {url[:80]}...")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        headers = data[0]
        rows = data[1:]
        print(f"  Got {len(rows)} rows")
        return headers, rows
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, []

def clean_name(name):
    # "Danvers town, Essex County, Massachusetts" -> "Danvers"
    return name.split(" town,")[0].split(" city,")[0].split(" Town,")[0].split(" City,")[0].strip()

def safe_float(val, default=None):
    try:
        v = float(val)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default

print("Fetching Census ACS data for all MA towns...")

# 2023 ACS
h23, rows23 = fetch(2023, VARS_2023)
# 2013 ACS
h13, rows13 = fetch(2013, VARS_2013)

if not rows23:
    print("Failed to fetch 2023 data — check network/API key")
    exit(1)

# Index 2013 by geo ID
geo13 = {}
if rows13:
    idx_name13 = h13.index("NAME")
    idx_inc13  = h13.index("B19013_001E")
    idx_pop13  = h13.index("B01003_001E")
    idx_state13 = h13.index("state")
    idx_sub13  = h13.index("county subdivision")
    for r in rows13:
        key = (r[idx_state13], r[idx_sub13])
        geo13[key] = {
            "income_2013": safe_float(r[idx_inc13]),
            "pop_2013":    safe_float(r[idx_pop13]),
        }

# Build 2023 index
idx = {v: i for i, v in enumerate(h23)}

results = []
for r in rows23:
    name_raw = r[idx["NAME"]]
    # Only keep actual town/city subdivisions (skip county-level aggregates)
    if "County" not in name_raw and "Massachusetts" not in name_raw:
        continue
    if "County subdivision" in name_raw:
        continue

    town = clean_name(name_raw).removesuffix(" Town").removesuffix(" town")

    pop25     = safe_float(r[idx["B15003_001E"]]) or 1
    bach      = (safe_float(r[idx["B15003_022E"]]) or 0)
    masters   = (safe_float(r[idx["B15003_023E"]]) or 0)
    prof      = (safe_float(r[idx["B15003_024E"]]) or 0)
    doc       = (safe_float(r[idx["B15003_025E"]]) or 0)
    bach_pct  = round((bach + masters + prof + doc) / pop25 * 100, 1) if pop25 else None

    pov_uni   = safe_float(r[idx["B17001_001E"]]) or 1
    pov_pop   = safe_float(r[idx["B17001_002E"]]) or 0
    pov_pct   = round(pov_pop / pov_uni * 100, 1) if pov_uni else None

    clf       = safe_float(r[idx["B23025_003E"]]) or 1
    unemp     = safe_float(r[idx["B23025_005E"]]) or 0
    unemp_pct = round(unemp / clf * 100, 1) if clf else None

    inc_2023  = safe_float(r[idx["B19013_001E"]])
    pop_2023  = safe_float(r[idx["B01003_001E"]])

    state_fips = r[idx["state"]]
    subdiv_fips = r[idx["county subdivision"]]
    g13 = geo13.get((state_fips, subdiv_fips), {})
    inc_2013 = g13.get("income_2013")
    pop_2013 = g13.get("pop_2013")

    inc_chg = None
    if inc_2023 and inc_2013 and inc_2013 > 0:
        inc_chg = round((inc_2023 - inc_2013) / inc_2013 * 100, 1)

    pop_chg = None
    if pop_2023 and pop_2013 and pop_2013 > 0:
        pop_chg = round((pop_2023 - pop_2013) / pop_2013 * 100, 1)

    results.append({
        "town_name":              town,
        "bachelors_degree_pct":   bach_pct,
        "poverty_pct":            pov_pct,
        "unemployment_pct":       unemp_pct,
        "median_household_income":inc_2023,
        "income_10yr_change_pct": inc_chg,
        "population":             pop_2023,
        "population_10yr_change_pct": pop_chg,
    })

results.sort(key=lambda x: x["town_name"])

fields = ["town_name","bachelors_degree_pct","poverty_pct","unemployment_pct",
          "median_household_income","income_10yr_change_pct","population","population_10yr_change_pct"]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(results)

print(f"\nSaved {len(results)} towns to {OUT}")
print("\nSample rows:")
for row in results[:5]:
    print(f"  {row['town_name']:<20} bach={row['bachelors_degree_pct']}%  pov={row['poverty_pct']}%  unemp={row['unemployment_pct']}%  inc_chg={row['income_10yr_change_pct']}%")
