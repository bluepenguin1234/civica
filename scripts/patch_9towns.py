import csv, sys
sys.stdout.reconfigure(encoding="utf-8")

patches = {
    "Dover": {
        "bond_rating_sp": "AAA",
        "pension_funded_ratio_pct": "71.8",
        "effective_tax_rate_pct": "1.13",
        "residential_rate_per_1000": "11.27",
        "median_annual_tax_bill": "15529",
        "violent_crime_per_100k": "151",
        "property_crime_per_100k": "504",
        "flood_risk_pct": "8",
        "flood_2050_growth_pts": "1",
    },
    "Sherborn": {
        "bond_rating_sp": "AAA",
        "pension_funded_ratio_pct": "54.54",
        "effective_tax_rate_pct": "1.66",
        "residential_rate_per_1000": "16.58",
        "median_annual_tax_bill": "17678",
        "violent_crime_per_100k": "22",
        "property_crime_per_100k": "178",
    },
    "Carlisle": {
        "pension_funded_ratio_pct": "54.54",
        "effective_tax_rate_pct": "1.32",
        "residential_rate_per_1000": "13.18",
        "median_annual_tax_bill": "15411",
        "violent_crime_per_100k": "28.4",
        "property_crime_per_100k": "15.2",
        "test_scores_math_pct": "76.0",
    },
    "Stow": {
        "bond_rating_sp": "AAA",
        "pension_funded_ratio_pct": "54.54",
        "effective_tax_rate_pct": "1.74",
        "residential_rate_per_1000": "17.42",
        "median_annual_tax_bill": "11884",
        "violent_crime_per_100k": "55",
        "property_crime_per_100k": "259",
    },
    "Groton": {
        "bond_rating_sp": "AAA",
        "pension_funded_ratio_pct": "54.54",
        "effective_tax_rate_pct": "1.53",
        "residential_rate_per_1000": "15.25",
        "median_annual_tax_bill": "10027",
        "violent_crime_per_100k": "43",
        "property_crime_per_100k": "199",
    },
    "Plainville": {
        "pension_funded_ratio_pct": "63.5",
        "residential_rate_per_1000": "11.56",
        "median_annual_tax_bill": "6797",
        "violent_crime_per_100k": "26.8",
        "property_crime_per_100k": "175.8",
    },
    "East Longmeadow": {
        "pension_funded_ratio_pct": "54.73",
        "effective_tax_rate_pct": "1.85",
        "residential_rate_per_1000": "18.48",
        "median_annual_tax_bill": "6465",
        "violent_crime_per_100k": "122.7",
        "property_crime_per_100k": "102.6",
        "flood_risk_pct": "17",
    },
    "Ludlow": {
        "pension_funded_ratio_pct": "58.32",
        "effective_tax_rate_pct": "1.74",
        "residential_rate_per_1000": "17.35",
        "median_annual_tax_bill": "5177",
        "violent_crime_per_100k": "93.9",
        "property_crime_per_100k": "49.3",
    },
    "Webster": {
        "effective_tax_rate_pct": "1.19",
        "residential_rate_per_1000": "11.88",
        "median_annual_tax_bill": "4232",
        "violent_crime_per_100k": "638",
        "property_crime_per_100k": "800",
    },
}

rows = list(csv.DictReader(open("data/towns.csv", encoding="utf-8")))
fieldnames = list(rows[0].keys())
updated = 0
for row in rows:
    town = row["town_name"]
    if town in patches:
        for k, v in patches[town].items():
            row[k] = v
        row["last_updated"] = "2026-05-14"
        updated += 1
        print(f"  Patched: {town}")

with open("data/towns.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
print(f"\nPatched {updated} of {len(rows)} towns")
