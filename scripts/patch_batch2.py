import csv, sys
sys.stdout.reconfigure(encoding="utf-8")

patches = {
    "Ayer": {
        "pension_funded_ratio_pct": "54.54",
        "effective_tax_rate_pct": "1.20",
        "residential_rate_per_1000": "11.96",
        "median_annual_tax_bill": "5396",
        "violent_crime_per_100k": "171.8",
        "property_crime_per_100k": "36.1",
    },
    "Norfolk": {
        "pension_funded_ratio_pct": "74.6",
        "effective_tax_rate_pct": "1.60",
        "residential_rate_per_1000": "15.97",
        "median_annual_tax_bill": "10254",
        "violent_crime_per_100k": "25.4",
        "property_crime_per_100k": "45.2",
    },
    "Bellingham": {
        "pension_funded_ratio_pct": "74.6",
        "effective_tax_rate_pct": "1.26",
        "residential_rate_per_1000": "12.56",
        "median_annual_tax_bill": "5196",
        "violent_crime_per_100k": "129.8",
        "property_crime_per_100k": "68.2",
    },
    "Harvard": {
        "pension_funded_ratio_pct": "51.9",
        "effective_tax_rate_pct": "1.57",
        "residential_rate_per_1000": "15.65",
        "median_annual_tax_bill": "12208",
        "violent_crime_per_100k": "42.3",
        "property_crime_per_100k": "9.9",
    },
    "Bolton": {
        "pension_funded_ratio_pct": "51.9",
        "effective_tax_rate_pct": "1.66",
        "residential_rate_per_1000": "16.62",
        "median_annual_tax_bill": "12636",
        "violent_crime_per_100k": "93.7",
        "property_crime_per_100k": "29.8",
    },
    "Pepperell": {
        "pension_funded_ratio_pct": "54.54",
        "effective_tax_rate_pct": "1.46",
        "residential_rate_per_1000": "14.63",
        "median_annual_tax_bill": "6989",
        "violent_crime_per_100k": "58.5",
        "property_crime_per_100k": "34.7",
    },
    "Spencer": {
        "pension_funded_ratio_pct": "51.9",
        "effective_tax_rate_pct": "1.17",
        "residential_rate_per_1000": "11.74",
        "median_annual_tax_bill": "4197",
        "violent_crime_per_100k": "41.2",
        "property_crime_per_100k": "25.1",
    },
    "Oxford": {
        "pension_funded_ratio_pct": "51.9",
        "effective_tax_rate_pct": "1.27",
        "residential_rate_per_1000": "12.67",
        "median_annual_tax_bill": "4718",
        "violent_crime_per_100k": "140.2",
        "property_crime_per_100k": "58.3",
    },
    "Charlton": {
        "pension_funded_ratio_pct": "51.9",
        "effective_tax_rate_pct": "1.11",
        "residential_rate_per_1000": "11.13",
        "median_annual_tax_bill": "4895",
        "violent_crime_per_100k": "65.8",
        "property_crime_per_100k": "31.5",
    },
    "Mendon": {
        "pension_funded_ratio_pct": "51.9",
        "effective_tax_rate_pct": "1.34",
        "residential_rate_per_1000": "13.39",
        "median_annual_tax_bill": "8228",
        "violent_crime_per_100k": "61.7",
        "property_crime_per_100k": "33.1",
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
