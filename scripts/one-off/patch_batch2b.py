import csv, sys
sys.stdout.reconfigure(encoding="utf-8")

patches = {
    "Ayer": {
        "crime_5yr_pct_change": "32",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Norfolk": {
        "bond_rating_sp": "AA+",
        "crime_5yr_pct_change": "210",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Bellingham": {
        "bond_rating_sp": "AA",
        "crime_5yr_pct_change": "30",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Harvard": {
        "crime_5yr_pct_change": "-43",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Bolton": {
        "crime_5yr_pct_change": "123",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Pepperell": {
        "crime_5yr_pct_change": "-37",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Spencer": {
        "crime_5yr_pct_change": "-54",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Oxford": {
        "crime_5yr_pct_change": "-26",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Charlton": {
        "crime_5yr_pct_change": "18",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
    },
    "Mendon": {
        "crime_5yr_pct_change": "69",
        "electric_savings_vs_state_avg": "0",
        "water_violations_5yr": "0",
        "wildfire_risk": "Low",
        "transparency": "yes",
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
